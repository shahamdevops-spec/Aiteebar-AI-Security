"""
Threat Detection Schema definitions for API request/response validation.
Uses Pydantic v2 for type validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ThreatEvidenceSchema(BaseModel):
    """Evidence collected for a threat"""
    key: str
    value: Any
    description: Optional[str] = None


class ThreatDetectionSchema(BaseModel):
    """Schema for detected threat"""
    id: Optional[str] = None
    agent_id: Optional[str] = Field(None, description="Agent UUID")
    threat_type: str = Field(..., description="Type of threat (rule name)")
    severity: str = Field(..., description="Severity: LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    confidence: float = Field(..., ge=0, le=100, description="Confidence 0-100")
    description: str = Field(..., description="Threat description and explanation")
    affected_resources: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: str = Field(..., description="Recommended mitigation action")
    timestamp: datetime
    resolved: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "threat_123",
                "agent_id": "agent_456",
                "threat_type": "CredentialExposureRule",
                "severity": "CRITICAL",
                "risk_score": 95.0,
                "confidence": 95.0,
                "description": "CRITICAL: 1 credential(s) exposed: API_KEY",
                "affected_resources": ["production_api"],
                "evidence": {
                    "exposed_credentials": {
                        "API_KEY": [
                            {
                                "confidence": 92.0,
                                "context": "...my api key is sk_live_abc123..."
                            }
                        ]
                    }
                },
                "recommended_action": "BLOCK immediately, ROTATE exposed credentials",
                "timestamp": "2025-09-13T10:30:45Z",
                "resolved": False
            }
        }


class ThreatDetectionRequestSchema(BaseModel):
    """Request for threat detection analysis"""
    agent_id: str = Field(..., description="Agent UUID to analyze")
    user_input: Optional[str] = Field(None, description="User prompt/input")
    dlp_events: List[Dict[str, Any]] = Field(default_factory=list, description="DLP detection results")
    network_connections: List[Dict[str, Any]] = Field(default_factory=list)
    attempted_tool: Optional[Dict[str, Any]] = Field(None)
    recent_requests: List[Dict[str, Any]] = Field(default_factory=list)
    access_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    tool_sequence: List[str] = Field(default_factory=list)


class ThreatDetectionResponseSchema(BaseModel):
    """Response containing detected threats"""
    agent_id: str
    timestamp: datetime
    total_threats: int
    threats: List[ThreatDetectionSchema]
    critical_count: int = Field(description="Number of CRITICAL threats")
    high_count: int = Field(description="Number of HIGH threats")
    medium_count: int = Field(description="Number of MEDIUM threats")
    low_count: int = Field(description="Number of LOW threats")
    severity_breakdown: Dict[str, int]
    risk_level: str = Field(description="Overall agent risk: LOW, MEDIUM, HIGH, CRITICAL")
    recommendation: str = Field(description="Overall recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "timestamp": "2025-09-13T10:30:45Z",
                "total_threats": 2,
                "threats": [],
                "critical_count": 1,
                "high_count": 1,
                "medium_count": 0,
                "low_count": 0,
                "severity_breakdown": {"CRITICAL": 1, "HIGH": 1},
                "risk_level": "CRITICAL",
                "recommendation": "ISOLATE agent, conduct full investigation"
            }
        }


class ThreatSummarySchema(BaseModel):
    """Summary statistics of threat detections"""
    total_threats: int
    severity_breakdown: Dict[str, int]
    threat_types: Dict[str, int]
    most_common_threat: Optional[str]
    trend: str = Field(description="Trend: increasing, decreasing, stable")
    high_severity_count: int = Field(description="CRITICAL + HIGH count")


class ThreatHistoryFilterSchema(BaseModel):
    """Query parameters for threat history filtering"""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    agent_id: Optional[str] = None
    severity: Optional[str] = None
    threat_type: Optional[str] = None
    days: Optional[int] = Field(default=7, ge=1, le=365)
    resolved_only: bool = Field(default=False)


class AgentThreatScoreSchema(BaseModel):
    """Agent threat score assessment"""
    agent_id: str
    overall_score: float = Field(..., ge=0, le=100)
    threat_count: int
    severity_breakdown: Dict[str, int]
    risk_level: str = Field(description="Overall risk: LOW, MEDIUM, HIGH, CRITICAL")
    recommendation: str
    recent_threat_types: List[str]
    last_threat_timestamp: Optional[datetime] = None


class RuleEvaluationResultSchema(BaseModel):
    """Individual rule evaluation result"""
    rule_name: str
    triggered: bool
    risk_score: float = Field(ge=0, le=100)
    severity: str
    explanation: str
    evidence: Dict[str, Any]
    timestamp: datetime


class MultiRuleEvaluationSchema(BaseModel):
    """Results of evaluating multiple rules"""
    timestamp: datetime
    agent_id: Optional[str]
    rules_evaluated: int
    rules_triggered: int
    threat_detections: List[ThreatDetectionSchema]
    processing_time_ms: float


class ThreatQuerySchema(BaseModel):
    """Query threat detection history"""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    agent_id: Optional[str] = None
    severity_filter: Optional[str] = None
    days: int = Field(default=7, ge=1, le=365)
    threat_type: Optional[str] = None


class ThreatResolutionSchema(BaseModel):
    """Mark threat as resolved"""
    threat_id: str
    resolved: bool = True
    resolution_notes: Optional[str] = None
    action_taken: Optional[str] = None
