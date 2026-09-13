"""Dashboard endpoints for metrics, charts, and recent activity"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import (
    AIApplication,
    AIAgent,
    SecurityEvent,
    AgentActivity,
    DLPEvent,
    PolicyAction,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get dashboard metrics summary.

    Returns count of applications, agents, connections, and critical items.
    """
    # Count total applications
    total_applications = db.query(func.count(AIApplication.id)).scalar() or 0

    # Count total agents
    total_agents = db.query(func.count(AIAgent.id)).scalar() or 0

    # Count high-risk applications (risk_level >= 65)
    high_risk_applications = (
        db.query(func.count(AIApplication.id))
        .filter(AIApplication.risk_level >= 65)
        .scalar() or 0
    )

    # Count critical agents (status = 'critical')
    critical_agents = (
        db.query(func.count(AIAgent.id))
        .filter(AIAgent.status == "critical")
        .scalar() or 0
    )

    # Count recent sensitive data events (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    sensitive_data_events = (
        db.query(func.count(DLPEvent.id))
        .filter(DLPEvent.created_at >= seven_days_ago)
        .scalar() or 0
    )

    # Count blocked actions (last 7 days)
    blocked_actions = (
        db.query(func.count(PolicyAction.id))
        .filter(
            and_(
                PolicyAction.action_type == "block",
                PolicyAction.created_at >= seven_days_ago,
            )
        )
        .scalar() or 0
    )

    # Count MCP connections (agents with mcp_tools)
    mcp_connections = (
        db.query(func.count(AIAgent.id))
        .filter(AIAgent.mcp_tools.isnot(None))
        .scalar() or 0
    )

    return {
        "total_applications": total_applications,
        "total_agents": total_agents,
        "mcp_connections": mcp_connections,
        "high_risk_applications": high_risk_applications,
        "critical_agents": critical_agents,
        "sensitive_data_events": sensitive_data_events,
        "blocked_actions": blocked_actions,
    }


@router.get("/risk-distribution")
async def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get distribution of risk levels across all applications.

    Returns count of applications in each risk level.
    """
    # Define risk level ranges
    low = db.query(func.count(AIApplication.id)).filter(AIApplication.risk_level < 25).scalar() or 0
    medium = db.query(func.count(AIApplication.id)).filter(
        and_(AIApplication.risk_level >= 25, AIApplication.risk_level < 50)
    ).scalar() or 0
    high = db.query(func.count(AIApplication.id)).filter(
        and_(AIApplication.risk_level >= 50, AIApplication.risk_level < 75)
    ).scalar() or 0
    critical = db.query(func.count(AIApplication.id)).filter(AIApplication.risk_level >= 75).scalar() or 0

    return {
        "low": low,
        "medium": medium,
        "high": high,
        "critical": critical,
    }


@router.get("/application-categories")
async def get_application_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get applications grouped by category with count and average risk.

    Returns list of categories with statistics.
    """
    results = (
        db.query(
            AIApplication.category,
            func.count(AIApplication.id).label("count"),
            func.avg(AIApplication.risk_level).label("avg_risk"),
        )
        .filter(AIApplication.category.isnot(None))
        .group_by(AIApplication.category)
        .all()
    )

    return [
        {
            "category": row[0] or "Uncategorized",
            "count": row[1],
            "risk_score": round(float(row[2]) if row[2] else 0, 1),
        }
        for row in results
    ]


@router.get("/recent-events")
async def get_recent_events(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get recent security events.

    Returns list of most recent security events.
    """
    events = (
        db.query(SecurityEvent)
        .order_by(SecurityEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(event.id),
            "name": event.event_type,
            "severity": event.severity,
            "timestamp": event.created_at.isoformat(),
            "application": event.ai_application.name if event.ai_application else "Unknown",
            "description": event.description,
        }
        for event in events
    ]


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get recent agent activity.

    Returns list of recent agent activities.
    """
    activities = (
        db.query(AgentActivity)
        .order_by(AgentActivity.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(activity.id),
            "agent_name": activity.agent.name if activity.agent else "Unknown",
            "action": activity.action_type,
            "status": activity.status,
            "timestamp": activity.created_at.isoformat(),
            "details": activity.details,
        }
        for activity in activities
    ]


@router.get("/top-risky-agents")
async def get_top_risky_agents(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get top agents by risk score.

    Returns list of agents with highest risk scores.
    """
    agents = (
        db.query(AIAgent)
        .order_by(AIAgent.risk_score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(agent.id),
            "name": agent.name,
            "risk_score": round(agent.risk_score, 1),
            "status": agent.status,
            "application": agent.ai_application.name if agent.ai_application else "Unknown",
            "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
        }
        for agent in agents
    ]


@router.get("/top-risky-applications")
async def get_top_risky_applications(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get top applications by risk level.

    Returns list of applications with highest risk levels.
    """
    applications = (
        db.query(AIApplication)
        .order_by(AIApplication.risk_level.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(app.id),
            "name": app.name,
            "risk_level": round(app.risk_level, 1),
            "status": app.status,
            "provider": app.ai_provider or "Unknown",
            "agent_count": len(app.agents) if app.agents else 0,
        }
        for app in applications
    ]
