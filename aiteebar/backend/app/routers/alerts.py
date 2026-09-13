"""
SOC Alert API endpoints
Alert generation, triage, delivery, and SIEM export.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Alert,
    AlertStatus,
    AIAgent,
    AIApplication,
    EventSeverity,
)
from app.schemas.alert import (
    AlertAcknowledge,
    AlertCreate,
    AlertDeliveryResponse,
    AlertResponse,
    SiemExportResponse,
)
from app.security import get_current_user
from app.services.alerting import AlertGenerator, AlertNotifier

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate an alert directly.

    Used when a caller has already determined an alert is warranted, rather
    than letting the severity threshold decide from a logged event.
    """
    agent = (
        db.query(AIAgent).filter(AIAgent.id == alert_data.agent_id).first()
        if alert_data.agent_id
        else None
    )
    if alert_data.agent_id and not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {alert_data.agent_id} not found",
        )

    application = (
        db.query(AIApplication).filter(AIApplication.id == alert_data.application_id).first()
        if alert_data.application_id
        else (agent.application if agent else None)
    )
    if alert_data.application_id and not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {alert_data.application_id} not found",
        )

    alert = Alert(
        timestamp=datetime.utcnow(),
        severity=alert_data.severity,
        title=alert_data.title,
        description=alert_data.description,
        agent_id=alert_data.agent_id,
        application_id=application.id if application else None,
        agent_snapshot=AlertGenerator._snapshot_agent(agent),
        application_snapshot=AlertGenerator._snapshot_application(application),
        data_type=alert_data.data_type,
        destination=alert_data.destination,
        risk_score=alert_data.risk_score,
        action_taken=alert_data.action_taken,
        source=alert_data.source,
        event_ids=alert_data.event_ids,
        status=AlertStatus.OPEN,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    AlertNotifier.dispatch(alert, AlertGenerator.to_siem_dict(alert), db)

    return alert


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    severity: Optional[EventSeverity] = Query(None, description="Filter by severity"),
    alert_status: Optional[AlertStatus] = Query(None, alias="status"),
    agent_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List alerts, newest first. Filter with e.g. `?severity=CRITICAL`."""
    query = db.query(Alert).filter(
        Alert.timestamp >= datetime.utcnow() - timedelta(days=days)
    )

    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_status:
        query = query.filter(Alert.status == alert_status)
    if agent_id:
        query = query.filter(Alert.agent_id == agent_id)

    return query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()


# Declared before /{alert_id} so the literal path is not captured as an ID.
@router.get("/export", response_model=SiemExportResponse)
async def export_alerts_for_siem(
    severity: Optional[EventSeverity] = Query(None),
    alert_status: Optional[AlertStatus] = Query(None, alias="status"),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """
    Export alerts as SIEM-compatible JSON.

    Returns the same payload shape that is pushed to webhook collectors, so a
    SIEM can be backfilled from here and receive live alerts on the same schema.
    """
    query = db.query(Alert).filter(
        Alert.timestamp >= datetime.utcnow() - timedelta(days=days)
    )

    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_status:
        query = query.filter(Alert.status == alert_status)

    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()

    return SiemExportResponse(
        exported_at=datetime.utcnow(),
        count=len(alerts),
        alerts=[AlertGenerator.to_siem_dict(alert) for alert in alerts],
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Fetch a single alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return alert


@router.get("/{alert_id}/siem")
async def get_alert_siem_payload(alert_id: str, db: Session = Depends(get_db)):
    """Fetch a single alert in SIEM-compatible form."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return AlertGenerator.to_siem_dict(alert)


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: str,
    body: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Acknowledge, resolve, or mark an alert as a false positive."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.status = body.status
    alert.updated_at = datetime.utcnow()

    if body.status != AlertStatus.OPEN:
        alert.acknowledged_by = current_user.get("sub")
        alert.acknowledged_at = datetime.utcnow()
    else:
        alert.acknowledged_by = None
        alert.acknowledged_at = None

    db.commit()
    db.refresh(alert)

    return alert


@router.post("/{alert_id}/deliver", response_model=AlertDeliveryResponse)
async def deliver_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Re-send an alert over the enabled delivery channels.

    Useful after a webhook outage, or once a channel is configured that was
    disabled when the alert was first generated.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    results = AlertNotifier.dispatch(alert, AlertGenerator.to_siem_dict(alert), db)

    return AlertDeliveryResponse(alert_id=alert.id, results=results)
