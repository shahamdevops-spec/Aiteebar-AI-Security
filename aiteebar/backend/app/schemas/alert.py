"""
Pydantic schemas for SOC alerting.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models import (
    ActionTaken,
    AlertDeliveryStatus,
    AlertStatus,
    DetectionMethod,
    EventSeverity,
)


class AlertCreate(BaseModel):
    """Generate an alert directly, rather than via an event."""
    severity: EventSeverity = Field(..., description="Alert severity")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)

    agent_id: Optional[str] = None
    application_id: Optional[str] = None

    data_type: Optional[str] = None
    destination: Optional[str] = None
    risk_score: float = Field(0, ge=0, le=100)
    action_taken: ActionTaken = Field(ActionTaken.ALLOWED)

    source: DetectionMethod = Field(
        DetectionMethod.MANUAL, description="Subsystem that raised the alert"
    )
    event_ids: List[str] = Field(default_factory=list, description="Correlated security event IDs")


class AlertResponse(BaseModel):
    """An alert as stored by the platform."""
    id: str
    timestamp: datetime
    severity: EventSeverity
    title: str
    description: str

    agent_id: Optional[str]
    application_id: Optional[str]
    agent_snapshot: Dict[str, Any]
    application_snapshot: Dict[str, Any]

    data_type: Optional[str]
    destination: Optional[str]
    risk_score: float
    action_taken: ActionTaken

    source: DetectionMethod
    event_ids: List[str]

    status: AlertStatus
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]

    delivery_status: AlertDeliveryStatus
    delivery_error: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class SiemAlert(BaseModel):
    """
    The canonical SIEM-compatible alert payload.
    This is the shape delivered to webhooks and returned by the export endpoint.
    """
    alert_id: str
    timestamp: Optional[str]
    severity: str
    title: str
    description: str
    agent: Dict[str, Any]
    application: Dict[str, Any]
    data_type: Optional[str]
    destination: Optional[str]
    risk_score: float
    action_taken: str
    source: str
    events: List[str]


class SiemExportResponse(BaseModel):
    """Batch of alerts formatted for SIEM ingestion."""
    exported_at: datetime
    count: int
    alerts: List[SiemAlert]


class AlertAcknowledge(BaseModel):
    """Acknowledge or close an alert."""
    status: AlertStatus = Field(..., description="New triage state")


class AlertDeliveryResponse(BaseModel):
    """Outcome of an alert delivery attempt, per channel."""
    alert_id: str
    results: Dict[str, str]
