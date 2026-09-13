"""
SQLAlchemy ORM models for Aiteebar AI Security database schema.
Corresponds to the PostgreSQL schema defined in database/schema.sql
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from sqlalchemy import (
    Column, String, UUID, DateTime, Boolean, Numeric, Text, Integer,
    ForeignKey, CheckConstraint, Index, Enum as SQLEnum, func
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


# ============================================================================
# ENUM DEFINITIONS
# ============================================================================

class UserRole(str, Enum):
    """User roles for access control"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class RiskLevel(str, Enum):
    """Risk levels for applications, agents, tools"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentStatus(str, Enum):
    """Agent deployment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ActionType(str, Enum):
    """Types of actions agents can perform"""
    CONNECT = "CONNECT"
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    EXTERNAL_CALL = "EXTERNAL_CALL"


class ActivityStatus(str, Enum):
    """Status of recorded activities"""
    PENDING = "pending"
    EXECUTED = "executed"
    BLOCKED = "blocked"


class DataType(str, Enum):
    """Sensitive data types for DLP detection"""
    CNIC = "CNIC"
    IBAN = "IBAN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    PASSPORT = "PASSPORT"
    HEALTH_RECORD = "HEALTH_RECORD"
    OTHER = "OTHER"


class EventSeverity(str, Enum):
    """Severity levels for events"""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionTaken(str, Enum):
    """Actions taken on events"""
    ALLOWED = "ALLOWED"
    WARNED = "WARNED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    BLOCKED = "BLOCKED"


class EventStatus(str, Enum):
    """Status of security events"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class DetectionMethod(str, Enum):
    """Methods for detecting security events"""
    POLICY_ENGINE = "policy_engine"
    DLP = "dlp"
    THREAT_DETECTION = "threat_detection"
    MANUAL = "manual"
    OTHER = "other"


class PolicyAction(str, Enum):
    """Policy actions"""
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class ToolStatus(str, Enum):
    """MCP tool status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class EntityType(str, Enum):
    """Entity types for risk assessments"""
    APPLICATION = "application"
    AGENT = "agent"
    TOOL = "tool"


# ============================================================================
# 1. USERS MODEL
# ============================================================================

class User(Base):
    """User accounts with role-based access control"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    policies = relationship("Policy", back_populates="created_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# ============================================================================
# 2. AI_APPLICATIONS MODEL
# ============================================================================

class AIApplication(Base):
    """AI applications and services being assessed"""
    __tablename__ = "ai_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    vendor = Column(String(255), index=True)
    category = Column(String(100))
    description = Column(Text)

    # Risk Scores
    risk_score = Column(Numeric(5, 2), default=0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)

    # Dimension Scores
    privacy_score = Column(Numeric(5, 2))
    security_score = Column(Numeric(5, 2))
    data_handling_score = Column(Numeric(5, 2))
    enterprise_control_score = Column(Numeric(5, 2))
    integration_score = Column(Numeric(5, 2))
    permission_score = Column(Numeric(5, 2))

    # Features
    mcp_support = Column(Boolean, default=False, index=True)
    api_available = Column(Boolean, default=False)
    enterprise_controls = Column(JSONB, default={})
    data_residency = Column(String(100))
    authentication = Column(JSONB, default={})

    # Additional
    notes = Column(Text)
    is_demo = Column(Boolean, default=False, index=True)
    last_assessed = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agents = relationship("AIAgent", back_populates="application", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="application")
    risk_assessments = relationship("RiskAssessment", back_populates="application")

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100"),
        Index("idx_ai_applications_risk_score", risk_score.desc()),
    )

    def __repr__(self):
        return f"<AIApplication(id={self.id}, name={self.name}, risk_level={self.risk_level})>"


# ============================================================================
# 3. AI_AGENTS MODEL
# ============================================================================

class AIAgent(Base):
    """AI agents deployed from applications"""
    __tablename__ = "ai_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("ai_applications.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255))
    environment = Column(String(100))

    # Risk Assessment
    risk_score = Column(Numeric(5, 2), default=0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)

    # Capabilities
    connected_tools = Column(JSONB, default=[])
    data_access = Column(JSONB, default={})

    # Status
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.ACTIVE, nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    application = relationship("AIApplication", back_populates="agents")
    tools = relationship("MCPTool", back_populates="agent", cascade="all, delete-orphan")
    activities = relationship("AgentActivity", back_populates="agent", cascade="all, delete-orphan")
    dlp_events = relationship("DLPEvent", back_populates="agent", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="agent")
    risk_assessments = relationship("RiskAssessment", back_populates="agent")

    def __repr__(self):
        return f"<AIAgent(id={self.id}, name={self.name}, status={self.status})>"


# ============================================================================
# 4. MCP_TOOLS MODEL
# ============================================================================

class MCPTool(Base):
    """MCP tools used by agents"""
    __tablename__ = "mcp_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    description = Column(Text)

    # Permissions as JSON array
    permissions = Column(JSONB, default=[])

    # Data Sensitivity
    data_sensitivity = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)

    # Risk Assessment
    risk_score = Column(Numeric(5, 2), default=0)

    # Status
    status = Column(SQLEnum(ToolStatus), default=ToolStatus.ACTIVE, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", back_populates="tools")
    activities = relationship("AgentActivity", back_populates="tool")
    security_events = relationship("SecurityEvent", back_populates="tool")
    risk_assessments = relationship("RiskAssessment", back_populates="tool")

    def __repr__(self):
        return f"<MCPTool(id={self.id}, name={self.name}, type={self.type})>"


# ============================================================================
# 5. AGENT_ACTIVITY MODEL
# ============================================================================

class AgentActivity(Base):
    """Log of agent actions and activities"""
    __tablename__ = "agent_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp_tools.id", ondelete="SET NULL"), index=True)

    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)

    resource_name = Column(String(255))
    status = Column(SQLEnum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False, index=True)

    risk_score = Column(Numeric(5, 2), default=0, index=True)

    # Detailed metadata
    agent_metadata = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", back_populates="activities")
    tool = relationship("MCPTool", back_populates="activities")

    __table_args__ = (
        Index("idx_agent_activity_risk_score", risk_score.desc()),
    )

    def __repr__(self):
        return f"<AgentActivity(id={self.id}, action={self.action_type}, status={self.status})>"


# ============================================================================
# 6. DLP_EVENTS MODEL
# ============================================================================

class DLPEvent(Base):
    """Data Loss Prevention events"""
    __tablename__ = "dlp_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    # Data Type Detection
    data_type = Column(SQLEnum(DataType), nullable=False, index=True)

    confidence = Column(Numeric(5, 2))
    severity = Column(SQLEnum(EventSeverity), default=EventSeverity.MEDIUM, nullable=False, index=True)

    matched_context = Column(Text)
    recommended_action = Column(Text)
    detected_in = Column(String(255))

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", back_populates="dlp_events")

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 100"),
        Index("idx_dlp_events_confidence", confidence.desc()),
    )

    def __repr__(self):
        return f"<DLPEvent(id={self.id}, data_type={self.data_type}, severity={self.severity})>"


# ============================================================================
# 7. SECURITY_EVENTS MODEL
# ============================================================================

class SecurityEvent(Base):
    """Security incidents and alerts"""
    __tablename__ = "security_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(EventSeverity), nullable=False, index=True)

    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("ai_applications.id", ondelete="SET NULL"), index=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp_tools.id", ondelete="SET NULL"), index=True)

    data_type = Column(String(100))

    source = Column(String(255))
    destination = Column(String(255))

    detection_method = Column(SQLEnum(DetectionMethod), index=True)
    risk_score = Column(Numeric(5, 2), default=0, index=True)

    action_taken = Column(SQLEnum(ActionTaken), default=ActionTaken.ALLOWED, nullable=False)
    status = Column(SQLEnum(EventStatus), default=EventStatus.OPEN, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", back_populates="security_events")
    application = relationship("AIApplication", back_populates="security_events")
    tool = relationship("MCPTool", back_populates="security_events")
    policy_actions = relationship("PolicyAction", back_populates="event")

    __table_args__ = (
        Index("idx_security_events_risk_score", risk_score.desc()),
        Index("idx_security_events_created_at", created_at.desc()),
    )

    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, event_type={self.event_type}, severity={self.severity})>"


# ============================================================================
# 8. POLICIES MODEL
# ============================================================================

class Policy(Base):
    """Security policies"""
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True, nullable=False, index=True)

    # Policy definition
    condition = Column(JSONB, nullable=False, default={})
    action = Column(SQLEnum(PolicyAction), nullable=False, index=True)

    # Priority: lower number = higher priority
    priority = Column(Integer, default=100, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="policies")
    policy_actions = relationship("PolicyAction", back_populates="policy")

    def __repr__(self):
        return f"<Policy(id={self.id}, name={self.name}, action={self.action})>"


# ============================================================================
# 9. POLICY_ACTIONS MODEL
# ============================================================================

class PolicyAction(Base):
    """Policy execution tracking"""
    __tablename__ = "policy_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False, index=True)

    action_taken = Column(String(100), nullable=False)
    executed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    policy = relationship("Policy", back_populates="policy_actions")
    event = relationship("SecurityEvent", back_populates="policy_actions")

    def __repr__(self):
        return f"<PolicyAction(id={self.id}, action={self.action_taken})>"


# ============================================================================
# 10. DESTINATIONS MODEL
# ============================================================================

class Destination(Base):
    """External destinations for agent communication"""
    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), nullable=False, index=True)
    url = Column(String(2048))

    # Risk Assessment
    risk_score = Column(Numeric(5, 2), default=0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)

    is_internal = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Destination(id={self.id}, name={self.name}, risk_level={self.risk_level})>"


# ============================================================================
# 11. RISK_ASSESSMENTS MODEL
# ============================================================================

class RiskAssessment(Base):
    """Risk assessment snapshots"""
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    entity_type = Column(SQLEnum(EntityType), nullable=False)

    # Generic entity reference
    application_id = Column(UUID(as_uuid=True), ForeignKey("ai_applications.id", ondelete="CASCADE"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp_tools.id", ondelete="CASCADE"), nullable=True)

    overall_score = Column(Numeric(5, 2), nullable=False, index=True)

    # Dimension scores
    dimensions = Column(JSONB, default={})

    explanation = Column(Text)
    key_concerns = Column(JSONB, default=[])
    recommended_controls = Column(JSONB, default=[])

    assessment_date = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    next_assessment_date = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    application = relationship("AIApplication", back_populates="risk_assessments")
    agent = relationship("AIAgent", back_populates="risk_assessments")
    tool = relationship("MCPTool", back_populates="risk_assessments")

    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 100"),
        CheckConstraint(
            "(entity_type = 'application' AND application_id IS NOT NULL) OR "
            "(entity_type = 'agent' AND agent_id IS NOT NULL) OR "
            "(entity_type = 'tool' AND tool_id IS NOT NULL)"
        ),
        Index("idx_risk_assessments_overall_score", overall_score.desc()),
    )

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, entity_type={self.entity_type}, score={self.overall_score})>"
