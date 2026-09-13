"""
Pydantic schemas for risk assessment responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevelEnum(str, Enum):
    """Risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DimensionScore(BaseModel):
    """A single risk dimension score"""
    dimension: str = Field(..., description="Dimension name (privacy, security, etc.)")
    score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    color: str = Field(..., description="Color code (green, yellow, orange, red)")
    label: str = Field(..., description="Risk label (Low Risk, Medium Risk, etc.)")
    explanation: str = Field(..., description="What this dimension means")


class RiskAssessmentResponse(BaseModel):
    """Complete risk assessment for an application"""
    application_id: str = Field(..., description="Application UUID")
    application_name: str = Field(..., description="Application name")

    overall_score: float = Field(..., ge=0, le=100, description="Overall risk score 0-100")
    risk_level: RiskLevelEnum = Field(..., description="Risk level category")
    risk_color: str = Field(..., description="Color for risk level")

    dimensions: List[DimensionScore] = Field(..., description="Breakdown by dimension")

    key_concerns: List[str] = Field(..., description="Key concerns for this application")
    recommended_controls: List[str] = Field(..., description="Recommended security controls")

    assessed_at: datetime = Field(..., description="When assessment was performed")
    next_assessment_date: Optional[datetime] = Field(None, description="When next assessment is due")
    days_until_reassessment: Optional[int] = Field(None, description="Days until next assessment")

    is_demo: bool = Field(..., description="Whether this is demo data")

    class Config:
        from_attributes = True


class RiskMetricsResponse(BaseModel):
    """Risk metrics summary"""
    total_applications: int
    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int
    average_score: float = Field(..., ge=0, le=100)
    highest_risk_applications: List[Dict[str, Any]]
    assessment_date: datetime


class RiskTrendResponse(BaseModel):
    """Risk trend data over time"""
    application_id: str
    application_name: str
    trend_data: List[Dict[str, Any]] = Field(..., description="Historical risk scores")
    current_score: float
    risk_level: RiskLevelEnum
    trend: str = Field(..., description="'improving', 'stable', or 'deteriorating'")


class UpdateRiskAssessmentRequest(BaseModel):
    """Request to update risk assessment"""
    privacy_score: Optional[float] = Field(None, ge=0, le=100)
    security_score: Optional[float] = Field(None, ge=0, le=100)
    data_handling_score: Optional[float] = Field(None, ge=0, le=100)
    enterprise_control_score: Optional[float] = Field(None, ge=0, le=100)
    integration_score: Optional[float] = Field(None, ge=0, le=100)
    permission_score: Optional[float] = Field(None, ge=0, le=100)

    notes: Optional[str] = Field(None, description="Assessment notes")
