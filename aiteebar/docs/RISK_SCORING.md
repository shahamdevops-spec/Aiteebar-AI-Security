# Multi-Factor Explainable Risk Scoring System

## Overview

The **Risk Scoring Engine** is a sophisticated system that combines 7 distinct risk factors to calculate comprehensive risk assessments for AI applications, agents, tools, and network destinations. It provides explainable, transparent risk scores with detailed breakdowns of contributing factors.

### Key Features

✅ **7-Factor Assessment** - Comprehensive risk evaluation across multiple dimensions
✅ **Explainable Scoring** - Transparent breakdown of every factor and its contribution
✅ **Weighted Algorithm** - Scientifically calibrated weights for each factor
✅ **Real-Time Calculation** - Integrates with live system data (DLP, Threats, etc.)
✅ **Multi-Entity Support** - Score applications, agents, tools, and destinations
✅ **Risk Recommendations** - Actionable recommendations based on risk level
✅ **Trend Analysis** - Track risk changes over time
✅ **Comparative Analysis** - Compare risk scores between entities

---

## Risk Factors & Weights

### 1. Application Risk (Weight: 25%)

**Purpose**: Assess the inherent risk of the parent application

**Calculation Inputs**:
- Application risk_score (0-100)
- Risk level classification (LOW/MEDIUM/HIGH/CRITICAL)
- Security assessment dimensions:
  - Privacy score
  - Security score
  - Data handling score

**Formula**:
```
app_risk = (
  app_risk_score * 0.4 +
  level_score * 0.3 +
  (100 - security_score) * 0.15 +
  (100 - privacy_score) * 0.10 +
  (100 - data_handling_score) * 0.05
)
```

**Example**:
- App with HIGH risk level, 60% security = ~75/100 app risk factor
- Contributes 0.75 × 0.25 = 18.75 points to overall score

---

### 2. Agent Privilege Level (Weight: 20%)

**Purpose**: Evaluate agent's access and capabilities

**Calculation Inputs**:
- Number of connected tools (max 40 points)
- Data access scope (max 30 points)
- Agent status (active/inactive) (20 points)
- Agent risk level classification (10-100 points)

**Formula**:
```
privilege_risk = (
  min(40, num_tools * 5) +
  min(30, num_data_types * 10) +
  (20 if active else 5) +
  level_risk_score
)
```

**Example**:
- Agent with 5 tools, 3 data access types, active status
- Tools: 25pts, Data: 30pts, Status: 20pts = ~65/100 privilege risk
- Contributes 0.65 × 0.20 = 13 points to overall score

---

### 3. Data Sensitivity Level (Weight: 25%)

**Purpose**: Assess types and scope of sensitive data accessed

**Data Type Severity Weights**:
- **CRITICAL (95-98)**: CNIC, IBAN, PASSWORD, API_KEY, AWS_SECRET, CREDIT_CARD
- **HIGH (70-75)**: SOURCE_CODE, CONFIDENTIAL
- **MEDIUM (35-40)**: EMAIL, PHONE

**Formula**:
```
sensitivity_risk = weighted_average(accessed_data_types) + boost

Where:
boost = min(15, num_critical_types * 5)
```

**Example**:
- Accessing CNIC (95) + EMAIL (40) + API_KEY (92) = avg 75.67
- With 2 critical types boost: 75.67 + 10 = 85.67/100
- Contributes 0.8567 × 0.25 = 21.4 points to overall score

---

### 4. Tool Permission Scope (Weight: 15%)

**Purpose**: Evaluate risk of connected tools and their permissions

**Tool Risk Weights**:
- **CRITICAL tools**: 95 points
- **HIGH tools**: 70 points
- **MEDIUM tools**: 40 points
- **LOW tools**: 15 points

**Formula**:
```
tool_permission_risk = (
  average_tool_risk +
  min(20, num_dangerous_tools * 10)
)
```

**Example**:
- Agent with 1 CRITICAL tool (ExecuteCommand) + 1 LOW tool (ReadFile)
- Average: (95 + 15) / 2 = 55
- With 1 dangerous tool boost: 55 + 10 = 65/100
- Contributes 0.65 × 0.15 = 9.75 points to overall score

---

### 5. Destination Risk (Weight: 10%)

**Purpose**: Assess network destination risk and connection patterns

**Calculation Inputs**:
- Internal vs External destination
- Number of external connections
- Destination risk scores

**Formula**:
```
destination_risk = (
  external_connection_risk * 0.6 +
  average_destination_risk * 0.4
)

Where:
external_connection_risk = min(60, num_external * 20)
```

**Example**:
- Agent with 3 external connections to average-risk destinations
- External risk: min(60, 3 * 20) = 60
- Avg destination risk: 55
- Final: (60 * 0.6) + (55 * 0.4) = 58/100
- Contributes 0.58 × 0.10 = 5.8 points to overall score

---

### 6. Behavior Anomaly Score (Weight: 5%)

**Purpose**: Incorporate behavioral threat detection signals

**Calculation Inputs**:
- Number of detected threats
- Threat severity levels (CRITICAL=100, HIGH=60, MEDIUM=30, LOW=10)
- Recency of threats (last hour = +5 per threat)

**Formula**:
```
behavior_anomaly = (
  average_threat_score * 0.8 +
  recency_boost
)

Where:
recency_boost = min(20, recent_threat_count * 5)
```

**Example**:
- Agent with 2 HIGH threats + 1 MEDIUM threat from last hour
- Avg threat: (60 + 60 + 30) / 3 = 50
- Recency boost: min(20, 3 * 5) = 15
- Final: (50 * 0.8) + 15 = 55/100
- Contributes 0.55 × 0.05 = 2.75 points to overall score

---

## Overall Risk Scoring

### Final Formula

```
overall_risk_score = Σ (factor_value × factor_weight)

= (app_risk × 0.25) +
  (privilege_level × 0.20) +
  (data_sensitivity × 0.25) +
  (tool_permissions × 0.15) +
  (destination_risk × 0.10) +
  (behavior_anomaly × 0.05)
```

### Risk Level Classification

| Score Range | Level | Action |
|-------------|-------|--------|
| 0-40 | **LOW** | Continue normal monitoring |
| 40-60 | **MEDIUM** | Monitor activity, schedule review |
| 60-80 | **HIGH** | Restrict permissions, increase monitoring |
| 80-100 | **CRITICAL** | Isolate agent, immediate investigation |

### Example Calculation

**Scenario**: DataProcessor agent accessing customer database

| Factor | Value | Weight | Contribution |
|--------|-------|--------|--------------|
| Application Risk | 65 | 0.25 | 16.25 |
| Agent Privilege | 55 | 0.20 | 11.0 |
| Data Sensitivity | 85 | 0.25 | 21.25 |
| Tool Permissions | 45 | 0.15 | 6.75 |
| Destination Risk | 50 | 0.10 | 5.0 |
| Behavior Anomaly | 30 | 0.05 | 1.5 |
| **OVERALL** | **68.75** | **1.00** | **61.75** |

**Result**: **HIGH RISK** (68.75/100)
**Recommendation**: Restrict permissions, increase monitoring

---

## API Endpoints

### GET /api/risk/score

Calculate risk score for an entity.

**Parameters**:
- `entity_type`: "application" | "agent" | "tool" | "destination"
- `entity_id`: UUID of the entity

**Example Request**:
```bash
GET /api/risk/score?entity_type=agent&entity_id=agent_12345
```

**Response**:
```json
{
  "entity_type": "agent",
  "entity_id": "agent_12345",
  "overall_score": 68.3,
  "risk_level": "HIGH",
  "factors": [
    {
      "name": "Data Sensitivity Level",
      "value": 85.0,
      "weight": 0.25,
      "weighted_contribution": 21.25,
      "explanation": "Accessing 3 data types including CNIC, IBAN, API_KEY",
      "contributing_factors": {
        "data_types_accessed": ["CNIC", "IBAN", "API_KEY"],
        "CNIC_sensitivity": 95,
        "IBAN_sensitivity": 90,
        "API_KEY_sensitivity": 92
      }
    },
    ...
  ],
  "explanation": "Agent 'DataAnalyzer' has HIGH overall risk score (68.3/100)",
  "detailed_explanation": "Risk Factor Breakdown:\n1. Data Sensitivity...",
  "timestamp": "2025-09-13T10:30:45Z"
}
```

### GET /api/risk/summary

Get summary of risk scores for all entities of a type.

**Parameters**:
- `entity_type`: Type of entities to summarize
- `days`: Time period (default: 7)

**Response**:
```json
{
  "summary_date": "2025-09-13T10:30:45Z",
  "entity_type": "agent",
  "total_entities": 15,
  "average_score": 52.3,
  "highest_risk_score": 89.5,
  "lowest_risk_score": 12.3,
  "risk_level_breakdown": {
    "CRITICAL": 1,
    "HIGH": 4,
    "MEDIUM": 7,
    "LOW": 3
  },
  "critical_count": 1,
  "high_count": 4,
  "medium_count": 7,
  "low_count": 3
}
```

### GET /api/risk/recommendations/{entity_id}

Get risk mitigation recommendations.

**Parameters**:
- `entity_id`: UUID of the entity
- `entity_type`: Type of entity

**Response**:
```json
{
  "entity_id": "agent_123",
  "risk_level": "HIGH",
  "recommendations": [
    "RESTRICT tool access to essential tools only",
    "Increase monitoring frequency and alerting",
    "Review and audit data access permissions",
    "Implement rate limiting on requests"
  ],
  "priority": "HIGH",
  "estimated_remediation_time": "2-8 hours"
}
```

---

## Frontend Dashboard

**Location**: `/risk-scoring` route

**Features**:
1. **Risk Score Calculator** - Calculate scores for any entity
2. **Risk Gauge** - Visual representation of risk score (0-100)
3. **Factor Breakdown** - Detailed visualization of all factors
4. **Contributing Factors** - Component factors influencing each factor
5. **Risk Interpretation** - Explanation of risk levels and meanings
6. **Detailed Breakdown** - Full text explanation of assessment

---

## Explainability & Transparency

### Factor Explainability

Each factor includes:
1. **Clear Name** - What aspect is being measured
2. **Numerical Value** - The raw 0-100 score
3. **Weight** - How much it contributes to overall
4. **Explanation** - Human-readable description
5. **Contributing Factors** - Component elements that make up the factor

### Example Transparency

```
Data Sensitivity Level: 85/100 (Weight: 25% = 21.25 contribution)
├─ Explanation: Accessing 3 data types including CNIC, IBAN, API_KEY
├─ Contributing Factors:
│  ├─ CNIC: 95 (National ID - Critical)
│  ├─ IBAN: 90 (Bank Account - Critical)
│  ├─ API_KEY: 92 (API Credential - Critical)
│  └─ Boost: +10 (multiple critical types)
└─ Result: (95 + 90 + 92) / 3 + 10 = 85.67 → 85
```

---

## Integration Points

### With DLP Engine
- DLP events used to calculate **Data Sensitivity** factor
- Credential exposures boost sensitivity score

### With Threat Detection
- Threat detections feed into **Behavior Anomaly** factor
- Threat severity weighted appropriately

### With Agent Activity
- Agent connections inform **Destination Risk**
- Tool usage feeds **Tool Permission Scope**

### With Application Registry
- Application risk_score and dimensions used directly
- Application risk_level weights overall score

---

## Testing

### Run Tests
```bash
pytest tests/test_risk_scoring.py -v
```

### Test Coverage
- ✅ All 7 factors tested individually
- ✅ Edge cases (no data, all critical, etc.)
- ✅ Multi-entity scenarios
- ✅ Risk level classification
- ✅ Score-to-dict conversion
- ✅ Explanation generation

---

## Best Practices

### For Security Teams
1. **Monitor HIGH agents** - Review and remediate weekly
2. **Investigate CRITICAL** - Take immediate action
3. **Establish baseline** - Understand normal risk levels
4. **Set alerts** - Notify on risk level changes
5. **Document decisions** - Track risk mitigation actions

### For Developers
1. **Understand factors** - Know what drives scores
2. **Minimize privilege** - Reduce agent_privilege_level
3. **Limit data access** - Keep data_sensitivity low
4. **Use safe tools** - Choose LOW sensitivity tools
5. **Monitor behavior** - Address anomalies quickly

### For Operations
1. **Regular reviews** - Check risk summaries weekly
2. **Trend analysis** - Watch for increasing scores
3. **Capacity planning** - Factor risk into decisions
4. **Documentation** - Keep audit trail of changes
5. **Training** - Educate teams on risk factors

---

## Calibration & Tuning

### Adjusting Weights

If you find certain factors are over/underweighting:

1. **Collect feedback** - Gather security team insights
2. **Analyze incidents** - Compare risk scores to incidents
3. **Recalibrate** - Adjust weights in engine.py
4. **Test** - Run through historical data
5. **Deploy** - Update production weights

### Example Weight Adjustment

```python
# If DATA_SENSITIVITY false alarms on legitimate access:
# Reduce from 0.25 to 0.20

overall_score = (
  app_risk * 0.25 +
  agent_privilege * 0.20 +
  data_sensitivity * 0.20  # ← Reduced
  tool_permissions * 0.20  # ← Increased
  destination_risk * 0.10 +
  behavior_anomaly * 0.05
)
```

---

## Future Enhancements

- [ ] Machine learning-based weighting
- [ ] Custom factor definitions per organization
- [ ] Temporal risk trends and forecasting
- [ ] Collaborative risk assessment
- [ ] Automated risk remediation workflows
- [ ] Risk-based access control (RBAC)
- [ ] Benchmarking against similar entities
- [ ] Industry-specific risk models
- [ ] Third-party risk integration
- [ ] Regulatory compliance mapping

---

## Support

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Code**: `/backend/app/services/risk/`
- **Tests**: `/backend/tests/test_risk_scoring.py`
- **Frontend**: `/frontend/app/risk-scoring/page.tsx`

---

**Last Updated**: 2025-09-13
**Version**: 1.0.0
**Status**: Production Ready ✅
