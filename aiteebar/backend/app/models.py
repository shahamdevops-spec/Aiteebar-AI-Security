"""
SQLAlchemy ORM models for Aiteebar AI Security database schema.
Corresponds to the PostgreSQL schema defined in database/schema.sql
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from sqlalchemy import (
    Column, String, DateTime, Boolean, Numeric, Text, Integer,
    ForeignKey, CheckConstraint, Index, Enum as SQLEnum, func
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import JSON

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


class PolicyAction(str, Enum):
    """Policy enforcement actions"""
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class SecurityEventType(str, Enum):
    """Categories of security events logged by the platform"""
    AGENT_TOOL_CONNECTION = "agent_tool_connection"
    DATA_ACCESS = "data_access"
    DLP_DETECTION = "dlp_detection"
    RISK_THRESHOLD_EXCEEDED = "risk_threshold_exceeded"
    POLICY_VIOLATION = "policy_violation"
    EXTERNAL_COMMUNICATION = "external_communication"
    THREAT_DETECTED = "threat_detected"
    BLOCK_ACTION_TAKEN = "block_action_taken"


class AlertStatus(str, Enum):
    """SOC alert triage state"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AlertDeliveryStatus(str, Enum):
    """Outbound delivery state for an alert"""
    NOT_ATTEMPTED = "not_attempted"
    DELIVERED = "delivered"
    FAILED = "failed"
    DISABLED = "disabled"


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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    enterprise_controls = Column(JSON, default={})
    data_residency = Column(String(100))
    authentication = Column(JSON, default={})

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("ai_applications.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255))
    environment = Column(String(100))

    # Risk Assessment
    risk_score = Column(Numeric(5, 2), default=0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)

    # Capabilities
    connected_tools = Column(JSON, default=[])
    data_access = Column(JSON, default={})

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    description = Column(Text)

    # Permissions as JSON array
    permissions = Column(JSON, default=[])

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_id = Column(String(36), ForeignKey("mcp_tools.id", ondelete="SET NULL"), index=True)

    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)

    resource_name = Column(String(255))
    status = Column(SQLEnum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False, index=True)

    risk_score = Column(Numeric(5, 2), default=0, index=True)

    # Detailed metadata
    agent_metadata = Column(JSON, default={})

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(EventSeverity), nullable=False, index=True)

    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="SET NULL"), index=True)
    application_id = Column(String(36), ForeignKey("ai_applications.id", ondelete="SET NULL"), index=True)
    tool_id = Column(String(36), ForeignKey("mcp_tools.id", ondelete="SET NULL"), index=True)

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
    policy_executions = relationship("PolicyExecution", back_populates="event")

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
    """Security policies for access control and data protection"""
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    enabled = Column(Boolean, default=True, nullable=False, index=True)

    # Policy definition - JSON with triggers and conditions
    condition = Column(JSON, nullable=False, default={})
    action = Column(SQLEnum(PolicyAction), nullable=False, index=True)

    # Priority: lower number = higher priority
    priority = Column(Integer, default=100, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="policies")
    policy_executions = relationship("PolicyExecution", back_populates="policy")

    __table_args__ = (
        Index("idx_policies_enabled_priority", enabled.desc(), priority.asc()),
    )

    def __repr__(self):
        return f"<Policy(id={self.id}, name={self.name}, action={self.action})>"


# ============================================================================
# 9. POLICY_EXECUTIONS MODEL
# ============================================================================

class PolicyExecution(Base):
    """Policy execution tracking and audit log"""
    __tablename__ = "policy_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String(36), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(String(36), ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False, index=True)

    action_taken = Column(SQLEnum(PolicyAction), nullable=False, index=True)
    executed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    # Audit details
    matched_conditions = Column(JSON, default={})
    reasoning = Column(Text)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    policy = relationship("Policy", back_populates="policy_executions")
    event = relationship("SecurityEvent", back_populates="policy_executions")

    __table_args__ = (
        Index("idx_policy_executions_executed_at", executed_at.desc()),
    )

    def __repr__(self):
        return f"<PolicyExecution(id={self.id}, policy_id={self.policy_id}, action={self.action_taken})>"


# ============================================================================
# 10. DESTINATIONS MODEL
# ============================================================================

class Destination(Base):
    """External destinations for agent communication"""
    __tablename__ = "destinations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    entity_type = Column(SQLEnum(EntityType), nullable=False)

    # Generic entity reference
    application_id = Column(String(36), ForeignKey("ai_applications.id", ondelete="CASCADE"), nullable=True)
    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=True)
    tool_id = Column(String(36), ForeignKey("mcp_tools.id", ondelete="CASCADE"), nullable=True)

    overall_score = Column(Numeric(5, 2), nullable=False, index=True)

    # Dimension scores
    dimensions = Column(JSON, default={})

    explanation = Column(Text)
    key_concerns = Column(JSON, default=[])
    recommended_controls = Column(JSON, default=[])

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


# ============================================================================
# 12. THREAT_DETECTIONS MODEL
# ============================================================================

class ThreatDetection(Base):
    """Threat detection results from rule-based engine"""
    __tablename__ = "threat_detections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    # Threat Classification
    threat_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(EventSeverity), default=EventSeverity.MEDIUM, nullable=False, index=True)

    risk_score = Column(Numeric(5, 2), default=0, index=True)
    confidence = Column(Numeric(5, 2), default=0)

    description = Column(Text, nullable=False)
    evidence = Column(JSON, default={})
    affected_resources = Column(JSON, default=[])

    recommended_action = Column(Text)
    resolved = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", backref="threat_detections")

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100"),
        CheckConstraint("confidence >= 0 AND confidence <= 100"),
        Index("idx_threat_detections_severity", severity.desc()),
        Index("idx_threat_detections_risk_score", risk_score.desc()),
        Index("idx_threat_detections_created_at", created_at.desc()),
    )

    def __repr__(self):
        return f"<ThreatDetection(id={self.id}, agent_id={self.agent_id}, threat_type={self.threat_type}, severity={self.severity})>"


# ============================================================================
# 13. ALERTS MODEL
# ============================================================================

class Alert(Base):
    """SOC alerts generated from security events, shaped for SIEM export"""
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    severity = Column(SQLEnum(EventSeverity), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    agent_id = Column(String(36), ForeignKey("ai_agents.id", ondelete="SET NULL"), index=True)
    application_id = Column(String(36), ForeignKey("ai_applications.id", ondelete="SET NULL"), index=True)

    # Entity state is copied in at generation time so the alert stays readable
    # after the agent or application row is modified or deleted.
    agent_snapshot = Column(JSON, default={})
    application_snapshot = Column(JSON, default={})

    data_type = Column(String(100), index=True)
    destination = Column(String(255))
    risk_score = Column(Numeric(5, 2), default=0, index=True)
    action_taken = Column(SQLEnum(ActionTaken), nullable=False)

    source = Column(SQLEnum(DetectionMethod), nullable=False, index=True)
    event_ids = Column(JSON, default=[])

    # MITRE ATLAS techniques, resolved when the alert is generated and frozen
    # alongside the entity snapshots. Freezing matters: if the mapping table is
    # later revised, a historical alert should still show what was asserted at
    # the time it was raised.
    atlas_techniques = Column(JSON, default=[])

    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, nullable=False, index=True)
    acknowledged_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    acknowledged_at = Column(DateTime(timezone=True))

    delivery_status = Column(
        SQLEnum(AlertDeliveryStatus),
        default=AlertDeliveryStatus.NOT_ATTEMPTED,
        nullable=False,
    )
    delivery_error = Column(Text)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    agent = relationship("AIAgent", backref="alerts")
    application = relationship("AIApplication", backref="alerts")

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100"),
        Index("idx_alerts_severity_status", severity, status),
        Index("idx_alerts_timestamp", timestamp.desc()),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, severity={self.severity}, title={self.title})>"
