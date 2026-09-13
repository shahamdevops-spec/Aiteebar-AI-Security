"""
AI Applications API endpoints for browsing and managing AI applications catalog.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import AIApplication, RiskLevel
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/applications", tags=["applications"])


# ============================================================================
# SCHEMAS
# ============================================================================

from pydantic import BaseModel

class ApplicationResponse(BaseModel):
    id: str
    name: str
    vendor: Optional[str]
    category: Optional[str]
    description: Optional[str]
    risk_score: Optional[float]
    risk_level: str
    privacy_score: Optional[float]
    security_score: Optional[float]
    data_handling_score: Optional[float]
    enterprise_control_score: Optional[float]
    integration_score: Optional[float]
    permission_score: Optional[float]
    mcp_support: bool
    api_available: bool
    data_residency: Optional[str]
    is_demo: bool
    last_assessed: Optional[str]

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    applications: List[ApplicationResponse]


class CategoryCount(BaseModel):
    category: str
    count: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("name", regex="^(name|risk_score)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get paginated list of AI applications with optional filtering and sorting.

    Query parameters:
    - category: Filter by category
    - risk_level: Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)
    - search: Search by name, vendor, or description
    - sort_by: Sort by 'name' or 'risk_score'
    - sort_order: 'asc' or 'desc'
    - limit: Number of results (1-100)
    - offset: Pagination offset
    """

    query = db.query(AIApplication)

    # Apply filters
    if category:
        query = query.filter(AIApplication.category == category)

    if risk_level:
        query = query.filter(AIApplication.risk_level == risk_level)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (AIApplication.name.ilike(search_term)) |
            (AIApplication.vendor.ilike(search_term)) |
            (AIApplication.description.ilike(search_term))
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort_by == "risk_score":
        query = query.order_by(
            AIApplication.risk_score.desc() if sort_order == "desc" else AIApplication.risk_score
        )
    else:
        query = query.order_by(
            AIApplication.name.desc() if sort_order == "desc" else AIApplication.name
        )

    # Apply pagination
    applications = query.limit(limit).offset(offset).all()

    return ApplicationListResponse(
        total=total,
        limit=limit,
        offset=offset,
        applications=applications
    )


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of unique categories and their application counts."""

    results = db.query(
        AIApplication.category,
        func.count(AIApplication.id).label("count")
    ).filter(
        AIApplication.category.isnot(None)
    ).group_by(
        AIApplication.category
    ).order_by(
        func.count(AIApplication.id).desc()
    ).all()

    return [
        CategoryCount(category=cat, count=count)
        for cat, count in results
    ]


@router.get("/search")
async def search_applications(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50),
):
    """Search applications by name, vendor, or description."""

    search_term = f"%{q}%"
    applications = db.query(AIApplication).filter(
        (AIApplication.name.ilike(search_term)) |
        (AIApplication.vendor.ilike(search_term)) |
        (AIApplication.description.ilike(search_term))
    ).limit(limit).all()

    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific application."""

    application = db.query(AIApplication).filter(
        AIApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application
