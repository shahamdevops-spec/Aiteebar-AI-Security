"""
Risk assessment API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models import AIApplication
from app.schemas.risk import RiskAssessmentResponse, DimensionScore, RiskMetricsResponse
from app.services.risk import RiskAssessmentService

router = APIRouter(prefix="/api/risk", tags=["risk"])


def build_risk_assessment(app: AIApplication, db: Session = None) -> RiskAssessmentResponse:
    """Build a complete risk assessment response from an application"""

    dimensions_data = {
        "privacy": app.privacy_score,
        "security": app.security_score,
        "data_handling": app.data_handling_score,
        "enterprise_control": app.enterprise_control_score,
        "integration": app.integration_score,
        "permission": app.permission_score,
    }

    # Build dimension scores
    explanations = RiskAssessmentService.create_dimension_explanations()
    dimensions = []

    for dim_name, score in dimensions_data.items():
        if score is None:
            score = 0
        formatted = RiskAssessmentService.format_dimension_score(float(score))
        dimensions.append(DimensionScore(
            dimension=dim_name,
            score=formatted["score"],
            color=formatted["color"],
            label=formatted["label"],
            explanation=explanations.get(dim_name, ""),
        ))

    # Get concerns and controls
    app_dict = {
        "privacy_score": app.privacy_score,
        "security_score": app.security_score,
        "data_handling_score": app.data_handling_score,
        "enterprise_control_score": app.enterprise_control_score,
        "integration_score": app.integration_score,
        "permission_score": app.permission_score,
        "risk_score": app.risk_score,
    }

    key_concerns = RiskAssessmentService.get_key_concerns(app_dict)
    recommended_controls = RiskAssessmentService.get_recommended_controls(app_dict)

    # Calculate next assessment date
    next_assessment = None
    days_until = None
    if app.last_assessed:
        next_assessment = RiskAssessmentService.calculate_next_assessment_date(90)
        days_until = (next_assessment - datetime.utcnow()).days
        if days_until < 0:
            days_until = 0

    overall_score = float(app.risk_score or 0)
    risk_level = RiskAssessmentService.categorize_risk_level(overall_score)
    risk_color = RiskAssessmentService.get_risk_color(overall_score)

    return RiskAssessmentResponse(
        application_id=str(app.id),
        application_name=app.name,
        overall_score=round(overall_score, 2),
        risk_level=risk_level,
        risk_color=risk_color,
        dimensions=dimensions,
        key_concerns=key_concerns,
        recommended_controls=recommended_controls,
        assessed_at=app.last_assessed or datetime.utcnow(),
        next_assessment_date=next_assessment,
        days_until_reassessment=days_until,
        is_demo=app.is_demo,
    )


@router.get("/applications/{application_id}", response_model=RiskAssessmentResponse)
async def get_application_risk(
    application_id: str,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive risk assessment for an application.

    Returns detailed risk breakdown with:
    - Overall risk score and level
    - Dimension-by-dimension analysis
    - Key concerns
    - Recommended controls
    """

    app = db.query(AIApplication).filter(
        AIApplication.id == application_id
    ).first()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return build_risk_assessment(app, db)


@router.get("/metrics", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    db: Session = Depends(get_db),
):
    """
    Get overall risk metrics across all applications.

    Returns:
    - Count by risk level
    - Average score
    - Highest risk applications
    """

    apps = db.query(AIApplication).all()

    if not apps:
        return RiskMetricsResponse(
            total_applications=0,
            low_risk=0,
            medium_risk=0,
            high_risk=0,
            critical_risk=0,
            average_score=0,
            highest_risk_applications=[],
            assessment_date=datetime.utcnow(),
        )

    low_count = 0
    medium_count = 0
    high_count = 0
    critical_count = 0
    total_score = 0

    highest_risk = []

    for app in apps:
        score = float(app.risk_score or 0)
        total_score += score

        level = RiskAssessmentService.categorize_risk_level(score)
        if level == "LOW":
            low_count += 1
        elif level == "MEDIUM":
            medium_count += 1
        elif level == "HIGH":
            high_count += 1
        else:
            critical_count += 1

        highest_risk.append({
            "id": str(app.id),
            "name": app.name,
            "risk_score": float(app.risk_score or 0),
            "risk_level": level,
            "vendor": app.vendor,
        })

    # Sort and get top 10 highest risk
    highest_risk.sort(key=lambda x: x["risk_score"], reverse=True)
    highest_risk = highest_risk[:10]

    average_score = total_score / len(apps) if apps else 0

    return RiskMetricsResponse(
        total_applications=len(apps),
        low_risk=low_count,
        medium_risk=medium_count,
        high_risk=high_count,
        critical_risk=critical_count,
        average_score=round(average_score, 2),
        highest_risk_applications=highest_risk,
        assessment_date=datetime.utcnow(),
    )


@router.get("/by-level/{risk_level}")
async def get_applications_by_risk_level(
    risk_level: str,
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """
    Get all applications at a specific risk level.

    Risk levels: LOW, MEDIUM, HIGH, CRITICAL
    """

    if risk_level.upper() not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid risk level. Use: LOW, MEDIUM, HIGH, CRITICAL"
        )

    apps = db.query(AIApplication).filter(
        AIApplication.risk_level == risk_level.upper()
    ).limit(limit).all()

    return {
        "risk_level": risk_level.upper(),
        "count": len(apps),
        "applications": [
            {
                "id": str(app.id),
                "name": app.name,
                "vendor": app.vendor,
                "risk_score": float(app.risk_score or 0),
                "category": app.category,
            }
            for app in apps
        ]
    }
