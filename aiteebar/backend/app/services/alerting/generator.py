"""
SOC Alert Generation
Turns security events into structured, SIEM-compatible alerts.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    Alert,
    AlertStatus,
    ActionTaken,
    AIAgent,
    AIApplication,
    DetectionMethod,
    EventSeverity,
    SecurityEvent,
    SecurityEventType,
)

logger = logging.getLogger(__name__)


# Ordered low to high so threshold comparisons are a simple index lookup.
SEVERITY_ORDER = [
    EventSeverity.INFO,
    EventSeverity.LOW,
    EventSeverity.MEDIUM,
    EventSeverity.HIGH,
    EventSeverity.CRITICAL,
]

# Human-readable alert titles per event type. The data-exfiltration phrasing is
# reserved for the policy/threat paths where an external destination is involved.
TITLE_BY_EVENT_TYPE = {
    SecurityEventType.AGENT_TOOL_CONNECTION: "AI Agent Connected to Restricted Tool",
    SecurityEventType.DATA_ACCESS: "AI Agent Accessed Sensitive Data",
    SecurityEventType.DLP_DETECTION: "Sensitive Data Detected in Agent Output",
    SecurityEventType.RISK_THRESHOLD_EXCEEDED: "Agent Risk Threshold Exceeded",
    SecurityEventType.POLICY_VIOLATION: "Security Policy Violation",
    SecurityEventType.EXTERNAL_COMMUNICATION: "Agent Communication with External Destination",
    SecurityEventType.THREAT_DETECTED: "Threat Detected in Agent Activity",
    SecurityEventType.BLOCK_ACTION_TAKEN: "Agent Action Blocked by Enforcement",
}


class AlertGenerator:
    """Builds SOC alerts from security events."""

    @staticmethod
    def meets_threshold(severity: EventSeverity) -> bool:
        """Check whether a severity is at or above the auto-generation threshold."""
        try:
            threshold = EventSeverity(settings.alert_auto_generate_severity)
        except ValueError:
            logger.warning(
                "Invalid ALERT_AUTO_GENERATE_SEVERITY %r, falling back to CRITICAL",
                settings.alert_auto_generate_severity,
            )
            threshold = EventSeverity.CRITICAL

        return SEVERITY_ORDER.index(severity) >= SEVERITY_ORDER.index(threshold)

    @staticmethod
    def generate_from_event(
        event: SecurityEvent,
        db: Session,
        related_event_ids: Optional[List[str]] = None,
    ) -> Optional[Alert]:
        """
        Build an alert from a security event, if the event meets the severity
        threshold. Returns None when the event is below threshold.
        """
        if not AlertGenerator.meets_threshold(event.severity):
            return None

        agent = (
            db.query(AIAgent).filter(AIAgent.id == event.agent_id).first()
            if event.agent_id
            else None
        )
        application = AlertGenerator._resolve_application(event, agent, db)

        event_ids = [event.id]
        if related_event_ids:
            event_ids.extend(eid for eid in related_event_ids if eid != event.id)

        alert = Alert(
            timestamp=event.created_at or datetime.utcnow(),
            severity=event.severity,
            title=AlertGenerator._build_title(event),
            description=AlertGenerator._build_description(event, agent, application),
            agent_id=event.agent_id,
            application_id=application.id if application else event.application_id,
            agent_snapshot=AlertGenerator._snapshot_agent(agent),
            application_snapshot=AlertGenerator._snapshot_application(application),
            data_type=event.data_type,
            destination=event.destination,
            risk_score=event.risk_score or 0,
            action_taken=event.action_taken,
            source=event.detection_method or DetectionMethod.OTHER,
            event_ids=event_ids,
            status=AlertStatus.OPEN,
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        logger.info(
            "Alert generated: id=%s severity=%s title=%r event=%s",
            alert.id,
            alert.severity.value,
            alert.title,
            event.id,
        )

        return alert

    @staticmethod
    def _resolve_application(
        event: SecurityEvent,
        agent: Optional[AIAgent],
        db: Session,
    ) -> Optional[AIApplication]:
        """Find the application, preferring the event's own link then the agent's parent."""
        if event.application_id:
            return db.query(AIApplication).filter(
                AIApplication.id == event.application_id
            ).first()
        if agent:
            return agent.application
        return None

    @staticmethod
    def _build_title(event: SecurityEvent) -> str:
        """Pick a title, escalating the wording when data is leaving to an external destination."""
        try:
            event_type = SecurityEventType(event.event_type)
        except ValueError:
            return f"Security Event: {event.event_type}"

        exfiltration_types = {
            SecurityEventType.POLICY_VIOLATION,
            SecurityEventType.THREAT_DETECTED,
            SecurityEventType.EXTERNAL_COMMUNICATION,
            SecurityEventType.BLOCK_ACTION_TAKEN,
        }
        if event_type in exfiltration_types and event.data_type and event.destination:
            return "AI Agent Data Exfiltration Attempt"

        return TITLE_BY_EVENT_TYPE.get(event_type, f"Security Event: {event.event_type}")

    @staticmethod
    def _build_description(
        event: SecurityEvent,
        agent: Optional[AIAgent],
        application: Optional[AIApplication],
    ) -> str:
        """Assemble a description from whichever event fields are populated."""
        actor = agent.name if agent else "An unidentified agent"
        parts = [f"{actor} triggered a {event.severity.value} severity event"]

        if application:
            parts.append(f"under application '{application.name}'")
        if event.data_type:
            parts.append(f"involving {event.data_type} data")
        if event.source:
            parts.append(f"from {event.source}")
        if event.destination:
            parts.append(f"to destination '{event.destination}'")

        sentence = " ".join(parts) + "."

        detail = (
            f" Detected by {event.detection_method.value} "
            f"with a risk score of {float(event.risk_score or 0):.0f}/100. "
            f"Action taken: {event.action_taken.value}."
        ) if event.detection_method else (
            f" Risk score {float(event.risk_score or 0):.0f}/100. "
            f"Action taken: {event.action_taken.value}."
        )

        return sentence + detail

    @staticmethod
    def _snapshot_agent(agent: Optional[AIAgent]) -> Dict[str, Any]:
        if not agent:
            return {}
        return {
            "id": agent.id,
            "name": agent.name,
            "owner": agent.owner,
            "environment": agent.environment,
            "status": agent.status.value if agent.status else None,
            "risk_score": float(agent.risk_score or 0),
            "risk_level": agent.risk_level.value if agent.risk_level else None,
            "connected_tools": agent.connected_tools or [],
        }

    @staticmethod
    def _snapshot_application(application: Optional[AIApplication]) -> Dict[str, Any]:
        if not application:
            return {}
        return {
            "id": application.id,
            "name": application.name,
            "vendor": application.vendor,
            "category": application.category,
            "risk_score": float(application.risk_score or 0),
            "risk_level": application.risk_level.value if application.risk_level else None,
        }

    @staticmethod
    def to_siem_dict(alert: Alert) -> Dict[str, Any]:
        """Render an alert as the canonical SIEM-compatible JSON payload."""
        return {
            "alert_id": alert.id,
            "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
            "severity": alert.severity.value,
            "title": alert.title,
            "description": alert.description,
            "agent": alert.agent_snapshot or {},
            "application": alert.application_snapshot or {},
            "data_type": alert.data_type,
            "destination": alert.destination,
            "risk_score": float(alert.risk_score or 0),
            "action_taken": alert.action_taken.value,
            "source": alert.source.value,
            "events": alert.event_ids or [],
        }
