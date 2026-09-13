"""
Risk Scoring Router - API endpoints for multi-factor risk assessment.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    AIApplication, AIAgent, MCPTool, Destination,
    DLPEvent, ThreatDetection
)
from ..schemas.risk_score import (
    RiskScoreSchema, RiskScoreSummarySchema, RiskScoreComparisonSchema,
    RiskRecommendationSchema, RiskTrendSchema
)
from ..services.risk.engine import RiskScoringEngine

engine = RiskScoringEngine()
router = APIRouter(prefix="/api/risk", tags=["Risk Scoring"])


def _get_app_data(app: AIApplication) -> dict:
    """Extract app data for risk scoring"""
    return {
        'name': app.name,
        'risk_score': float(app.risk_score) if app.risk_score else 0,
        'risk_level': app.risk_level.value if app.risk_level else 'LOW',
        'privacy_score': float(app.privacy_score) if app.privacy_score else 50,
        'security_score': float(app.security_score) if app.security_score else 50,
        'data_handling_score': float(app.data_handling_score) if app.data_handling_score else 50,
    }


def _get_agent_data(agent: AIAgent) -> dict:
    """Extract agent data for risk scoring"""
    return {
        'name': agent.name,
        'risk_score': float(agent.risk_score) if agent.risk_score else 0,
        'risk_level': agent.risk_level.value if agent.risk_level else 'LOW',
        'status': agent.status.value if agent.status else 'active',
        'connected_tools': agent.connected_tools or [],
        'data_access': agent.data_access or {},
    }


def _get_tool_data(tool: MCPTool) -> dict:
    """Extract tool data for risk scoring"""
    return {
        'name': tool.name,
        'data_sensitivity': tool.data_sensitivity.value if tool.data_sensitivity else 'LOW',
        'risk_score': float(tool.risk_score) if tool.risk_score else 0,
    }


def _get_destination_data(dest: Destination) -> dict:
    """Extract destination data for risk scoring"""
    return {
        'name': dest.name,
        'is_internal': dest.is_internal,
        'risk_score': float(dest.risk_score) if dest.risk_score else 0,
    }


@router.get("/score", response_model=RiskScoreSchema)
async def get_risk_score(
    entity_type: str = Query(..., description="Type: application, agent, tool, destination"),
    entity_id: str = Query(..., description="Entity UUID"),
    db: Session = Depends(get_db)
):
    """
    Calculate risk score for an entity.

    Supports:
    - application: Multi-factor risk assessment
    - agent: Comprehensive 7-factor assessment
    - tool: Tool-specific risk
    - destination: Network destination risk

    Returns detailed breakdown of all factors and recommendations.
    """
    try:
        if entity_type == 'application':
            app = db.query(AIApplication).filter(AIApplication.id == entity_id).first()
            if not app:
                raise HTTPException(status_code=404, detail="Application not found")

            app_data = _get_app_data(app)
            score = engine.calculate_application_risk(entity_id, app_data)

        elif entity_type == 'agent':
            agent = db.query(AIAgent).filter(AIAgent.id == entity_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            # Get application data
            app = db.query(AIApplication).filter(AIApplication.id == agent.application_id).first()
            app_data = _get_app_data(app) if app else {}

            # Get agent data
            agent_data = _get_agent_data(agent)

            # Get tools
            tools_data = [_get_tool_data(t) for t in agent.tools]

            # Get network connections (simulate from threat detections)
            connections = []

            # Get threats
            threats = db.query(ThreatDetection).filter(
                ThreatDetection.agent_id == entity_id,
                ThreatDetection.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).all()

            threats_data = [
                {
                    'severity': t.severity,
                    'risk_score': float(t.risk_score) if t.risk_score else 0,
                    'timestamp': t.timestamp,
                }
                for t in threats
            ]

            # Get DLP events
            dlp_events = db.query(DLPEvent).filter(
                DLPEvent.agent_id == entity_id,
                DLPEvent.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).all()

            dlp_data = [
                {
                    'severity': d.severity,
                    'data_type': d.data_type,
                    'confidence': float(d.confidence) if d.confidence else 0,
                }
                for d in dlp_events
            ]

            score = engine.calculate_agent_risk(
                entity_id, agent_data, app_data, tools_data,
                connections, threats_data, dlp_data
            )

        elif entity_type == 'tool':
            tool = db.query(MCPTool).filter(MCPTool.id == entity_id).first()
            if not tool:
                raise HTTPException(status_code=404, detail="Tool not found")

            tool_data = _get_tool_data(tool)
            score = engine.calculate_tool_risk(entity_id, tool_data)

        elif entity_type == 'destination':
            dest = db.query(Destination).filter(Destination.id == entity_id).first()
            if not dest:
                raise HTTPException(status_code=404, detail="Destination not found")

            dest_data = _get_destination_data(dest)
            score = engine.calculate_destination_risk(entity_id, dest_data)

        else:
            raise HTTPException(status_code=400, detail="Invalid entity_type")

        return RiskScoreSchema(**score.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")


@router.get("/summary", response_model=RiskScoreSummarySchema)
async def get_risk_summary(
    entity_type: str = Query(..., description="Type: application, agent, tool, destination"),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get summary of risk scores for all entities of a type.

    Provides:
    - Average risk score
    - Distribution by risk level
    - Highest and lowest scores
    """
    try:
        scores = []

        if entity_type == 'application':
            apps = db.query(AIApplication).all()
            for app in apps:
                app_data = _get_app_data(app)
                score = engine.calculate_application_risk(app.id, app_data)
                scores.append(score.overall_score)

        elif entity_type == 'agent':
            agents = db.query(AIAgent).all()
            for agent in agents:
                try:
                    app = db.query(AIApplication).filter(AIApplication.id == agent.application_id).first()
                    app_data = _get_app_data(app) if app else {}
                    agent_data = _get_agent_data(agent)
                    tools_data = [_get_tool_data(t) for t in agent.tools]

                    threats = db.query(ThreatDetection).filter(
                        ThreatDetection.agent_id == agent.id,
                        ThreatDetection.timestamp >= datetime.utcnow() - timedelta(days=days)
                    ).all()
                    threats_data = [
                        {'severity': t.severity, 'risk_score': float(t.risk_score) if t.risk_score else 0, 'timestamp': t.timestamp}
                        for t in threats
                    ]

                    dlp_events = db.query(DLPEvent).filter(
                        DLPEvent.agent_id == agent.id,
                        DLPEvent.timestamp >= datetime.utcnow() - timedelta(days=days)
                    ).all()
                    dlp_data = [
                        {'severity': d.severity, 'data_type': d.data_type, 'confidence': float(d.confidence) if d.confidence else 0}
                        for d in dlp_events
                    ]

                    score = engine.calculate_agent_risk(
                        agent.id, agent_data, app_data, tools_data, [], threats_data, dlp_data
                    )
                    scores.append(score.overall_score)
                except:
                    continue

        elif entity_type == 'tool':
            tools = db.query(MCPTool).all()
            for tool in tools:
                tool_data = _get_tool_data(tool)
                score = engine.calculate_tool_risk(tool.id, tool_data)
                scores.append(score.overall_score)

        elif entity_type == 'destination':
            dests = db.query(Destination).all()
            for dest in dests:
                dest_data = _get_destination_data(dest)
                score = engine.calculate_destination_risk(dest.id, dest_data)
                scores.append(score.overall_score)

        # Calculate summary statistics
        if scores:
            avg_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)
        else:
            avg_score = 0
            highest_score = 0
            lowest_score = 0

        # Count by risk level
        risk_levels = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for score in scores:
            if score >= 80:
                risk_levels['CRITICAL'] += 1
            elif score >= 60:
                risk_levels['HIGH'] += 1
            elif score >= 40:
                risk_levels['MEDIUM'] += 1
            else:
                risk_levels['LOW'] += 1

        return RiskScoreSummarySchema(
            summary_date=datetime.utcnow(),
            entity_type=entity_type,
            total_entities=len(scores),
            average_score=round(avg_score, 2),
            highest_risk_score=highest_score,
            lowest_risk_score=lowest_score,
            risk_level_breakdown=risk_levels,
            critical_count=risk_levels['CRITICAL'],
            high_count=risk_levels['HIGH'],
            medium_count=risk_levels['MEDIUM'],
            low_count=risk_levels['LOW'],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary calculation failed: {str(e)}")


@router.get("/recommendations/{entity_id}")
async def get_risk_recommendations(
    entity_id: str,
    entity_type: str = Query(..., description="Type: application, agent, tool, destination"),
    db: Session = Depends(get_db)
) -> RiskRecommendationSchema:
    """
    Get risk mitigation recommendations based on risk score.

    Provides actionable recommendations prioritized by severity.
    """
    try:
        # Get risk score
        if entity_type == 'agent':
            agent = db.query(AIAgent).filter(AIAgent.id == entity_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            app = db.query(AIApplication).filter(AIApplication.id == agent.application_id).first()
            app_data = _get_app_data(app) if app else {}
            agent_data = _get_agent_data(agent)
            tools_data = [_get_tool_data(t) for t in agent.tools]

            threats = db.query(ThreatDetection).filter(
                ThreatDetection.agent_id == entity_id
            ).all()
            threats_data = [
                {'severity': t.severity, 'risk_score': float(t.risk_score) if t.risk_score else 0, 'timestamp': t.timestamp}
                for t in threats
            ]

            dlp_events = db.query(DLPEvent).filter(
                DLPEvent.agent_id == entity_id
            ).all()
            dlp_data = [
                {'severity': d.severity, 'data_type': d.data_type, 'confidence': float(d.confidence) if d.confidence else 0}
                for d in dlp_events
            ]

            score = engine.calculate_agent_risk(
                entity_id, agent_data, app_data, tools_data, [], threats_data, dlp_data
            )
        else:
            raise HTTPException(status_code=400, detail="Only agent recommendations supported")

        # Generate recommendations based on risk level
        recommendations = []
        priority = score.risk_level

        if score.risk_level == 'CRITICAL':
            recommendations = [
                "IMMEDIATELY ISOLATE agent from production environment",
                "Conduct full forensic investigation of agent activities",
                "BLOCK all external connections",
                "REVOKE all elevated permissions",
                "AUDIT all accessed data and destinations",
                "Implement continuous monitoring and alerting",
                "Review and update security policies",
            ]
            remediation_time = "30 minutes - 2 hours"

        elif score.risk_level == 'HIGH':
            recommendations = [
                "RESTRICT tool access to essential tools only",
                "Increase monitoring frequency and alerting",
                "Review and audit data access permissions",
                "Implement rate limiting on requests",
                "Schedule security review and remediation",
                "Disable external connections until cleared",
                "Consider temporary suspension of non-critical tasks",
            ]
            remediation_time = "2-8 hours"

        elif score.risk_level == 'MEDIUM':
            recommendations = [
                "Monitor agent activity closely",
                "Review recent detections and threat alerts",
                "Schedule security assessment within 1 week",
                "Update access policies if needed",
                "Consider implementing additional controls",
                "Document risk mitigations taken",
            ]
            remediation_time = "1-3 days"

        else:  # LOW
            recommendations = [
                "Continue standard monitoring",
                "Review score periodically (monthly)",
                "Maintain current security controls",
                "Document baseline risk profile",
            ]
            remediation_time = "Ongoing"

        return RiskRecommendationSchema(
            entity_id=entity_id,
            risk_level=score.risk_level,
            recommendations=recommendations,
            priority=priority,
            estimated_remediation_time=remediation_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.get("/compare")
async def compare_risk_scores(
    entity1_type: str = Query(...),
    entity1_id: str = Query(...),
    entity2_type: str = Query(...),
    entity2_id: str = Query(...),
    db: Session = Depends(get_db)
) -> RiskScoreComparisonSchema:
    """
    Compare risk scores between two entities.

    Shows differences in scores and contributing factors.
    """
    # Calculate both scores
    # ... (similar to get_risk_score logic)
    # Then compare using engine.compare_risk_scores()

    raise HTTPException(status_code=501, detail="Compare endpoint coming soon")
