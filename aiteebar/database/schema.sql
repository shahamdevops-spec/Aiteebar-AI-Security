-- ============================================================================
-- AITEEBAR AI SECURITY - PostgreSQL Database Schema
-- ============================================================================
-- Comprehensive schema for AI security analysis, threat detection, and
-- risk assessment platform with MCP tool integration support
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
-- User accounts with role-based access control
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'analyst', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

COMMENT ON TABLE users IS 'User accounts with role-based access control (admin, analyst, viewer)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.role IS 'User role: admin (full access), analyst (can create scans), viewer (read-only)';

-- ============================================================================
-- 2. AI_APPLICATIONS TABLE
-- ============================================================================
-- AI applications and services being assessed
CREATE TABLE ai_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    vendor VARCHAR(255),
    category VARCHAR(100),
    description TEXT,

    -- Risk Scores (0-100 scale)
    risk_score NUMERIC(5,2) DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    -- Dimension Scores (0-100 scale)
    privacy_score NUMERIC(5,2),
    security_score NUMERIC(5,2),
    data_handling_score NUMERIC(5,2),
    enterprise_control_score NUMERIC(5,2),
    integration_score NUMERIC(5,2),
    permission_score NUMERIC(5,2),

    -- Capabilities and Features
    mcp_support BOOLEAN DEFAULT false,
    api_available BOOLEAN DEFAULT false,
    enterprise_controls JSONB DEFAULT '{}',
    data_residency VARCHAR(100),
    authentication JSONB DEFAULT '{}',

    -- Additional Info
    notes TEXT,
    is_demo BOOLEAN DEFAULT false,
    last_assessed TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_applications_name ON ai_applications(name);
CREATE INDEX idx_ai_applications_vendor ON ai_applications(vendor);
CREATE INDEX idx_ai_applications_risk_level ON ai_applications(risk_level);
CREATE INDEX idx_ai_applications_risk_score ON ai_applications(risk_score DESC);
CREATE INDEX idx_ai_applications_is_demo ON ai_applications(is_demo);
CREATE INDEX idx_ai_applications_mcp_support ON ai_applications(mcp_support);

COMMENT ON TABLE ai_applications IS 'AI applications and services being assessed for security';
COMMENT ON COLUMN ai_applications.risk_score IS 'Overall risk score (0-100), calculated from dimension scores';
COMMENT ON COLUMN ai_applications.enterprise_controls IS 'JSON array of available enterprise security controls';
COMMENT ON COLUMN ai_applications.is_demo IS 'Flag for illustrative/demo assessments';

-- ============================================================================
-- 3. AI_AGENTS TABLE
-- ============================================================================
-- AI agents deployed from applications
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES ai_applications(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    owner VARCHAR(255),
    environment VARCHAR(100),

    -- Risk Assessment
    risk_score NUMERIC(5,2) DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    -- Capabilities
    connected_tools JSONB DEFAULT '[]',
    data_access JSONB DEFAULT '{}',

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    last_activity TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_agents_application_id ON ai_agents(application_id);
CREATE INDEX idx_ai_agents_status ON ai_agents(status);
CREATE INDEX idx_ai_agents_risk_level ON ai_agents(risk_level);
CREATE INDEX idx_ai_agents_name ON ai_agents(name);
CREATE INDEX idx_ai_agents_last_activity ON ai_agents(last_activity);

COMMENT ON TABLE ai_agents IS 'AI agents deployed from applications with independent risk profiles';
COMMENT ON COLUMN ai_agents.connected_tools IS 'JSON array of connected MCP tools and their configurations';
COMMENT ON COLUMN ai_agents.data_access IS 'JSON object describing data access patterns and permissions';

-- ============================================================================
-- 4. MCP_TOOLS TABLE
-- ============================================================================
-- MCP (Model Context Protocol) tools used by agents
CREATE TABLE mcp_tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,

    -- Permissions as JSON array: ["read", "write", "execute"]
    permissions JSONB DEFAULT '[]',

    -- Data Sensitivity
    data_sensitivity VARCHAR(20) DEFAULT 'LOW' CHECK (data_sensitivity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    -- Risk Assessment
    risk_score NUMERIC(5,2) DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mcp_tools_agent_id ON mcp_tools(agent_id);
CREATE INDEX idx_mcp_tools_name ON mcp_tools(name);
CREATE INDEX idx_mcp_tools_type ON mcp_tools(type);
CREATE INDEX idx_mcp_tools_data_sensitivity ON mcp_tools(data_sensitivity);
CREATE INDEX idx_mcp_tools_status ON mcp_tools(status);

COMMENT ON TABLE mcp_tools IS 'MCP tools integrated with agents for specific capabilities';
COMMENT ON COLUMN mcp_tools.permissions IS 'JSON array of permissions: ["read", "write", "execute"]';

-- ============================================================================
-- 5. AGENT_ACTIVITY TABLE
-- ============================================================================
-- Log of agent actions and activities
CREATE TABLE agent_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    tool_id UUID REFERENCES mcp_tools(id) ON DELETE SET NULL,

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('CONNECT', 'READ', 'WRITE', 'EXECUTE', 'EXTERNAL_CALL')),

    resource_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'blocked')),

    risk_score NUMERIC(5,2) DEFAULT 0,

    -- Detailed metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_activity_agent_id ON agent_activity(agent_id);
CREATE INDEX idx_agent_activity_tool_id ON agent_activity(tool_id);
CREATE INDEX idx_agent_activity_timestamp ON agent_activity(timestamp DESC);
CREATE INDEX idx_agent_activity_action_type ON agent_activity(action_type);
CREATE INDEX idx_agent_activity_status ON agent_activity(status);
CREATE INDEX idx_agent_activity_risk_score ON agent_activity(risk_score DESC);

COMMENT ON TABLE agent_activity IS 'Detailed log of all agent actions and activities';
COMMENT ON COLUMN agent_activity.action_type IS 'Type of action: CONNECT (tool connection), READ (data read), WRITE (data write), EXECUTE (command execution), EXTERNAL_CALL (external API call)';
COMMENT ON COLUMN agent_activity.metadata IS 'JSON with additional context: request details, response summaries, error messages';

-- ============================================================================
-- 6. DLP_EVENTS TABLE
-- ============================================================================
-- Data Loss Prevention events - sensitive data detection
CREATE TABLE dlp_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Data Type Detection
    data_type VARCHAR(100) NOT NULL CHECK (data_type IN (
        'CNIC', 'IBAN', 'EMAIL', 'PHONE', 'API_KEY', 'PASSWORD',
        'CREDIT_CARD', 'SSN', 'PASSPORT', 'HEALTH_RECORD', 'OTHER'
    )),

    confidence NUMERIC(5,2) CHECK (confidence >= 0 AND confidence <= 100),
    severity VARCHAR(20) DEFAULT 'MEDIUM' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    matched_context TEXT,
    recommended_action TEXT,
    detected_in VARCHAR(255),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dlp_events_agent_id ON dlp_events(agent_id);
CREATE INDEX idx_dlp_events_timestamp ON dlp_events(timestamp DESC);
CREATE INDEX idx_dlp_events_data_type ON dlp_events(data_type);
CREATE INDEX idx_dlp_events_severity ON dlp_events(severity);
CREATE INDEX idx_dlp_events_confidence ON dlp_events(confidence DESC);

COMMENT ON TABLE dlp_events IS 'Data Loss Prevention events - sensitive data detected in agent communications';
COMMENT ON COLUMN dlp_events.data_type IS 'Type of sensitive data detected: CNIC, IBAN, EMAIL, PHONE, API_KEY, PASSWORD, etc.';
COMMENT ON COLUMN dlp_events.matched_context IS 'The actual text/pattern that matched the DLP rule (may be redacted)';

-- ============================================================================
-- 7. SECURITY_EVENTS TABLE
-- ============================================================================
-- Security incidents and alerts
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    agent_id UUID REFERENCES ai_agents(id) ON DELETE SET NULL,
    application_id UUID REFERENCES ai_applications(id) ON DELETE SET NULL,
    tool_id UUID REFERENCES mcp_tools(id) ON DELETE SET NULL,

    data_type VARCHAR(100),

    source VARCHAR(255),
    destination VARCHAR(255),

    detection_method VARCHAR(100) CHECK (detection_method IN ('policy_engine', 'dlp', 'threat_detection', 'manual', 'other')),
    risk_score NUMERIC(5,2) DEFAULT 0,

    action_taken VARCHAR(100) DEFAULT 'ALLOWED' CHECK (action_taken IN ('ALLOWED', 'WARNED', 'APPROVAL_REQUIRED', 'BLOCKED')),
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_agent_id ON security_events(agent_id);
CREATE INDEX idx_security_events_application_id ON security_events(application_id);
CREATE INDEX idx_security_events_tool_id ON security_events(tool_id);
CREATE INDEX idx_security_events_status ON security_events(status);
CREATE INDEX idx_security_events_detection_method ON security_events(detection_method);
CREATE INDEX idx_security_events_created_at ON security_events(created_at DESC);
CREATE INDEX idx_security_events_risk_score ON security_events(risk_score DESC);

COMMENT ON TABLE security_events IS 'Security incidents and alerts triggered by policies or threat detection';
COMMENT ON COLUMN security_events.event_type IS 'Category of security event: DATA_EXFILTRATION, UNAUTHORIZED_ACCESS, POLICY_VIOLATION, etc.';
COMMENT ON COLUMN security_events.detection_method IS 'How the event was detected: policy_engine, dlp, threat_detection, manual review';

-- ============================================================================
-- 8. POLICIES TABLE
-- ============================================================================
-- Security policies defining rules and actions
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

    name VARCHAR(255) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT true,

    -- Policy conditions and actions
    condition JSONB NOT NULL DEFAULT '{}',
    action VARCHAR(100) NOT NULL CHECK (action IN ('ALLOW', 'WARN', 'REQUIRE_APPROVAL', 'BLOCK')),

    -- Priority: lower number = higher priority
    priority INTEGER DEFAULT 100,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_created_by ON policies(created_by);
CREATE INDEX idx_policies_enabled ON policies(enabled);
CREATE INDEX idx_policies_priority ON policies(priority ASC);
CREATE INDEX idx_policies_action ON policies(action);

COMMENT ON TABLE policies IS 'Security policies defining rules for agent behavior and data access';
COMMENT ON COLUMN policies.condition IS 'JSON object defining policy conditions (if/then rules)';
COMMENT ON COLUMN policies.priority IS 'Priority for policy evaluation (lower number = higher priority, evaluated first)';

-- ============================================================================
-- 9. POLICY_ACTIONS TABLE
-- ============================================================================
-- Tracking of policy executions
CREATE TABLE policy_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_id UUID NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES security_events(id) ON DELETE CASCADE,

    action_taken VARCHAR(100) NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_actions_policy_id ON policy_actions(policy_id);
CREATE INDEX idx_policy_actions_event_id ON policy_actions(event_id);
CREATE INDEX idx_policy_actions_executed_at ON policy_actions(executed_at DESC);

COMMENT ON TABLE policy_actions IS 'Audit trail of policy executions and their effects';

-- ============================================================================
-- 10. DESTINATIONS TABLE
-- ============================================================================
-- External destinations that agents communicate with
CREATE TABLE destinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name VARCHAR(255) NOT NULL,
    url VARCHAR(2048),

    -- Risk Assessment
    risk_score NUMERIC(5,2) DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    is_internal BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_destinations_name ON destinations(name);
CREATE INDEX idx_destinations_is_internal ON destinations(is_internal);
CREATE INDEX idx_destinations_risk_level ON destinations(risk_level);

COMMENT ON TABLE destinations IS 'External services and APIs that agents connect to';

-- ============================================================================
-- 11. RISK_ASSESSMENTS TABLE
-- ============================================================================
-- Risk assessment snapshots for entities
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('application', 'agent', 'tool')),
    entity_id UUID NOT NULL,

    overall_score NUMERIC(5,2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),

    -- Dimension scores as JSON
    dimensions JSONB DEFAULT '{}',

    explanation TEXT,
    key_concerns JSONB DEFAULT '[]',
    recommended_controls JSONB DEFAULT '[]',

    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    next_assessment_date TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_assessments_entity_type_id ON risk_assessments(entity_type, entity_id);
CREATE INDEX idx_risk_assessments_overall_score ON risk_assessments(overall_score DESC);
CREATE INDEX idx_risk_assessments_assessment_date ON risk_assessments(assessment_date DESC);

COMMENT ON TABLE risk_assessments IS 'Risk assessment snapshots for applications, agents, and tools';
COMMENT ON COLUMN risk_assessments.dimensions IS 'JSON object with dimension scores: {privacy, security, data_handling, etc.}';
COMMENT ON COLUMN risk_assessments.key_concerns IS 'JSON array of identified security concerns';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Recent Security Events with full context
CREATE OR REPLACE VIEW vw_security_events_full AS
SELECT
    se.id,
    se.event_type,
    se.severity,
    se.action_taken,
    se.status,
    se.detection_method,
    se.risk_score,
    se.created_at,
    -- Application context
    aa.name AS application_name,
    -- Agent context
    ag.name AS agent_name,
    -- Tool context
    mt.name AS tool_name,
    -- DLP context
    CASE WHEN se.data_type IS NOT NULL THEN se.data_type ELSE 'N/A' END AS data_type
FROM security_events se
LEFT JOIN ai_applications aa ON se.application_id = aa.id
LEFT JOIN ai_agents ag ON se.agent_id = ag.id
LEFT JOIN mcp_tools mt ON se.tool_id = mt.id
ORDER BY se.created_at DESC;

COMMENT ON VIEW vw_security_events_full IS 'Security events with full context from related tables';

-- View: High-Risk Agents with recent activity
CREATE OR REPLACE VIEW vw_high_risk_agents AS
SELECT
    ag.id,
    ag.name,
    ag.status,
    ag.risk_score,
    ag.risk_level,
    aa.name AS application_name,
    COUNT(aa_rec.id) AS recent_activities_24h,
    COUNT(se.id) AS recent_events_24h,
    ag.last_activity
FROM ai_agents ag
JOIN ai_applications aa ON ag.application_id = aa.id
LEFT JOIN agent_activity aa_rec ON ag.id = aa_rec.agent_id AND aa_rec.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
LEFT JOIN security_events se ON ag.id = se.agent_id AND se.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
WHERE ag.risk_level IN ('HIGH', 'CRITICAL')
GROUP BY ag.id, ag.name, ag.status, ag.risk_score, ag.risk_level, aa.name, ag.last_activity
ORDER BY ag.risk_score DESC;

COMMENT ON VIEW vw_high_risk_agents IS 'High-risk agents with recent activity counts for dashboard';

-- View: Policy Effectiveness Report
CREATE OR REPLACE VIEW vw_policy_effectiveness AS
SELECT
    p.id,
    p.name,
    p.action,
    p.enabled,
    COUNT(pa.id) AS total_executions,
    COUNT(CASE WHEN pa.action_taken = p.action THEN 1 END) AS successful_executions,
    ROUND(
        COUNT(CASE WHEN pa.action_taken = p.action THEN 1 END)::NUMERIC /
        NULLIF(COUNT(pa.id), 0) * 100,
        2
    ) AS effectiveness_percentage
FROM policies p
LEFT JOIN policy_actions pa ON p.id = pa.policy_id
WHERE p.enabled = true
GROUP BY p.id, p.name, p.action, p.enabled
ORDER BY effectiveness_percentage DESC NULLS LAST;

COMMENT ON VIEW vw_policy_effectiveness IS 'Policy effectiveness metrics for optimization';

-- View: DLP Incident Summary by Data Type
CREATE OR REPLACE VIEW vw_dlp_summary AS
SELECT
    data_type,
    severity,
    COUNT(*) AS incident_count,
    ROUND(AVG(confidence), 2) AS avg_confidence,
    MAX(timestamp) AS latest_incident
FROM dlp_events
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY data_type, severity
ORDER BY incident_count DESC;

COMMENT ON VIEW vw_dlp_summary IS 'Summary of DLP incidents by data type and severity';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_applications_updated_at BEFORE UPDATE ON ai_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_agents_updated_at BEFORE UPDATE ON ai_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_tools_updated_at BEFORE UPDATE ON mcp_tools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_security_events_updated_at BEFORE UPDATE ON security_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_destinations_updated_at BEFORE UPDATE ON destinations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column() IS 'Function to automatically update the updated_at timestamp on record modification';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
