# AI Application Risk Assessment System

## Overview

The Aiteebar AI Security platform now includes a comprehensive, multi-dimensional risk assessment system for evaluating AI applications. This system demonstrates how the platform assesses and communicates risk through transparent, explainable scoring.

## Scoring Dimensions

The risk assessment evaluates applications across **6 key dimensions**:

### 1. **Privacy Score (20% weight)**
- Evaluates data collection, storage, and usage policies
- Assesses compliance with privacy regulations
- Considers data retention and deletion practices

### 2. **Security Score (25% weight)**
- Analyzes security practices and certifications
- Reviews vulnerability management track record
- Evaluates compliance with security standards (SOC2, ISO27001, etc.)

### 3. **Data Handling Score (20% weight)**
- Assesses encryption practices (in transit and at rest)
- Evaluates data retention policies
- Reviews secure deletion capabilities

### 4. **Enterprise Controls Score (15% weight)**
- Evaluates admin control capabilities
- Assesses SSO/SAML integration support
- Reviews audit logging capabilities

### 5. **Integration Score (10% weight)**
- Assesses API security measures
- Evaluates safe integration options
- Reviews third-party access controls

### 6. **Permission Score (10% weight)**
- Evaluates scope of required permissions
- Assesses granular permission controls
- Reviews least-privilege implementation

## Risk Levels

Risk scores (0-100) are categorized into four levels:

| Level | Score Range | Color | Interpretation |
|-------|-----------|-------|-----------------|
| **LOW** | 0-25 | 🟢 Green | Minimal risk, can generally be approved |
| **MEDIUM** | 26-50 | 🟡 Yellow | Moderate risk, requires controls |
| **HIGH** | 51-75 | 🟠 Orange | Significant risk, needs strong controls |
| **CRITICAL** | 76-100 | 🔴 Red | Severe risk, executive review required |

## Overall Score Calculation

The overall risk score is a **weighted average** of all dimensions:

```
Overall Score = 
  (Privacy × 0.20) +
  (Security × 0.25) +
  (Data Handling × 0.20) +
  (Enterprise Controls × 0.15) +
  (Integration × 0.10) +
  (Permission × 0.10)
```

## Backend Implementation

### Services
- **File**: `backend/app/services/risk.py`
- **Features**:
  - Calculate overall scores from dimension data
  - Categorize risk levels
  - Generate key concerns based on scores
  - Recommend security controls
  - Format dimension data with colors and labels

### Schemas
- **File**: `backend/app/schemas/risk.py`
- **Models**:
  - `RiskAssessmentResponse`: Complete assessment data
  - `DimensionScore`: Individual dimension breakdown
  - `RiskMetricsResponse`: Organization-wide metrics

### API Endpoints
- **File**: `backend/app/routers/risk.py`
- **Endpoints**:
  - `GET /api/risk/applications/{id}` - Get application risk assessment
  - `GET /api/risk/metrics` - Get organization-wide risk metrics
  - `GET /api/risk/by-level/{risk_level}` - Get applications by risk level

### Database
- **Model**: `AIApplication` (in `backend/app/models.py`)
- **Fields**:
  - `risk_score`: Overall risk score (0-100)
  - `risk_level`: Risk category (LOW, MEDIUM, HIGH, CRITICAL)
  - `privacy_score`: Privacy dimension score
  - `security_score`: Security dimension score
  - `data_handling_score`: Data handling dimension score
  - `enterprise_control_score`: Enterprise controls dimension score
  - `integration_score`: Integration dimension score
  - `permission_score`: Permission dimension score
  - `last_assessed`: Timestamp of last assessment

## Frontend Implementation

### Pages

#### 1. Risk Metrics Dashboard
- **Path**: `/risk-metrics`
- **Features**:
  - Organization-wide risk overview
  - Risk distribution by level
  - Highest risk applications list
  - Average risk scores
  - Drill-down into high-risk apps

#### 2. Application Risk Assessment
- **Path**: `/applications/[id]/risk`
- **Features**:
  - Detailed risk score visualization
  - Dimension-by-dimension breakdown
  - Key concerns identified
  - Recommended security controls
  - Assessment timestamp and next review date

### Components

#### 1. **RiskScoreGauge**
- Circular gauge visualization (0-100)
- Color-coded by risk level
- Animated needle indicator
- Risk level badge
- Score legend

#### 2. **DimensionBreakdown**
- Horizontal bar charts for each dimension
- Color-coded by risk level
- Dimension explanations
- Quick summary grid
- Score interpretation guide

#### 3. **KeyConcernsList**
- Risk concerns identified by algorithm
- Visual highlighting (orange/warning style)
- Concerns based on dimension scores above 70
- Risk assessment explanation

#### 4. **RecommendedControls**
- Security controls to implement
- Prioritized by risk level
- Implementation guidance
- Control icons for visual identification

#### 5. **RiskBadge**
- Compact risk indicator
- Can be embedded in application lists
- Clickable to view full assessment
- Shows score and risk level

## Testing the Feature

### 1. Access Risk Metrics Dashboard
```
http://localhost:3000/risk-metrics
```
View organization-wide risk overview with all applications categorized by risk level.

### 2. View Application Risk Assessment
```
http://localhost:3000/applications/{application_id}/risk
```
See detailed assessment with scores, concerns, and controls.

### 3. Test API Endpoints (via Swagger)
```
http://localhost:8000/docs
```

Navigate to the "risk" section and try:
- `GET /api/risk/applications/{id}` - Get specific app assessment
- `GET /api/risk/metrics` - Get organization metrics
- `GET /api/risk/by-level/{risk_level}` - Filter by risk level

## Seeded Data

The database includes **38+ AI applications** with complete risk assessments:

### General AI (10 apps)
- ChatGPT (Risk: HIGH - 65)
- Claude (Risk: MEDIUM - 55)
- Google Gemini (Risk: HIGH - 60)
- Microsoft Copilot (Risk: HIGH - 62)
- Perplexity AI (Risk: MEDIUM - 58)
- Grok (Risk: HIGH - 72)
- DeepSeek (Risk: MEDIUM - 50)
- LLaMA 2/3 (Risk: LOW - 45)
- Qwen (Risk: MEDIUM - 55)
- Mistral AI (Risk: LOW - 48)

### AI Coding (10 apps)
- GitHub Copilot (Risk: HIGH - 68)
- Cursor (Risk: MEDIUM - 55)
- Claude for Code (Risk: MEDIUM - 52)
- Windsurf (Risk: MEDIUM - 54)
- Amazon Q Developer (Risk: MEDIUM - 58)
- Codeium (Risk: LOW - 48)
- Tabnine (Risk: LOW - 50)
- Continue.dev (Risk: LOW - 45)
- Phind (Risk: MEDIUM - 56)

### Enterprise AI (8 apps)
- Azure OpenAI (Risk: MEDIUM - 52)
- Amazon Bedrock (Risk: MEDIUM - 50)
- Google Vertex AI (Risk: MEDIUM - 55)
- IBM watsonx (Risk: MEDIUM - 54)
- Oracle AI Platform (Risk: MEDIUM - 56)

### Productivity AI (6 apps)
- Notion AI (Risk: MEDIUM - 58)
- Microsoft Copilot Pro (Risk: MEDIUM - 60)
- Google Workspace AI (Risk: MEDIUM - 62)
- Slack AI (Risk: MEDIUM - 59)
- Grammarly (Risk: HIGH - 70)
- Jasper AI (Risk: HIGH - 68)

### AI Automation (5 apps)
- Zapier AI (Risk: HIGH - 65)
- Make.com (Risk: HIGH - 64)
- Dify (Risk: LOW - 45)
- LangChain (Risk: LOW - 40)
- n8n (Risk: LOW - 42)

### AI Infrastructure (7 apps)
- LangGraph (Risk: LOW - 38)
- Claude (Self-hosted) (Risk: LOW - 42)
- Ollama (Risk: LOW - 35)
- llama.cpp (Risk: LOW - 32)
- vLLM (Risk: LOW - 32)

**And more...**

## How Risk Scores Are Generated

### Algorithm

1. **Dimension Scoring**: Each dimension (Privacy, Security, etc.) is scored 0-100
2. **Weighted Calculation**: Apply weights to each dimension
3. **Overall Score**: Calculate weighted average
4. **Risk Categorization**: Determine LOW/MEDIUM/HIGH/CRITICAL
5. **Concern Analysis**: Extract concerns from high-scoring dimensions
6. **Control Recommendation**: Suggest controls based on weaknesses

### Example: ChatGPT Assessment
```
Privacy Score:              70
Security Score:             65
Data Handling Score:        60
Enterprise Control Score:   60
Integration Score:          85
Permission Score:           70

Calculation:
  (70 × 0.20) +        = 14
  (65 × 0.25) +        = 16.25
  (60 × 0.20) +        = 12
  (60 × 0.15) +        = 9
  (85 × 0.10) +        = 8.5
  (70 × 0.10)          = 7

Overall Score: 65 (HIGH RISK)
```

### Key Concerns Generated
- "High privacy risk: Limited data protection measures" (privacy_score > 70)
- "Data handling: Weak encryption or retention policies" (data_handling_score > 70)

### Recommended Controls
- Implement data minimization policies and DLP controls
- Enable continuous monitoring and threat detection
- Conduct regular security audits (quarterly)

## Important Notes

### ⚠️ Disclaimer

- **Demo Data**: All risk scores are demonstration assessments for illustrative purposes
- **Not Real Assessments**: These do not represent actual vendor security postures
- **For Training**: Use this system to understand risk assessment methodology
- **Not for Production**: Do not use these demo scores for real vendor selection
- **Actual Assessment Required**: Conduct real security assessments with actual vendors

### Future Enhancements

- [ ] Admin UI to update risk assessments
- [ ] Real vendor assessment data integration
- [ ] Historical risk trend tracking
- [ ] Custom risk weightings per organization
- [ ] Risk remediation tracking
- [ ] Vendor scorecard integration
- [ ] Automated assessment updates via API
- [ ] PDF report generation

## Integration Points

### Existing Features
- Risk scores already integrated into the Applications Catalog
- Accessible from each application's detail page
- Included in API responses for filtering/sorting

### Navigation
- Add Risk Metrics link to main navigation
- Link from Applications page to risk assessments
- Quick-access risk badges on dashboards

## Support & Questions

For questions about the risk assessment methodology, see:
- Backend service: `backend/app/services/risk.py`
- API endpoints: `backend/app/routers/risk.py`
- Frontend components: `frontend/components/risk/`

---

**Last Updated**: 2026-09-13
**Version**: 1.0.0
**Status**: Complete - Ready for Testing
