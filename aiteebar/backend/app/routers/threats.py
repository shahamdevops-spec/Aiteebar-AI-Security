"""
Threat Detection Router - API endpoints for threat detection and analysis.
Implements RESTful endpoints for threat detection, querying, and reporting.
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ThreatDetection, AIAgent, DLPEvent
from ..schemas.threats import (
    ThreatDetectionSchema, ThreatDetectionResponseSchema, ThreatSummarySchema,
    AgentThreatScoreSchema, ThreatQuerySchema, MultiRuleEvaluationSchema,
    ThreatResolutionSchema
)
from ..services.threat_detection.engine import ThreatDetectionEngine

# Initialize threat detection engine
threat_engine = ThreatDetectionEngine()
router = APIRouter(prefix="/api/threats", tags=["Threats"])


def _build_context(agent_id: str, db: Session) -> dict:
    """Build context for threat detection from database state"""
    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get recent DLP events for this agent
    dlp_events = db.query(DLPEvent).filter(
        DLPEvent.agent_id == agent_id,
        DLPEvent.timestamp >= datetime.utcnow() - timedelta(hours=1)
    ).all()

    dlp_event_dicts = [
        {
            'data_type': e.data_type,
            'severity': e.severity,
            'confidence': float(e.confidence) if e.confidence else 0,
            'context': e.matched_context[:100] if e.matched_context else '',
            'timestamp': e.timestamp,
        }
        for e in dlp_events
    ]

    return {
        'agent_id': agent_id,
        'agent_name': agent.name,
        'dlp_events': dlp_event_dicts,
        'network_connections': [],  # Would be populated from actual network logs
        'recent_requests': [],
        'access_patterns': [],
        'tool_sequence': [],
    }


@router.post("/detect")
async def detect_threats(
    agent_id: str = Query(..., description="Agent UUID"),
    user_input: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Detect threats for a specific agent.

    Evaluates all threat detection rules against the agent's current state.

    Args:
        agent_id: UUID of the agent to analyze
        user_input: Optional user prompt/input to check for prompt injection

    Returns:
        ThreatDetectionResponseSchema with detected threats
    """
    try:
        start_time = time.time()

        # Build context from database state
        context = _build_context(agent_id, db)

        # Add user input if provided
        if user_input:
            context['user_input'] = user_input

        # Detect threats
        detected_threats = threat_engine.detect_threats(context)

        # Count by severity
        severity_counts = {
            'CRITICAL': len([t for t in detected_threats if t.severity == 'CRITICAL']),
            'HIGH': len([t for t in detected_threats if t.severity == 'HIGH']),
            'MEDIUM': len([t for t in detected_threats if t.severity == 'MEDIUM']),
            'LOW': len([t for t in detected_threats if t.severity == 'LOW']),
        }

        # Determine overall risk level
        if severity_counts['CRITICAL'] > 0:
            risk_level = 'CRITICAL'
        elif severity_counts['HIGH'] > 0:
            risk_level = 'HIGH'
        elif severity_counts['MEDIUM'] > 0:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        # Recommendation
        recommendations = {
            'CRITICAL': 'ISOLATE agent, conduct full investigation',
            'HIGH': 'RESTRICT permissions, increase monitoring',
            'MEDIUM': 'Monitor activity, schedule review',
            'LOW': 'Continue normal monitoring',
        }

        # Save threats to database
        for threat in detected_threats:
            threat.id = str(uuid.uuid4())
            db_threat = ThreatDetection(
                id=threat.id,
                agent_id=agent_id,
                threat_type=threat.threat_type,
                severity=threat.severity,
                risk_score=threat.risk_score,
                confidence=threat.confidence,
                description=threat.description,
                evidence=threat.evidence,
                affected_resources=threat.affected_resources,
                recommended_action=threat.recommended_action,
                timestamp=threat.timestamp,
            )
            db.add(db_threat)

        db.commit()

        processing_time = (time.time() - start_time) * 1000

        return ThreatDetectionResponseSchema(
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            total_threats=len(detected_threats),
            threats=[ThreatDetectionSchema(
                id=t.id,
                agent_id=agent_id,
                threat_type=t.threat_type,
                severity=t.severity,
                risk_score=t.risk_score,
                confidence=t.confidence,
                description=t.description,
                affected_resources=t.affected_resources,
                evidence=t.evidence,
                recommended_action=t.recommended_action,
                timestamp=t.timestamp,
                resolved=False,
            ) for t in detected_threats],
            critical_count=severity_counts['CRITICAL'],
            high_count=severity_counts['HIGH'],
            medium_count=severity_counts['MEDIUM'],
            low_count=severity_counts['LOW'],
            severity_breakdown=severity_counts,
            risk_level=risk_level,
            recommendation=recommendations[risk_level],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat detection failed: {str(e)}")


@router.get("/events")
async def get_threats(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    threat_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Retrieve threat detections with optional filtering.

    Args:
        limit: Maximum results to return
        offset: Pagination offset
        agent_id: Filter by agent ID
        severity: Filter by severity level
        threat_type: Filter by threat type
        days: Include threats from last N days

    Returns:
        List of threat detection records
    """
    try:
        query = db.query(ThreatDetection)

        # Time filter
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(ThreatDetection.timestamp >= cutoff_date)

        # Optional filters
        if agent_id:
            query = query.filter(ThreatDetection.agent_id == agent_id)
        if severity:
            query = query.filter(ThreatDetection.severity == severity)
        if threat_type:
            query = query.filter(ThreatDetection.threat_type == threat_type)

        # Order by most recent first
        threats = query.order_by(desc(ThreatDetection.timestamp)).offset(offset).limit(limit).all()

        # Convert to schema
        return [
            ThreatDetectionSchema(
                id=threat.id,
                agent_id=threat.agent_id,
                threat_type=threat.threat_type,
                severity=threat.severity,
                risk_score=float(threat.risk_score) if threat.risk_score else 0,
                confidence=float(threat.confidence) if threat.confidence else 0,
                description=threat.description,
                affected_resources=threat.affected_resources or [],
                evidence=threat.evidence or {},
                recommended_action=threat.recommended_action or '',
                timestamp=threat.timestamp,
                resolved=threat.resolved,
            )
            for threat in threats
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve threats: {str(e)}")


@router.get("/summary")
async def get_threat_summary(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of threat detections.

    Args:
        days: Include threats from last N days

    Returns:
        Summary with threat counts and statistics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(ThreatDetection).filter(
            ThreatDetection.timestamp >= cutoff_date
        )
        threats = query.all()

        severity_breakdown = {
            'CRITICAL': len([t for t in threats if t.severity == 'CRITICAL']),
            'HIGH': len([t for t in threats if t.severity == 'HIGH']),
            'MEDIUM': len([t for t in threats if t.severity == 'MEDIUM']),
            'LOW': len([t for t in threats if t.severity == 'LOW']),
        }

        threat_types = {}
        for threat in threats:
            threat_types[threat.threat_type] = threat_types.get(threat.threat_type, 0) + 1

        # Determine trend
        mid_date = cutoff_date + timedelta(days=days/2)
        early_critical = len([t for t in threats if t.timestamp < mid_date and t.severity == 'CRITICAL'])
        late_critical = len([t for t in threats if t.timestamp >= mid_date and t.severity == 'CRITICAL'])

        if late_critical > early_critical * 1.1:
            trend = 'increasing'
        elif late_critical < early_critical * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'

        return ThreatSummarySchema(
            total_threats=len(threats),
            severity_breakdown=severity_breakdown,
            threat_types=threat_types,
            most_common_threat=max(threat_types, key=threat_types.get) if threat_types else None,
            trend=trend,
            high_severity_count=severity_breakdown['CRITICAL'] + severity_breakdown['HIGH'],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/agent/{agent_id}/score")
async def get_agent_threat_score(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    Calculate overall threat score for a specific agent.

    Args:
        agent_id: UUID of the agent

    Returns:
        AgentThreatScoreSchema with threat score and recommendations
    """
    try:
        agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        threats = db.query(ThreatDetection).filter(
            ThreatDetection.agent_id == agent_id
        ).all()

        if not threats:
            return AgentThreatScoreSchema(
                agent_id=agent_id,
                overall_score=0.0,
                threat_count=0,
                severity_breakdown={'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                risk_level='LOW',
                recommendation='No threats detected',
                recent_threat_types=[],
            )

        # Calculate weighted score
        severity_weights = {'CRITICAL': 100, 'HIGH': 60, 'MEDIUM': 30, 'LOW': 10}
        total_score = 0.0
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        recent_threats = threats[-100:]

        for threat in recent_threats:
            weight = severity_weights.get(threat.severity, 0)
            total_score += weight
            severity_counts[threat.severity] += 1

        overall_score = (total_score / (len(recent_threats) * 100)) * 100 if recent_threats else 0.0

        # Determine risk level
        if overall_score >= 80:
            risk_level = 'CRITICAL'
            recommendation = 'ISOLATE agent, conduct full investigation'
        elif overall_score >= 60:
            risk_level = 'HIGH'
            recommendation = 'RESTRICT permissions, increase monitoring'
        elif overall_score >= 40:
            risk_level = 'MEDIUM'
            recommendation = 'Monitor activity, schedule review'
        else:
            risk_level = 'LOW'
            recommendation = 'Continue normal monitoring'

        recent_threat_types = list(set(t.threat_type for t in recent_threats[-10:]))

        return AgentThreatScoreSchema(
            agent_id=agent_id,
            overall_score=overall_score,
            threat_count=len(threats),
            severity_breakdown=severity_counts,
            risk_level=risk_level,
            recommendation=recommendation,
            recent_threat_types=recent_threat_types,
            last_threat_timestamp=threats[-1].timestamp if threats else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate threat score: {str(e)}")


@router.post("/threats/{threat_id}/resolve")
async def resolve_threat(
    threat_id: str,
    request: ThreatResolutionSchema,
    db: Session = Depends(get_db)
):
    """
    Mark a threat as resolved.

    Args:
        threat_id: UUID of the threat
        request: Resolution details

    Returns:
        Updated threat detection
    """
    try:
        threat = db.query(ThreatDetection).filter(ThreatDetection.id == threat_id).first()
        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")

        threat.resolved = request.resolved
        threat.updated_at = datetime.utcnow()
        db.commit()

        return ThreatDetectionSchema(
            id=threat.id,
            agent_id=threat.agent_id,
            threat_type=threat.threat_type,
            severity=threat.severity,
            risk_score=float(threat.risk_score) if threat.risk_score else 0,
            confidence=float(threat.confidence) if threat.confidence else 0,
            description=threat.description,
            affected_resources=threat.affected_resources or [],
            evidence=threat.evidence or {},
            recommended_action=threat.recommended_action or '',
            timestamp=threat.timestamp,
            resolved=threat.resolved,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve threat: {str(e)}")
