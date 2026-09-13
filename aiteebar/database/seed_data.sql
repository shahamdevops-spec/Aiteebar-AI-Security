-- ============================================================================
-- AITEEBAR AI SECURITY - SEED DATA
-- Development and demo data for testing
-- ============================================================================

-- Insert demo users
INSERT INTO users (id, email, password_hash, name, role) VALUES
('550e8400-e29b-41d4-a716-446655440001'::uuid, 'admin@aiteebar.local', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Admin User', 'admin'),
('550e8400-e29b-41d4-a716-446655440002'::uuid, 'analyst@aiteebar.local', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Security Analyst', 'analyst'),
('550e8400-e29b-41d4-a716-446655440003'::uuid, 'viewer@aiteebar.local', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Report Viewer', 'viewer')
ON CONFLICT (email) DO NOTHING;

-- Insert demo AI applications
INSERT INTO ai_applications (
    id, name, vendor, category, description,
    risk_score, risk_level,
    privacy_score, security_score, data_handling_score,
    enterprise_control_score, integration_score, permission_score,
    mcp_support, api_available, is_demo
) VALUES
-- ChatGPT
('550e8400-e29b-41d4-a716-446655450001'::uuid,
 'ChatGPT',
 'OpenAI',
 'General Purpose LLM',
 'Large language model for various tasks including code generation and analysis',
 75.0, 'HIGH',
 65.0, 70.0, 80.0, 50.0, 85.0, 60.0,
 true, true, true),

-- Claude
('550e8400-e29b-41d4-a716-446655450002'::uuid,
 'Claude',
 'Anthropic',
 'General Purpose LLM',
 'AI assistant with focus on safety and reliability',
 35.0, 'LOW',
 85.0, 90.0, 92.0, 80.0, 75.0, 88.0,
 true, true, true),

-- Gemini
('550e8400-e29b-41d4-a716-446655450003'::uuid,
 'Gemini',
 'Google',
 'General Purpose LLM',
 'Multimodal AI model with advanced reasoning',
 65.0, 'MEDIUM',
 70.0, 75.0, 72.0, 70.0, 80.0, 75.0,
 true, true, true),

-- Internal Chat System
('550e8400-e29b-41d4-a716-446655450004'::uuid,
 'Internal Chat Assistant',
 'Acme Corp',
 'Enterprise LLM',
 'On-premise AI assistant for internal use',
 45.0, 'MEDIUM',
 92.0, 95.0, 97.0, 95.0, 50.0, 92.0,
 true, false, true);

-- Insert demo AI agents
INSERT INTO ai_agents (id, application_id, name, owner, environment, risk_score, risk_level, status) VALUES
('550e8400-e29b-41d4-a716-446655460001'::uuid,
 '550e8400-e29b-41d4-a716-446655450001'::uuid,
 'ChatGPT Production',
 'engineering@acme.com',
 'production',
 78.0, 'HIGH', 'active'),

('550e8400-e29b-41d4-a716-446655460002'::uuid,
 '550e8400-e29b-41d4-a716-446655450002'::uuid,
 'Claude Dev Environment',
 'dev@acme.com',
 'development',
 25.0, 'LOW', 'active'),

('550e8400-e29b-41d4-a716-446655460003'::uuid,
 '550e8400-e29b-41d4-a716-446655450004'::uuid,
 'Internal Chat - Customer Support',
 'support@acme.com',
 'production',
 40.0, 'MEDIUM', 'active');

-- Insert demo MCP tools
INSERT INTO mcp_tools (id, agent_id, name, type, permissions, data_sensitivity, risk_score, status) VALUES
-- ChatGPT tools
('550e8400-e29b-41d4-a716-446655470001'::uuid,
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 'Code Interpreter',
 'execution',
 '["read", "write", "execute"]'::jsonb,
 'HIGH', 85.0, 'active'),

('550e8400-e29b-41d4-a716-446655470002'::uuid,
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 'Web Browsing',
 'api',
 '["read"]'::jsonb,
 'MEDIUM', 65.0, 'active'),

('550e8400-e29b-41d4-a716-446655470003'::uuid,
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 'File Upload/Download',
 'file',
 '["read", "write"]'::jsonb,
 'CRITICAL', 90.0, 'active'),

-- Claude tools
('550e8400-e29b-41d4-a716-446655470004'::uuid,
 '550e8400-e29b-41d4-a716-446655460002'::uuid,
 'Read Files',
 'file',
 '["read"]'::jsonb,
 'HIGH', 40.0, 'active'),

-- Internal Chat tools
('550e8400-e29b-41d4-a716-446655470005'::uuid,
 '550e8400-e29b-41d4-a716-446655460003'::uuid,
 'Database Query Tool',
 'database',
 '["read"]'::jsonb,
 'CRITICAL', 50.0, 'active'),

('550e8400-e29b-41d4-a716-446655470006'::uuid,
 '550e8400-e29b-41d4-a716-446655460003'::uuid,
 'Email Notification',
 'api',
 '["write"]'::jsonb,
 'HIGH', 45.0, 'active');

-- Insert demo security events
INSERT INTO security_events (
    id, event_type, severity, agent_id, tool_id,
    source, destination, detection_method, risk_score,
    action_taken, status
) VALUES
('550e8400-e29b-41d4-a716-446655480001'::uuid,
 'EXTERNAL_API_CALL',
 'HIGH',
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 '550e8400-e29b-41d4-a716-446655470002'::uuid,
 'agent:chatgpt-prod',
 'https://api.example.com/data',
 'policy_engine', 75.0,
 'WARNED', 'acknowledged'),

('550e8400-e29b-41d4-a716-446655480002'::uuid,
 'DATA_ACCESS',
 'CRITICAL',
 '550e8400-e29b-41d4-a716-446655460003'::uuid,
 '550e8400-e29b-41d4-a716-446655470005'::uuid,
 'agent:internal-chat',
 'database:customer_data',
 'policy_engine', 85.0,
 'APPROVAL_REQUIRED', 'open'),

('550e8400-e29b-41d4-a716-446655480003'::uuid,
 'FILE_UPLOAD',
 'MEDIUM',
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 '550e8400-e29b-41d4-a716-446655470003'::uuid,
 'agent:chatgpt-prod',
 'file:uploaded_docs',
 'dlp', 55.0,
 'ALLOWED', 'resolved');

-- Insert demo DLP events
INSERT INTO dlp_events (id, agent_id, data_type, confidence, severity, detected_in) VALUES
('550e8400-e29b-41d4-a716-446655490001'::uuid,
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 'EMAIL',
 95.0, 'HIGH',
 'Code Interpreter'),

('550e8400-e29b-41d4-a716-446655490002'::uuid,
 '550e8400-e29b-41d4-a716-446655460001'::uuid,
 'IBAN',
 87.0, 'CRITICAL',
 'Web Browsing'),

('550e8400-e29b-41d4-a716-446655490003'::uuid,
 '550e8400-e29b-41d4-a716-446655460003'::uuid,
 'PHONE',
 92.0, 'HIGH',
 'Database Query Tool');

-- Insert demo destinations
INSERT INTO destinations (id, name, url, risk_score, risk_level, is_internal) VALUES
('550e8400-e29b-41d4-a716-446655500001'::uuid,
 'Customer Data API',
 'https://api.internal.acme.com/customers',
 60.0, 'MEDIUM', true),

('550e8400-e29b-41d4-a716-446655500002'::uuid,
 'Third-party Analytics',
 'https://analytics.external.com/events',
 80.0, 'HIGH', false),

('550e8400-e29b-41d4-a716-446655500003'::uuid,
 'Email Service',
 'https://smtp.internal.acme.com',
 45.0, 'MEDIUM', true);

-- Insert demo risk assessments
INSERT INTO risk_assessments (
    id, entity_type, application_id,
    overall_score, explanation
) VALUES
('550e8400-e29b-41d4-a716-446655510001'::uuid,
 'application',
 '550e8400-e29b-41d4-a716-446655450001'::uuid,
 75.0,
 'ChatGPT carries high risk due to external data handling and complex tool integration'),

('550e8400-e29b-41d4-a716-446655510002'::uuid,
 'application',
 '550e8400-e29b-41d4-a716-446655450002'::uuid,
 35.0,
 'Claude has strong privacy and security controls with good data handling practices'),

('550e8400-e29b-41d4-a716-446655510003'::uuid,
 'application',
 '550e8400-e29b-41d4-a716-446655450004'::uuid,
 45.0,
 'Internal chat system has good controls but limited tool integration');

-- Insert demo policies
INSERT INTO policies (id, created_by, name, action, priority, enabled) VALUES
('550e8400-e29b-41d4-a716-446655520001'::uuid,
 '550e8400-e29b-41d4-a716-446655440001'::uuid,
 'Block External API Calls to Unknown Services',
 'BLOCK',
 10,
 true),

('550e8400-e29b-41d4-a716-446655520002'::uuid,
 '550e8400-e29b-41d4-a716-446655440001'::uuid,
 'Warn on Customer Data Access',
 'WARN',
 20,
 true),

('550e8400-e29b-41d4-a716-446655520003'::uuid,
 '550e8400-e29b-41d4-a716-446655440001'::uuid,
 'Require Approval for File Uploads',
 'REQUIRE_APPROVAL',
 15,
 true);

-- Insert demo policy actions
INSERT INTO policy_actions (id, policy_id, event_id, action_taken, executed_at) VALUES
('550e8400-e29b-41d4-a716-446655530001'::uuid,
 '550e8400-e29b-41d4-a716-446655520002'::uuid,
 '550e8400-e29b-41d4-a716-446655480002'::uuid,
 'APPROVAL_REQUIRED',
 CURRENT_TIMESTAMP - INTERVAL '2 hours');

-- ============================================================================
-- SUMMARY OF INSERTED DATA:
-- ============================================================================
-- Users: 3 (admin, analyst, viewer)
-- Applications: 4 (ChatGPT, Claude, Gemini, Internal Chat)
-- Agents: 3 (ChatGPT Prod, Claude Dev, Internal Chat)
-- Tools: 6 (various capabilities)
-- Security Events: 3
-- DLP Events: 3
-- Destinations: 3
-- Risk Assessments: 3
-- Policies: 3
-- Policy Actions: 1
