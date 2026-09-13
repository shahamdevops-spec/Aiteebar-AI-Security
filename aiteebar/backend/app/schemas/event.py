"""
Pydantic schemas for security event logging.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import (
    ActionTaken,
    DetectionMethod,
    EventSeverity,
    EventStatus,
    SecurityEventType,
)


class SecurityEventCreate(BaseModel):
    """Log a security event."""
    event_type: SecurityEventType = Field(..., description="Category of event being logged")
    severity: EventSeverity = Field(..., description="Event severity")

    agent_id: Optional[str] = Field(None, description="Agent that produced the event")
    application_id: Optional[str] = Field(None, description="Owning application")
    tool_id: Optional[str] = Field(None, description="Tool involved, if any")

    data_type: Optional[str] = Field(None, description="Sensitive data type involved, e.g. CNIC")
    source: Optional[str] = Field(None, description="Where the data or action originated")
    destination: Optional[str] = Field(None, description="Where the data or action was headed")

    detection_method: Optional[DetectionMethod] = Field(
        None, description="Subsystem that detected the event"
    )
    risk_score: float = Field(0, ge=0, le=100, description="Risk score 0-100")
    action_taken: ActionTaken = Field(
        ActionTaken.ALLOWED, description="Enforcement outcome"
    )


class SecurityEventResponse(BaseModel):
    """A logged security event."""
    id: str
    event_type: str
    severity: EventSeverity

    agent_id: Optional[str]
    application_id: Optional[str]
    tool_id: Optional[str]

    data_type: Optional[str]
    source: Optional[str]
    destination: Optional[str]

    detection_method: Optional[DetectionMethod]
    risk_score: float
    action_taken: ActionTaken
    status: EventStatus

    created_at: datetime

    class Config:
        from_attributes = True


class SecurityEventIngestResponse(BaseModel):
    """Result of logging an event, including any alert it triggered."""
    event: SecurityEventResponse
    alert_generated: bool = Field(..., description="Whether the event met the alert threshold")
    alert_id: Optional[str] = Field(None, description="ID of the generated alert, if any")
