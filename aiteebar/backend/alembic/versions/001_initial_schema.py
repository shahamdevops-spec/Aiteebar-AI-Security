"""Initial schema creation - all tables and indexes

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema with all tables"""

    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "hstore"')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='viewer'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("role IN ('admin', 'analyst', 'viewer')"),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])

    # Create ai_applications table
    op.create_table(
        'ai_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('vendor', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('risk_level', sa.String(20), nullable=False, server_default='LOW'),
        sa.Column('privacy_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('security_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('data_handling_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('enterprise_control_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('integration_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('permission_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('mcp_support', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('api_available', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('enterprise_controls', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('data_residency', sa.String(100), nullable=True),
        sa.Column('authentication', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('last_assessed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('risk_score >= 0 AND risk_score <= 100'),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_applications_name', 'ai_applications', ['name'])
    op.create_index('idx_ai_applications_vendor', 'ai_applications', ['vendor'])
    op.create_index('idx_ai_applications_risk_level', 'ai_applications', ['risk_level'])
    op.create_index('idx_ai_applications_risk_score', 'ai_applications', ['risk_score'], unique=False, postgresql_ops={'risk_score': 'DESC'})
    op.create_index('idx_ai_applications_is_demo', 'ai_applications', ['is_demo'])
    op.create_index('idx_ai_applications_mcp_support', 'ai_applications', ['mcp_support'])

    # Create ai_agents table
    op.create_table(
        'ai_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('environment', sa.String(100), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('risk_level', sa.String(20), nullable=False, server_default='LOW'),
        sa.Column('connected_tools', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('data_access', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.CheckConstraint("status IN ('active', 'inactive', 'suspended')"),
        sa.ForeignKeyConstraint(['application_id'], ['ai_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_agents_application_id', 'ai_agents', ['application_id'])
    op.create_index('idx_ai_agents_status', 'ai_agents', ['status'])
    op.create_index('idx_ai_agents_risk_level', 'ai_agents', ['risk_level'])
    op.create_index('idx_ai_agents_name', 'ai_agents', ['name'])
    op.create_index('idx_ai_agents_last_activity', 'ai_agents', ['last_activity'])

    # Create mcp_tools table
    op.create_table(
        'mcp_tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('data_sensitivity', sa.String(20), nullable=False, server_default='LOW'),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("data_sensitivity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.CheckConstraint("status IN ('active', 'inactive')"),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_mcp_tools_agent_id', 'mcp_tools', ['agent_id'])
    op.create_index('idx_mcp_tools_name', 'mcp_tools', ['name'])
    op.create_index('idx_mcp_tools_type', 'mcp_tools', ['type'])
    op.create_index('idx_mcp_tools_data_sensitivity', 'mcp_tools', ['data_sensitivity'])
    op.create_index('idx_mcp_tools_status', 'mcp_tools', ['status'])

    # Create agent_activity table
    op.create_table(
        'agent_activity',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("action_type IN ('CONNECT', 'READ', 'WRITE', 'EXECUTE', 'EXTERNAL_CALL')"),
        sa.CheckConstraint("status IN ('pending', 'executed', 'blocked')"),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['mcp_tools.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_activity_agent_id', 'agent_activity', ['agent_id'])
    op.create_index('idx_agent_activity_tool_id', 'agent_activity', ['tool_id'])
    op.create_index('idx_agent_activity_timestamp', 'agent_activity', ['timestamp'], unique=False, postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_agent_activity_action_type', 'agent_activity', ['action_type'])
    op.create_index('idx_agent_activity_status', 'agent_activity', ['status'])
    op.create_index('idx_agent_activity_risk_score', 'agent_activity', ['risk_score'], unique=False, postgresql_ops={'risk_score': 'DESC'})

    # Create dlp_events table
    op.create_table(
        'dlp_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('data_type', sa.String(100), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('matched_context', sa.Text(), nullable=True),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('detected_in', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("data_type IN ('CNIC', 'IBAN', 'EMAIL', 'PHONE', 'API_KEY', 'PASSWORD', 'CREDIT_CARD', 'SSN', 'PASSPORT', 'HEALTH_RECORD', 'OTHER')"),
        sa.CheckConstraint('confidence >= 0 AND confidence <= 100'),
        sa.CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dlp_events_agent_id', 'dlp_events', ['agent_id'])
    op.create_index('idx_dlp_events_timestamp', 'dlp_events', ['timestamp'], unique=False, postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_dlp_events_data_type', 'dlp_events', ['data_type'])
    op.create_index('idx_dlp_events_severity', 'dlp_events', ['severity'])
    op.create_index('idx_dlp_events_confidence', 'dlp_events', ['confidence'], unique=False, postgresql_ops={'confidence': 'DESC'})

    # Create security_events table
    op.create_table(
        'security_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('data_type', sa.String(100), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('destination', sa.String(255), nullable=True),
        sa.Column('detection_method', sa.String(100), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('action_taken', sa.String(100), nullable=False, server_default='ALLOWED'),
        sa.Column('status', sa.String(50), nullable=False, server_default='open'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.CheckConstraint("detection_method IN ('policy_engine', 'dlp', 'threat_detection', 'manual', 'other')"),
        sa.CheckConstraint("action_taken IN ('ALLOWED', 'WARNED', 'APPROVAL_REQUIRED', 'BLOCKED')"),
        sa.CheckConstraint("status IN ('open', 'acknowledged', 'resolved')"),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['application_id'], ['ai_applications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tool_id'], ['mcp_tools.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_security_events_event_type', 'security_events', ['event_type'])
    op.create_index('idx_security_events_severity', 'security_events', ['severity'])
    op.create_index('idx_security_events_agent_id', 'security_events', ['agent_id'])
    op.create_index('idx_security_events_application_id', 'security_events', ['application_id'])
    op.create_index('idx_security_events_tool_id', 'security_events', ['tool_id'])
    op.create_index('idx_security_events_status', 'security_events', ['status'])
    op.create_index('idx_security_events_detection_method', 'security_events', ['detection_method'])
    op.create_index('idx_security_events_created_at', 'security_events', ['created_at'], unique=False, postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_security_events_risk_score', 'security_events', ['risk_score'], unique=False, postgresql_ops={'risk_score': 'DESC'})

    # Create policies table
    op.create_table(
        'policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('condition', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("action IN ('ALLOW', 'WARN', 'REQUIRE_APPROVAL', 'BLOCK')"),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_policies_created_by', 'policies', ['created_by'])
    op.create_index('idx_policies_enabled', 'policies', ['enabled'])
    op.create_index('idx_policies_priority', 'policies', ['priority'])
    op.create_index('idx_policies_action', 'policies', ['action'])

    # Create policy_actions table
    op.create_table(
        'policy_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_taken', sa.String(100), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['event_id'], ['security_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_policy_actions_event_id', 'policy_actions', ['event_id'])
    op.create_index('idx_policy_actions_executed_at', 'policy_actions', ['executed_at'], unique=False, postgresql_ops={'executed_at': 'DESC'})
    op.create_index('idx_policy_actions_policy_id', 'policy_actions', ['policy_id'])

    # Create destinations table
    op.create_table(
        'destinations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(2048), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0'),
        sa.Column('risk_level', sa.String(20), nullable=False, server_default='LOW'),
        sa.Column('is_internal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_destinations_is_internal', 'destinations', ['is_internal'])
    op.create_index('idx_destinations_name', 'destinations', ['name'])
    op.create_index('idx_destinations_risk_level', 'destinations', ['risk_level'])

    # Create risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('overall_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('key_concerns', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('recommended_controls', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('assessment_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('next_assessment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('overall_score >= 0 AND overall_score <= 100'),
        sa.CheckConstraint("entity_type IN ('application', 'agent', 'tool')"),
        sa.CheckConstraint(
            "(entity_type = 'application' AND application_id IS NOT NULL) OR "
            "(entity_type = 'agent' AND agent_id IS NOT NULL) OR "
            "(entity_type = 'tool' AND tool_id IS NOT NULL)"
        ),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['application_id'], ['ai_applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['mcp_tools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_risk_assessments_overall_score', 'risk_assessments', ['overall_score'], unique=False, postgresql_ops={'overall_score': 'DESC'})
    op.create_index('idx_risk_assessments_assessment_date', 'risk_assessments', ['assessment_date'], unique=False, postgresql_ops={'assessment_date': 'DESC'})
    op.create_index('idx_risk_assessments_entity_type_id', 'risk_assessments', ['entity_type', 'application_id', 'agent_id', 'tool_id'])


def downgrade() -> None:
    """Drop all tables (reverse of upgrade)"""

    # Drop tables in reverse order of creation (respecting foreign keys)
    op.drop_index('idx_risk_assessments_entity_type_id', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_assessment_date', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_overall_score', table_name='risk_assessments')
    op.drop_table('risk_assessments')

    op.drop_index('idx_destinations_risk_level', table_name='destinations')
    op.drop_index('idx_destinations_name', table_name='destinations')
    op.drop_index('idx_destinations_is_internal', table_name='destinations')
    op.drop_table('destinations')

    op.drop_index('idx_policy_actions_policy_id', table_name='policy_actions')
    op.drop_index('idx_policy_actions_executed_at', table_name='policy_actions')
    op.drop_index('idx_policy_actions_event_id', table_name='policy_actions')
    op.drop_table('policy_actions')

    op.drop_index('idx_policies_action', table_name='policies')
    op.drop_index('idx_policies_priority', table_name='policies')
    op.drop_index('idx_policies_enabled', table_name='policies')
    op.drop_index('idx_policies_created_by', table_name='policies')
    op.drop_table('policies')

    op.drop_index('idx_security_events_risk_score', table_name='security_events')
    op.drop_index('idx_security_events_created_at', table_name='security_events')
    op.drop_index('idx_security_events_detection_method', table_name='security_events')
    op.drop_index('idx_security_events_status', table_name='security_events')
    op.drop_index('idx_security_events_tool_id', table_name='security_events')
    op.drop_index('idx_security_events_application_id', table_name='security_events')
    op.drop_index('idx_security_events_agent_id', table_name='security_events')
    op.drop_index('idx_security_events_severity', table_name='security_events')
    op.drop_index('idx_security_events_event_type', table_name='security_events')
    op.drop_table('security_events')

    op.drop_index('idx_dlp_events_confidence', table_name='dlp_events')
    op.drop_index('idx_dlp_events_severity', table_name='dlp_events')
    op.drop_index('idx_dlp_events_data_type', table_name='dlp_events')
    op.drop_index('idx_dlp_events_timestamp', table_name='dlp_events')
    op.drop_index('idx_dlp_events_agent_id', table_name='dlp_events')
    op.drop_table('dlp_events')

    op.drop_index('idx_agent_activity_risk_score', table_name='agent_activity')
    op.drop_index('idx_agent_activity_status', table_name='agent_activity')
    op.drop_index('idx_agent_activity_action_type', table_name='agent_activity')
    op.drop_index('idx_agent_activity_timestamp', table_name='agent_activity')
    op.drop_index('idx_agent_activity_tool_id', table_name='agent_activity')
    op.drop_index('idx_agent_activity_agent_id', table_name='agent_activity')
    op.drop_table('agent_activity')

    op.drop_index('idx_mcp_tools_status', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_data_sensitivity', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_type', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_name', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_agent_id', table_name='mcp_tools')
    op.drop_table('mcp_tools')

    op.drop_index('idx_ai_agents_last_activity', table_name='ai_agents')
    op.drop_index('idx_ai_agents_name', table_name='ai_agents')
    op.drop_index('idx_ai_agents_risk_level', table_name='ai_agents')
    op.drop_index('idx_ai_agents_status', table_name='ai_agents')
    op.drop_index('idx_ai_agents_application_id', table_name='ai_agents')
    op.drop_table('ai_agents')

    op.drop_index('idx_ai_applications_mcp_support', table_name='ai_applications')
    op.drop_index('idx_ai_applications_is_demo', table_name='ai_applications')
    op.drop_index('idx_ai_applications_risk_score', table_name='ai_applications')
    op.drop_index('idx_ai_applications_risk_level', table_name='ai_applications')
    op.drop_index('idx_ai_applications_vendor', table_name='ai_applications')
    op.drop_index('idx_ai_applications_name', table_name='ai_applications')
    op.drop_table('ai_applications')

    op.drop_index('idx_users_is_active', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
