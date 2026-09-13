"""
AI Agents API endpoints for managing deployed AI agents.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models import AIAgent, AgentStatus, AIApplication
from app.schemas.agents import AgentResponse, AgentListResponse, AgentActivityResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=AgentListResponse)
async def list_agents(
    db: Session = Depends(get_db),
    application: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("name", regex="^(name|risk_score|last_activity)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get paginated list of AI agents with filtering and sorting.

    Query parameters:
    - application: Filter by application name
    - environment: Filter by environment (dev, staging, prod)
    - status: Filter by status (active, inactive, suspended)
    - sort_by: Sort by 'name', 'risk_score', or 'last_activity'
    - sort_order: 'asc' or 'desc'
    - limit: Number of results (1-100)
    - offset: Pagination offset
    """

    query = db.query(AIAgent)

    # Apply filters
    if application:
        app = db.query(AIApplication).filter(
            AIApplication.name.ilike(f"%{application}%")
        ).first()
        if app:
            query = query.filter(AIAgent.application_id == app.id)

    if environment:
        query = query.filter(AIAgent.environment == environment)

    if status:
        query = query.filter(AIAgent.status == status)

    # Get total count
    total = query.count()

    # Apply sorting
    if sort_by == "risk_score":
        query = query.order_by(
            AIAgent.risk_score.desc() if sort_order == "desc" else AIAgent.risk_score
        )
    elif sort_by == "last_activity":
        query = query.order_by(
            AIAgent.last_activity.desc() if sort_order == "desc" else AIAgent.last_activity
        )
    else:
        query = query.order_by(
            AIAgent.name.desc() if sort_order == "desc" else AIAgent.name
        )

    # Apply pagination
    agents = query.limit(limit).offset(offset).all()

    return AgentListResponse(
        total=total,
        limit=limit,
        offset=offset,
        agents=agents
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific agent."""

    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.get("/{agent_id}/activity")
async def get_agent_activity(
    agent_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Get recent activity for an agent."""

    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    from app.models import AgentActivity

    activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id == agent_id
    ).order_by(
        AgentActivity.timestamp.desc()
    ).limit(limit).all()

    return {
        "agent_id": agent_id,
        "activities": [
            {
                "id": str(a.id),
                "timestamp": a.timestamp.isoformat(),
                "action_type": a.action_type.value,
                "resource_name": a.resource_name,
                "status": a.status.value,
                "risk_score": float(a.risk_score or 0),
            }
            for a in activities
        ],
        "total": len(activities)
    }


@router.get("/environments/list")
async def get_environments(db: Session = Depends(get_db)):
    """Get list of unique environments."""
    from sqlalchemy import func

    environments = db.query(
        AIAgent.environment
    ).distinct().filter(
        AIAgent.environment.isnot(None)
    ).all()

    return {
        "environments": [e[0] for e in environments if e[0]]
    }


@router.get("/owners/list")
async def get_owners(db: Session = Depends(get_db)):
    """Get list of unique owners."""
    from sqlalchemy import func

    owners = db.query(
        AIAgent.owner
    ).distinct().filter(
        AIAgent.owner.isnot(None)
    ).all()

    return {
        "owners": [o[0] for o in owners if o[0]]
    }
