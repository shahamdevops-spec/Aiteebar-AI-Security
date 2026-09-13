"""
Security Event API endpoints
Internal event logging. Events at or above the configured severity threshold
automatically generate a SOC alert.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AIAgent,
    AIApplication,
    EventSeverity,
    SecurityEvent,
    SecurityEventType,
)
from app.schemas.event import (
    SecurityEventCreate,
    SecurityEventIngestResponse,
    SecurityEventResponse,
)
from app.security import get_current_user
from app.services.alerting import AlertGenerator, AlertNotifier

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=SecurityEventIngestResponse, status_code=status.HTTP_201_CREATED)
async def log_event(
    event_data: SecurityEventCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Log a security event.

    If the event severity meets the alert threshold (CRITICAL by default),
    a SIEM-compatible alert is generated and pushed to any enabled delivery
    channel in the same request.
    """
    if event_data.agent_id:
        agent_exists = db.query(AIAgent).filter(AIAgent.id == event_data.agent_id).first()
        if not agent_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {event_data.agent_id} not found",
            )

    if event_data.application_id:
        app_exists = db.query(AIApplication).filter(
            AIApplication.id == event_data.application_id
        ).first()
        if not app_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {event_data.application_id} not found",
            )

    event = SecurityEvent(
        event_type=event_data.event_type.value,
        severity=event_data.severity,
        agent_id=event_data.agent_id,
        application_id=event_data.application_id,
        tool_id=event_data.tool_id,
        data_type=event_data.data_type,
        source=event_data.source,
        destination=event_data.destination,
        detection_method=event_data.detection_method,
        risk_score=event_data.risk_score,
        action_taken=event_data.action_taken,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    alert = AlertGenerator.generate_from_event(event, db)

    if alert:
        payload = AlertGenerator.to_siem_dict(alert)
        AlertNotifier.dispatch(alert, payload, db)

    return SecurityEventIngestResponse(
        event=SecurityEventResponse.model_validate(event),
        alert_generated=alert is not None,
        alert_id=alert.id if alert else None,
    )


@router.get("", response_model=List[SecurityEventResponse])
async def list_events(
    event_type: Optional[SecurityEventType] = Query(None),
    severity: Optional[EventSeverity] = Query(None),
    agent_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365, description="Look back this many days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List logged security events, newest first."""
    query = db.query(SecurityEvent).filter(
        SecurityEvent.created_at >= datetime.utcnow() - timedelta(days=days)
    )

    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type.value)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if agent_id:
        query = query.filter(SecurityEvent.agent_id == agent_id)

    return (
        query.order_by(SecurityEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/types")
async def list_event_types():
    """List the event type vocabulary accepted by this API."""
    return {
        "event_types": [
            {"value": event_type.value, "name": event_type.name}
            for event_type in SecurityEventType
        ]
    }


@router.get("/{event_id}", response_model=SecurityEventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """Fetch a single security event."""
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event
