"""
Risk Scoring Schema definitions for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RiskFactorSchema(BaseModel):
    """Individual risk factor"""
    name: str = Field(..., description="Factor name")
    value: float = Field(..., ge=0, le=100, description="Factor value 0-100")
    weight: float = Field(..., ge=0, le=1, description="Weight in overall score (0-1)")
    weighted_contribution: float = Field(..., description="Value * Weight contribution")
    explanation: str = Field(..., description="Human-readable explanation")
    contributing_factors: Dict[str, Any] = Field(default_factory=dict, description="Component factors")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Application Risk",
                "value": 75.5,
                "weight": 0.25,
                "weighted_contribution": 18.9,
                "explanation": "Application 'DataProcessor' has HIGH risk level with 60% security score",
                "contributing_factors": {
                    "risk_score": 75.5,
                    "risk_level": 75,
                    "security_score": 60
                }
            }
        }


class RiskScoreSchema(BaseModel):
    """Complete risk assessment"""
    entity_type: str = Field(..., description="Type of entity: application, agent, tool, destination")
    entity_id: str = Field(..., description="UUID of the entity")
    overall_score: float = Field(..., ge=0, le=100, description="Overall risk score 0-100")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    factors: List[RiskFactorSchema] = Field(..., description="Individual risk factors")
    explanation: str = Field(..., description="Brief explanation of overall risk")
    detailed_explanation: str = Field(..., description="Detailed breakdown of all factors")
    timestamp: datetime = Field(..., description="When score was calculated")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "agent",
                "entity_id": "agent_12345",
                "overall_score": 68.3,
                "risk_level": "HIGH",
                "factors": [
                    {
                        "name": "Application Risk",
                        "value": 75.0,
                        "weight": 0.25,
                        "weighted_contribution": 18.75,
                        "explanation": "High-risk application",
                        "contributing_factors": {}
                    }
                ],
                "explanation": "Agent 'DataAnalyzer' has HIGH overall risk score (68.3/100)",
                "detailed_explanation": "Risk Factor Breakdown:\n1. Application Risk...",
                "timestamp": "2025-09-13T10:30:45Z"
            }
        }


class RiskScoreRequestSchema(BaseModel):
    """Request for risk score calculation"""
    entity_type: str = Field(..., description="Type: application, agent, tool, destination")
    entity_id: str = Field(..., description="Entity UUID")


class RiskScoreComparisonSchema(BaseModel):
    """Comparison between two risk scores"""
    entity1: Dict[str, Any] = Field(..., description="First entity info")
    entity2: Dict[str, Any] = Field(..., description="Second entity info")
    score_difference: float = Field(..., description="Absolute difference in scores")
    factor_differences: List[Dict[str, Any]] = Field(..., description="Factor-by-factor comparison")

    class Config:
        json_schema_extra = {
            "example": {
                "entity1": {
                    "type": "agent",
                    "id": "agent_1",
                    "score": 65.0,
                    "level": "HIGH"
                },
                "entity2": {
                    "type": "agent",
                    "id": "agent_2",
                    "score": 45.0,
                    "level": "MEDIUM"
                },
                "score_difference": 20.0,
                "factor_differences": [
                    {
                        "factor": "Data Sensitivity Level",
                        "entity1_value": 85.0,
                        "entity2_value": 45.0,
                        "difference": 40.0
                    }
                ]
            }
        }


class RiskTrendSchema(BaseModel):
    """Risk score trend over time"""
    entity_id: str = Field(..., description="Entity UUID")
    entity_type: str = Field(..., description="Entity type")
    current_score: float = Field(..., ge=0, le=100)
    previous_score: Optional[float] = Field(None, ge=0, le=100)
    trend: str = Field(..., description="Trend: increasing, decreasing, stable")
    change_percentage: Optional[float] = Field(None, description="Percentage change")
    data_points: int = Field(..., ge=1, description="Number of historical data points")
    period_days: int = Field(..., ge=1, description="Period covered in days")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "agent_123",
                "entity_type": "agent",
                "current_score": 68.3,
                "previous_score": 55.2,
                "trend": "increasing",
                "change_percentage": 23.7,
                "data_points": 30,
                "period_days": 30
            }
        }


class RiskRecommendationSchema(BaseModel):
    """Risk-based recommendations"""
    entity_id: str = Field(..., description="Entity UUID")
    risk_level: str = Field(..., description="Current risk level")
    recommendations: List[str] = Field(..., description="List of recommended actions")
    priority: str = Field(..., description="Priority: LOW, MEDIUM, HIGH, CRITICAL")
    estimated_remediation_time: Optional[str] = Field(None, description="Estimated time to remediate")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "agent_123",
                "risk_level": "HIGH",
                "recommendations": [
                    "RESTRICT tool access to essential tools only",
                    "Increase monitoring frequency",
                    "Review data access permissions",
                    "Implement rate limiting"
                ],
                "priority": "HIGH",
                "estimated_remediation_time": "2 hours"
            }
        }


class RiskScoreSummarySchema(BaseModel):
    """Summary of risk scores across entities"""
    summary_date: datetime = Field(..., description="Date of summary")
    entity_type: str = Field(..., description="Type of entities in summary")
    total_entities: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0, le=100)
    highest_risk_score: float = Field(..., ge=0, le=100)
    lowest_risk_score: float = Field(..., ge=0, le=100)
    risk_level_breakdown: Dict[str, int] = Field(..., description="Count by risk level")
    critical_count: int = Field(..., ge=0)
    high_count: int = Field(..., ge=0)
    medium_count: int = Field(..., ge=0)
    low_count: int = Field(..., ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "summary_date": "2025-09-13T10:30:45Z",
                "entity_type": "agent",
                "total_entities": 15,
                "average_score": 52.3,
                "highest_risk_score": 89.5,
                "lowest_risk_score": 12.3,
                "risk_level_breakdown": {
                    "CRITICAL": 1,
                    "HIGH": 4,
                    "MEDIUM": 7,
                    "LOW": 3
                },
                "critical_count": 1,
                "high_count": 4,
                "medium_count": 7,
                "low_count": 3
            }
        }
