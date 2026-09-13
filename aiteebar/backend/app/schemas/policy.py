"""
Pydantic schemas for policy management APIs
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PolicyActionEnum(str, Enum):
    """Policy enforcement actions"""
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class TriggerDefinition(BaseModel):
    """Policy trigger definition"""
    field: str = Field(..., description="Event field to check")
    operator: str = Field(..., description="Comparison operator")
    value: str = Field(..., description="Value to compare against")


class ConditionDefinition(BaseModel):
    """Policy condition with multiple triggers"""
    entity_type: Optional[str] = Field(None, description="Entity type to match")
    triggers: List[TriggerDefinition] = Field(..., description="List of triggers")
    logic: str = Field("AND", description="Logic operator: AND or OR")


class PolicyCreate(BaseModel):
    """Create a new policy"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    condition: ConditionDefinition = Field(..., description="Policy conditions and triggers")
    action: PolicyActionEnum = Field(..., description="Action to take when policy matches")
    priority: int = Field(100, ge=0, description="Lower = higher priority")
    enabled: bool = Field(True, description="Whether policy is enabled")


class PolicyUpdate(BaseModel):
    """Update an existing policy"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    condition: Optional[ConditionDefinition] = None
    action: Optional[PolicyActionEnum] = None
    priority: Optional[int] = Field(None, ge=0)
    enabled: Optional[bool] = None


class PolicyResponse(BaseModel):
    """Policy details response"""
    id: str
    name: str
    description: Optional[str]
    condition: Dict[str, Any]
    action: str
    priority: int
    enabled: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolicyExecutionResponse(BaseModel):
    """Policy execution audit log entry"""
    id: str
    policy_id: str
    event_id: str
    action_taken: str
    matched_conditions: Dict[str, Any]
    reasoning: Optional[str]
    executed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyStatisticsResponse(BaseModel):
    """Policy system statistics"""
    total_policies: int
    enabled_policies: int
    total_executions: int
    executions_by_action: Dict[str, int]
