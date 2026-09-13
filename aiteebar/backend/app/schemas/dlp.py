"""
DLP Schema definitions for API request/response validation.
Uses Pydantic v2 for type validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DetectedDataSchema(BaseModel):
    """Schema for individual detected sensitive data"""
    data_type: str = Field(..., description="Type of sensitive data detected")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    matched_content: str = Field(..., description="The matched data (truncated for safety)")
    context: str = Field(..., description="Surrounding context of the match")
    position: int = Field(..., ge=0, description="Position in text where match starts")

    class Config:
        json_schema_extra = {
            "example": {
                "data_type": "EMAIL",
                "confidence": 85.5,
                "severity": "MEDIUM",
                "matched_content": "user@example.com",
                "context": "...contact info is user@example.com for...",
                "position": 125,
            }
        }


class DLPScanRequest(BaseModel):
    """Request body for DLP scan endpoint"""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to scan")
    source: Optional[str] = Field(None, description="Source identifier (agent, api, etc)")
    scan_id: Optional[str] = Field(None, description="Optional scan correlation ID")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "My email is john@example.com and my API key is sk_live_abc123def456",
                "source": "agent_prompt_injection",
                "scan_id": "scan_12345"
            }
        }


class DLPScanResponse(BaseModel):
    """Response from DLP scan endpoint"""
    success: bool
    scan_id: str
    timestamp: datetime
    text_length: int
    detections: List[DetectedDataSchema]
    total_detections: int
    severity_breakdown: dict = Field(..., description="Count by severity level")
    data_types_found: List[str] = Field(default_factory=list)
    processing_time_ms: float = Field(..., description="Scan processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "scan_id": "scan_12345",
                "timestamp": "2025-09-13T10:30:45.123Z",
                "text_length": 500,
                "detections": [
                    {
                        "data_type": "EMAIL",
                        "confidence": 85.0,
                        "severity": "MEDIUM",
                        "matched_content": "john@example.com",
                        "context": "contact info is john@example.com for queries",
                        "position": 20
                    }
                ],
                "total_detections": 1,
                "severity_breakdown": {"MEDIUM": 1},
                "data_types_found": ["EMAIL"],
                "processing_time_ms": 15.5
            }
        }


class DLPEvent(BaseModel):
    """DLP event for logging and reporting"""
    id: Optional[str] = None
    timestamp: datetime
    agent_id: Optional[str] = Field(None, description="ID of the AI agent")
    agent_name: Optional[str] = Field(None, description="Name of the AI agent")
    source: str = Field(..., description="Source of the scan (prompt, response, memory, etc)")
    text_preview: str = Field(..., description="First 100 chars of scanned text")
    detections: List[DetectedDataSchema]
    total_detections: int
    severity_breakdown: dict = Field(..., description="Count by severity")
    action_taken: str = Field(default="flagged", description="Action taken (flagged, blocked, etc)")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-09-13T10:30:45.123Z",
                "agent_id": "agent_123",
                "agent_name": "DataAnalyzer",
                "source": "agent_prompt",
                "text_preview": "My email is john@example.com and password is...",
                "detections": [],
                "total_detections": 1,
                "severity_breakdown": {"EMAIL": 1},
                "action_taken": "flagged"
            }
        }


class DLPReportRequest(BaseModel):
    """Request for DLP report"""
    days: int = Field(default=7, ge=1, le=365, description="Number of days to report")
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    severity_filter: Optional[str] = Field(None, description="Filter by severity level")


class SeverityBreakdown(BaseModel):
    """Severity breakdown statistics"""
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    total: int = Field(default=0)


class DataTypeBreakdown(BaseModel):
    """Data type detection breakdown"""
    data_type: str
    count: int
    severity: str
    confidence_avg: float


class DLPReport(BaseModel):
    """DLP activity report"""
    report_date: datetime
    period_days: int
    total_events: int
    severity_breakdown: SeverityBreakdown
    data_types_found: List[DataTypeBreakdown]
    top_detected_types: List[str] = Field(description="Top 5 most detected data types")
    agents_with_detections: int = Field(description="Number of agents with detections")
    trend: Optional[str] = Field(None, description="Trend: increasing, decreasing, stable")

    class Config:
        json_schema_extra = {
            "example": {
                "report_date": "2025-09-13T10:30:45.123Z",
                "period_days": 7,
                "total_events": 25,
                "severity_breakdown": {
                    "critical": 3,
                    "high": 5,
                    "medium": 12,
                    "low": 5,
                    "total": 25
                },
                "data_types_found": [
                    {
                        "data_type": "EMAIL",
                        "count": 10,
                        "severity": "MEDIUM",
                        "confidence_avg": 85.5
                    }
                ],
                "top_detected_types": ["EMAIL", "API_KEY", "PASSWORD"],
                "agents_with_detections": 3,
                "trend": "stable"
            }
        }


class DLPEventQuery(BaseModel):
    """Query parameters for DLP event filtering"""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    agent_id: Optional[str] = None
    severity: Optional[str] = None
    data_type: Optional[str] = None
    days: Optional[int] = Field(default=7, ge=1, le=365)
