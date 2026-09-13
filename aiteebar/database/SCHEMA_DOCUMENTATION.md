# Aiteebar AI Security - Database Schema Documentation

Complete documentation of the PostgreSQL database schema for the Aiteebar AI Security platform.

## 📋 Table of Contents

1. [Schema Overview](#schema-overview)
2. [Tables](#tables)
3. [Views](#views)
4. [Indexes](#indexes)
5. [Relationships](#relationships)
6. [Data Types](#data-types)
7. [Queries](#common-queries)
8. [Migration Guide](#migration-guide)

## Schema Overview

### Database: `aiteebar_db`

**PostgreSQL Version**: 14+  
**Extensions**: uuid-ossp, pg_trgm, hstore  
**Tables**: 11  
**Views**: 4  
**Total Indexes**: 50+  

### Architecture Pattern

The schema follows a **normalized relational design** with:

- **Core Entities**: Users, Applications, Agents, Tools
- **Activity Tracking**: AgentActivity, DLPEvents, SecurityEvents
- **Policy Management**: Policies, PolicyActions
- **Risk Assessment**: RiskAssessments
- **Destinations**: External service tracking

## Tables

### 1. Users

Stores user accounts with role-based access control.

```sql
-- Key columns
id: UUID PRIMARY KEY
email: VARCHAR UNIQUE
password_hash: VARCHAR (bcrypt)
name: VARCHAR
role: ENUM('admin', 'analyst', 'viewer')
is_active: BOOLEAN
last_login_at: TIMESTAMP
created_at, updated_at: TIMESTAMP
```

**Constraints**:
- Email uniqueness
- Role validation
- Relationships: Policies (created_by)

**Indexes**: email, role, is_active

**Use Cases**:
- User authentication
- Role-based access control
- Audit trail

---

### 2. AI Applications

Represents AI applications/services being assessed.

```sql
-- Key columns
id: UUID PRIMARY KEY
name: VARCHAR
vendor: VARCHAR
category: VARCHAR
description: TEXT

-- Risk Scoring (0-100)
risk_score: NUMERIC
risk_level: ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

-- Dimension Scores
privacy_score: NUMERIC
security_score: NUMERIC
data_handling_score: NUMERIC
enterprise_control_score: NUMERIC
integration_score: NUMERIC
permission_score: NUMERIC

-- Capabilities
mcp_support: BOOLEAN
api_available: BOOLEAN
enterprise_controls: JSONB
data_residency: VARCHAR
authentication: JSONB

is_demo: BOOLEAN
last_assessed: TIMESTAMP
```

**Relationships**: 
- has many AIAgents
- has many SecurityEvents
- has many RiskAssessments

**Indexes**: name, vendor, risk_level, risk_score, is_demo, mcp_support

**Use Cases**:
- Track AI services in use
- Compare security posture
- Demo assessments for testing

---

### 3. AI Agents

Deployed instances of AI applications with independent risk profiles.

```sql
-- Key columns
id: UUID PRIMARY KEY
application_id: UUID FOREIGN KEY
name: VARCHAR
owner: VARCHAR
environment: VARCHAR (production, staging, development)

-- Risk Assessment
risk_score: NUMERIC
risk_level: ENUM
status: ENUM('active', 'inactive', 'suspended')

-- Capabilities
connected_tools: JSONB []
data_access: JSONB {}

last_activity: TIMESTAMP
```

**Relationships**:
- belongs to AIApplication
- has many MCPTools
- has many AgentActivities
- has many DLPEvents
- has many SecurityEvents
- has many RiskAssessments

**Indexes**: application_id, status, risk_level, name, last_activity

**Use Cases**:
- Track agent deployment
- Monitor agent activity
- Assess individual agent risk

---

### 4. MCP Tools

Model Context Protocol tools integrated with agents.

```sql
-- Key columns
id: UUID PRIMARY KEY
agent_id: UUID FOREIGN KEY
name: VARCHAR
type: VARCHAR (database, api, file, execution)
description: TEXT

-- Permissions
permissions: JSONB [] (["read", "write", "execute"])

-- Data Sensitivity
data_sensitivity: ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
risk_score: NUMERIC

status: ENUM('active', 'inactive')
```

**Relationships**:
- belongs to AIAgent
- has many AgentActivities
- has many SecurityEvents
- has many RiskAssessments

**Indexes**: agent_id, name, type, data_sensitivity, status

**Use Cases**:
- Track tool access controls
- Monitor sensitive data exposure
- Assess tool risks

---

### 5. Agent Activity

Detailed log of all agent actions and activities.

```sql
-- Key columns
id: UUID PRIMARY KEY
agent_id: UUID FOREIGN KEY
tool_id: UUID FOREIGN KEY (nullable)

timestamp: TIMESTAMP
action_type: ENUM('CONNECT', 'READ', 'WRITE', 'EXECUTE', 'EXTERNAL_CALL')
resource_name: VARCHAR
status: ENUM('pending', 'executed', 'blocked')

risk_score: NUMERIC
metadata: JSONB
```

**Relationships**:
- belongs to AIAgent
- belongs to MCPTool (optional)

**Indexes**: agent_id, tool_id, timestamp DESC, action_type, status, risk_score DESC

**Use Cases**:
- Activity audit trail
- Threat detection
- Anomaly detection

**Note**: This table grows quickly; consider archiving old records.

---

### 6. DLP Events

Data Loss Prevention events - sensitive data detection.

```sql
-- Key columns
id: UUID PRIMARY KEY
agent_id: UUID FOREIGN KEY
timestamp: TIMESTAMP

-- Detection
data_type: ENUM('CNIC', 'IBAN', 'EMAIL', 'PHONE', 'API_KEY', 'PASSWORD', ...)
confidence: NUMERIC (0-100)
severity: ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

matched_context: TEXT (detected pattern/content)
recommended_action: TEXT
detected_in: VARCHAR (tool name)
```

**Relationships**:
- belongs to AIAgent

**Indexes**: agent_id, timestamp DESC, data_type, severity, confidence DESC

**Use Cases**:
- Detect sensitive data leakage
- Compliance reporting
- Data exposure monitoring

---

### 7. Security Events

Security incidents and alerts.

```sql
-- Key columns
id: UUID PRIMARY KEY

event_type: VARCHAR
severity: ENUM('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

agent_id: UUID FOREIGN KEY (nullable)
application_id: UUID FOREIGN KEY (nullable)
tool_id: UUID FOREIGN KEY (nullable)

source: VARCHAR
destination: VARCHAR

detection_method: ENUM('policy_engine', 'dlp', 'threat_detection', 'manual', 'other')
risk_score: NUMERIC

action_taken: ENUM('ALLOWED', 'WARNED', 'APPROVAL_REQUIRED', 'BLOCKED')
status: ENUM('open', 'acknowledged', 'resolved')

created_at, updated_at: TIMESTAMP
```

**Relationships**:
- may reference AIAgent
- may reference AIApplication
- may reference MCPTool
- has many PolicyActions

**Indexes**: event_type, severity, agent_id, application_id, tool_id, status, detection_method, created_at DESC, risk_score DESC

**Use Cases**:
- Track security incidents
- Policy violation alerts
- Threat detection

---

### 8. Policies

Security policies defining rules and actions.

```sql
-- Key columns
id: UUID PRIMARY KEY
created_by: UUID FOREIGN KEY (users)

name: VARCHAR
description: TEXT
enabled: BOOLEAN

-- Policy Definition
condition: JSONB (if/then rules)
action: ENUM('ALLOW', 'WARN', 'REQUIRE_APPROVAL', 'BLOCK')

-- Evaluation Priority
priority: INTEGER (lower = higher priority)

created_at, updated_at: TIMESTAMP
```

**Relationships**:
- belongs to User (created_by)
- has many PolicyActions

**Indexes**: created_by, enabled, priority ASC, action

**Use Cases**:
- Define security rules
- Control agent behavior
- Implement compliance policies

---

### 9. Policy Actions

Tracking of policy executions.

```sql
-- Key columns
id: UUID PRIMARY KEY
policy_id: UUID FOREIGN KEY
event_id: UUID FOREIGN KEY (security_events)

action_taken: VARCHAR
executed_at: TIMESTAMP
created_at: TIMESTAMP
```

**Relationships**:
- belongs to Policy
- belongs to SecurityEvent

**Indexes**: policy_id, event_id, executed_at DESC

**Use Cases**:
- Audit policy executions
- Policy effectiveness metrics
- Compliance logging

---

### 10. Destinations

External services and APIs agents connect to.

```sql
-- Key columns
id: UUID PRIMARY KEY
name: VARCHAR
url: VARCHAR

risk_score: NUMERIC
risk_level: ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
is_internal: BOOLEAN

created_at, updated_at: TIMESTAMP
```

**Indexes**: name, is_internal, risk_level

**Use Cases**:
- Track external API usage
- Monitor destination risk
- External service inventory

---

### 11. Risk Assessments

Risk assessment snapshots for entities.

```sql
-- Key columns
id: UUID PRIMARY KEY

entity_type: ENUM('application', 'agent', 'tool')
application_id: UUID FOREIGN KEY (nullable)
agent_id: UUID FOREIGN KEY (nullable)
tool_id: UUID FOREIGN KEY (nullable)

overall_score: NUMERIC (0-100)
dimensions: JSONB (privacy, security, data_handling scores)

explanation: TEXT
key_concerns: JSONB []
recommended_controls: JSONB []

assessment_date: TIMESTAMP
next_assessment_date: TIMESTAMP
created_at: TIMESTAMP
```

**Relationships**:
- may reference AIApplication
- may reference AIAgent
- may reference MCPTool

**Indexes**: entity_type, application_id, agent_id, tool_id, overall_score DESC, assessment_date DESC

**Use Cases**:
- Track risk over time
- Assessment history
- Trend analysis

---

## Views

### 1. vw_security_events_full

Full context security events with related data.

```sql
SELECT 
    se.*,
    aa.name as application_name,
    ag.name as agent_name,
    mt.name as tool_name
FROM security_events se
LEFT JOIN ai_applications aa ON se.application_id = aa.id
LEFT JOIN ai_agents ag ON se.agent_id = ag.id
LEFT JOIN mcp_tools mt ON se.tool_id = mt.id
```

### 2. vw_high_risk_agents

High-risk agents with recent activity counts.

```sql
SELECT 
    ag.*,
    aa.name as application_name,
    COUNT(DISTINCT aa_rec.id) as recent_activities_24h,
    COUNT(DISTINCT se.id) as recent_events_24h
WHERE ag.risk_level IN ('HIGH', 'CRITICAL')
GROUP BY ag.id, aa.name
ORDER BY ag.risk_score DESC
```

### 3. vw_policy_effectiveness

Policy effectiveness metrics.

```sql
SELECT 
    p.*,
    COUNT(pa.id) as total_executions,
    COUNT(CASE WHEN pa.action_taken = p.action THEN 1 END) as successful_executions,
    ROUND(success_count / total_count * 100, 2) as effectiveness_percentage
```

### 4. vw_dlp_summary

DLP incidents by data type and severity.

```sql
SELECT 
    data_type,
    severity,
    COUNT(*) as incident_count,
    ROUND(AVG(confidence), 2) as avg_confidence,
    MAX(timestamp) as latest_incident
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY data_type, severity
```

---

## Indexes

### Performance-Critical Indexes

| Table | Column | Type | Reason |
|-------|--------|------|--------|
| agent_activity | (agent_id, timestamp DESC) | Composite | Recent activity lookup |
| security_events | (severity, status) | Composite | Alert filtering |
| dlp_events | (agent_id, timestamp DESC) | Composite | DLP timeline |
| ai_agents | (status, risk_level) | Composite | Dashboard queries |
| ai_applications | risk_score DESC | Desc | Sorting by risk |

### Index Statistics

- **Total Indexes**: 50+
- **Composite Indexes**: 10+
- **DESC Indexes**: 15+
- **Functional Indexes**: 0 (currently)

---

## Relationships

### Entity Relationships

```
User
  ├── creates → Policy

AIApplication
  ├── has → AIAgent (1:N)
  ├── referenced_by → SecurityEvent
  └── assessed_by → RiskAssessment

AIAgent
  ├── has → MCPTool (1:N)
  ├── has → AgentActivity (1:N)
  ├── has → DLPEvent (1:N)
  ├── referenced_by → SecurityEvent
  └── assessed_by → RiskAssessment

MCPTool
  ├── has → AgentActivity (1:N)
  ├── referenced_by → SecurityEvent
  └── assessed_by → RiskAssessment

Policy
  └── generates → PolicyAction (1:N)

SecurityEvent
  └── triggers → PolicyAction (1:N)
```

---

## Data Types

### Enums Used

```sql
-- User Roles
ENUM('admin', 'analyst', 'viewer')

-- Risk Levels
ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

-- Agent Status
ENUM('active', 'inactive', 'suspended')

-- Activity Action Types
ENUM('CONNECT', 'READ', 'WRITE', 'EXECUTE', 'EXTERNAL_CALL')

-- Activity Status
ENUM('pending', 'executed', 'blocked')

-- Data Types (DLP)
ENUM('CNIC', 'IBAN', 'EMAIL', 'PHONE', 'API_KEY', 'PASSWORD', ...)

-- Event Severity
ENUM('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')

-- Action Taken
ENUM('ALLOWED', 'WARNED', 'APPROVAL_REQUIRED', 'BLOCKED')

-- Event Status
ENUM('open', 'acknowledged', 'resolved')

-- Detection Method
ENUM('policy_engine', 'dlp', 'threat_detection', 'manual', 'other')

-- Policy Action
ENUM('ALLOW', 'WARN', 'REQUIRE_APPROVAL', 'BLOCK')

-- Tool Status
ENUM('active', 'inactive')

-- Entity Type
ENUM('application', 'agent', 'tool')
```

### JSONB Columns

- `ai_applications.enterprise_controls`: Array of control names
- `ai_applications.authentication`: Auth method details
- `ai_agents.connected_tools`: Tool configuration array
- `ai_agents.data_access`: Data access patterns
- `mcp_tools.permissions`: Permission list
- `agent_activity.metadata`: Activity metadata
- `risk_assessments.dimensions`: Dimension scores
- `risk_assessments.key_concerns`: Concern list
- `risk_assessments.recommended_controls`: Control recommendations
- `policies.condition`: Policy rules

---

## Common Queries

### High-Risk Agents with Recent Activity

```sql
SELECT 
    ag.id, ag.name, ag.risk_score,
    COUNT(aa.id) as activity_count,
    MAX(aa.timestamp) as last_activity
FROM ai_agents ag
LEFT JOIN agent_activity aa ON ag.id = aa.agent_id 
    AND aa.timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
WHERE ag.risk_level = 'CRITICAL'
GROUP BY ag.id, ag.name, ag.risk_score
ORDER BY ag.risk_score DESC;
```

### DLP Events by Data Type (Last 7 Days)

```sql
SELECT 
    data_type,
    COUNT(*) as event_count,
    ROUND(AVG(confidence), 2) as avg_confidence,
    MAX(severity) as highest_severity
FROM dlp_events
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY data_type
ORDER BY event_count DESC;
```

### Unresolved Security Events

```sql
SELECT 
    se.id, se.event_type, se.severity, se.created_at,
    aa.name as agent_name,
    aa.name as application_name
FROM security_events se
LEFT JOIN ai_agents aa ON se.agent_id = aa.id
LEFT JOIN ai_applications ia ON se.application_id = ia.id
WHERE se.status = 'open'
ORDER BY se.severity DESC, se.created_at DESC;
```

### Policy Effectiveness Report

```sql
SELECT 
    p.id, p.name, p.action,
    COUNT(pa.id) as total_executions,
    COUNT(CASE WHEN pa.action_taken = p.action THEN 1 END) as successful,
    ROUND(
        COUNT(CASE WHEN pa.action_taken = p.action THEN 1 END)::NUMERIC /
        NULLIF(COUNT(pa.id), 0) * 100, 2
    ) as effectiveness_percent
FROM policies p
LEFT JOIN policy_actions pa ON p.id = pa.policy_id
GROUP BY p.id, p.name, p.action
ORDER BY effectiveness_percent DESC NULLS LAST;
```

---

## Migration Guide

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Rollback specific number
alembic downgrade -2

# Check current version
alembic current

# View migration history
alembic history
```

### Creating New Migrations

```bash
# Create new migration (autogenerate from ORM changes)
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description"
```

### Migration Best Practices

1. **Always test migrations** in development first
2. **Keep migrations small** - one logical change per migration
3. **Make migrations reversible** - implement both upgrade() and downgrade()
4. **Document complex migrations** with comments
5. **Never modify applied migrations** - create new ones instead
6. **Review SQL** before applying in production

---

## Constraints and Validation

### Check Constraints

All risk scores are validated as 0-100:
```sql
CHECK (score >= 0 AND score <= 100)
```

Enum constraints ensure valid values:
```sql
CHECK (role IN ('admin', 'analyst', 'viewer'))
CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
```

RiskAssessment constraints ensure valid entity references:
```sql
CHECK (
    (entity_type = 'application' AND application_id IS NOT NULL) OR
    (entity_type = 'agent' AND agent_id IS NOT NULL) OR
    (entity_type = 'tool' AND tool_id IS NOT NULL)
)
```

### Foreign Key Constraints

- Cascade delete on parent deletion
- Set null on optional foreign keys
- Restrict delete when referenced by users

---

## Performance Considerations

### Query Optimization Tips

1. **Use filtered indexes** for common WHERE conditions
2. **Join through indexed columns** - prefer PK/FK joins
3. **Partition large tables** (e.g., agent_activity by date)
4. **Archive old events** regularly
5. **Use EXPLAIN ANALYZE** to review query plans

### Maintenance Tasks

```sql
-- Analyze query optimization
VACUUM ANALYZE;

-- Check index usage
SELECT * FROM pg_stat_user_indexes;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial schema creation |

---

## Support

For schema questions or issues, refer to:
- ARCHITECTURE.md - System design context
- DEVELOPMENT.md - Development setup
- database/schema.sql - SQL definitions
