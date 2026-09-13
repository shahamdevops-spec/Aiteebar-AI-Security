"""
Pydantic schemas for agent endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatusEnum(str, Enum):
    """Agent status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class MCPToolResponse(BaseModel):
    """Connected MCP tool information"""
    id: str = Field(..., description="Tool ID")
    name: str = Field(..., description="Tool name")
    type: str = Field(..., description="Tool type (database, api, file, etc.)")
    permissions: List[str] = Field(..., description="List of permissions (read, write, execute)")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score for this tool")
    status: str = Field(..., description="Tool status")


class AgentResponse(BaseModel):
    """Complete agent information"""
    id: str = Field(..., description="Agent UUID")
    application_id: str = Field(..., description="Connected application ID")
    application_name: Optional[str] = Field(None, description="Connected application name")

    name: str = Field(..., description="Agent name")
    owner: Optional[str] = Field(None, description="Agent owner/team")
    environment: Optional[str] = Field(None, description="Environment (dev, staging, prod)")

    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score")
    risk_level: str = Field(..., description="Risk level (LOW, MEDIUM, HIGH, CRITICAL)")

    connected_tools: List[Dict[str, Any]] = Field(..., description="Connected MCP tools")
    data_access: Dict[str, Any] = Field(..., description="Data access overview")

    status: str = Field(..., description="Agent status (active, inactive, suspended)")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Paginated agent list response"""
    total: int
    limit: int
    offset: int
    agents: List[AgentResponse]


class AgentActivityResponse(BaseModel):
    """Agent activity record"""
    id: str
    timestamp: datetime
    action_type: str
    resource_name: Optional[str]
    status: str
    risk_score: float


class AgentCreate(BaseModel):
    """Request to create an agent"""
    name: str = Field(..., min_length=1, max_length=255)
    application_id: str
    owner: Optional[str] = None
    environment: Optional[str] = None
    connected_tools: Optional[List[str]] = None
    data_access: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    """Request to update an agent"""
    name: Optional[str] = None
    owner: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[AgentStatusEnum] = None
    connected_tools: Optional[List[str]] = None
    data_access: Optional[Dict[str, Any]] = None
