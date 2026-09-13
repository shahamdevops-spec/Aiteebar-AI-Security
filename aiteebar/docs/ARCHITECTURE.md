# Aiteebar AI Security - Architecture Documentation

## System Overview

Aiteebar AI Security is a production-ready platform designed to provide AI-powered security analysis and threat intelligence. The system is built on a modern, scalable microservices architecture with clear separation of concerns.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Web Browser     │  │  Mobile App      │  │  CLI Tools   │  │
│  │  (Next.js React) │  │  (React Native)  │  │  (Python)    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                      │                    │           │
└───────────┼──────────────────────┼────────────────────┼───────────┘
            │                      │                    │
            │ HTTPS/WebSocket      │ HTTPS/WebSocket    │ HTTPS
            │                      │                    │
┌───────────┼──────────────────────┼────────────────────┼───────────┐
│           ▼                      ▼                    ▼           │
│  ┌────────────────────────────────────────────────────┐          │
│  │            API Gateway / Load Balancer             │          │
│  │                    (NGINX)                         │          │
│  └────────────────────┬───────────────────────────────┘          │
│                       │                                           │
│  ┌────────────────────┴───────────────────────────────┐          │
│  │              API Service Layer                      │          │
│  └────────────────────────────────────────────────────┘          │
│                       │                                           │
│  ┌────────────────────┴───────────────────────────────┐          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │          │
│  │  │ Auth     │  │ Security │  │ Threat Intel     │ │          │
│  │  │ Service  │  │ Analysis │  │ Service          │ │          │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │          │
│  │                                                     │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │          │
│  │  │ User     │  │ Audit    │  │ Notification     │ │          │
│  │  │ Management
│  │ Management  │  │ Service          │ │          │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │          │
│  │                                                     │          │
│  └────────────────────────────────────────────────────┘          │
│  Backend (FastAPI - Python 3.11+)                               │
└───────────────────────┬──────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────────┐ ┌───▼────────┐ ┌──▼─────────────┐
│   PostgreSQL   │ │   Redis    │ │  File Storage  │
│   (Primary DB) │ │  (Cache)   │ │  (S3/MinIO)    │
└────────────────┘ └────────────┘ └────────────────┘
        │               │
        └───────────────┴─────────────────────────┐
                                                   │
                      ┌────────────────────────────┤
                      │                            │
        ┌─────────────▼──────────┐   ┌────────────▼──────┐
        │  Message Queue (RabbitMQ) │  │ External APIs    │
        │  (Async Tasks)            │  │ (OpenAI, etc)    │
        └──────────────────────────┘  └──────────────────┘
```

## Service Boundaries

### 1. **Authentication & Authorization Service**
- **Responsibility**: User authentication, JWT token management, role-based access control
- **Key Features**:
  - OAuth2 integration (Google, GitHub)
  - JWT token generation and validation
  - Role-based access control (Admin, Analyst, Viewer)
  - Session management
- **Database**: Users, Roles, Permissions tables
- **API Endpoints**: `/api/v1/auth/*`

### 2. **Security Analysis Service**
- **Responsibility**: Core security analysis and vulnerability assessment
- **Key Features**:
  - Threat scanning and detection
  - Vulnerability assessment
  - Security score calculation
  - Risk scoring and prioritization
- **Database**: Scans, Vulnerabilities, Threats tables
- **API Endpoints**: `/api/v1/security/*`

### 3. **Threat Intelligence Service**
- **Responsibility**: Threat data aggregation and intelligence
- **Key Features**:
  - Threat data collection
  - Indicator of Compromise (IoC) tracking
  - Threat correlation
  - Intelligence reports
- **Database**: Threat Data, IoCs, Reports tables
- **API Endpoints**: `/api/v1/threats/*`

### 4. **User Management Service**
- **Responsibility**: User profiles and organization management
- **Key Features**:
  - User CRUD operations
  - Organization management
  - Team management
  - User preferences and settings
- **Database**: Users, Organizations, Teams tables
- **API Endpoints**: `/api/v1/users/*`

### 5. **Audit & Logging Service**
- **Responsibility**: System auditing and compliance logging
- **Key Features**:
  - Action logging
  - Change tracking
  - Compliance audit trails
  - Activity analytics
- **Database**: Audit Logs table
- **API Endpoints**: `/api/v1/audit/*`

## Database Schema Overview

### Core Tables

```
Users
├── id (UUID, PK)
├── email (unique)
├── password_hash
├── first_name
├── last_name
├── role (enum)
├── organization_id (FK)
├── is_active
├── created_at
└── updated_at

Organizations
├── id (UUID, PK)
├── name
├── industry
├── size
├── subscription_tier
├── created_at
└── updated_at

Security Scans
├── id (UUID, PK)
├── organization_id (FK)
├── scan_type (enum)
├── status (enum)
├── start_time
├── end_time
├── results_summary
└── created_at

Vulnerabilities
├── id (UUID, PK)
├── scan_id (FK)
├── severity (enum: critical, high, medium, low)
├── title
├── description
├── affected_component
├── remediation
└── discovered_at

Threats
├── id (UUID, PK)
├── threat_name
├── threat_type (enum)
├── severity
├── description
├── last_seen
└── created_at

Audit Logs
├── id (UUID, PK)
├── user_id (FK)
├── action (enum)
├── resource_type
├── resource_id
├── changes (JSON)
├── timestamp
└── ip_address
```

## API Layer Design

### REST API Principles

- **Versioning**: URL-based versioning (`/api/v1/`, `/api/v2/`)
- **Resource-Oriented Design**: Operations on resources (users, scans, threats)
- **Standard HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **JSON Payloads**: All request/response bodies in JSON
- **Consistent Naming**: camelCase for JSON fields, kebab-case for URLs

### Authentication Flow

```
1. User Login
   POST /api/v1/auth/login
   Body: { email, password }
   Response: { access_token, refresh_token, expires_in }

2. Access Protected Resources
   GET /api/v1/security/scans
   Header: Authorization: Bearer <access_token>

3. Refresh Token
   POST /api/v1/auth/refresh
   Body: { refresh_token }
   Response: { access_token, expires_in }

4. Logout
   POST /api/v1/auth/logout
   Header: Authorization: Bearer <access_token>
```

### Authorization Model (Role-Based Access Control)

```
Roles:
├── Admin
│   └── Full system access, user management, billing
├── Analyst
│   └── View/create/modify security analyses
├── Viewer
│   └── Read-only access to reports and data
└── Integrator
    └── API access for third-party integrations
```

### API Versioning Strategy

- **Current Version**: `/api/v1/`
- **Deprecation Policy**: 2 major versions supported simultaneously
- **Breaking Changes**: Only in major versions
- **Deprecation Headers**: `Deprecation`, `Sunset` headers in responses

### Error Response Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "status": 404,
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-12345-abcde",
    "details": {
      "resource_type": "Security Scan",
      "resource_id": "scan-123"
    }
  }
}
```

### Rate Limiting Approach

- **Strategy**: Token bucket algorithm
- **Limits**:
  - Authenticated users: 1000 requests per hour
  - Anonymous users: 100 requests per hour
  - Burst: 50 requests per minute
- **Response Headers**:
  - `X-RateLimit-Limit`: Max requests per hour
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp of limit reset

## Data Flow for Demo Scenario

### Scenario: Running a Security Scan

```
1. User initiates scan via web UI
   Frontend → POST /api/v1/security/scans/initiate
   
2. API validates request and creates scan record
   Backend → DB: INSERT into scans
   
3. Scan job enqueued for processing
   Backend → Message Queue: Enqueue scan_job
   
4. Worker processes scan asynchronously
   Worker → External Services: Run security checks
   
5. Results stored in database
   Worker → DB: INSERT vulnerabilities
   
6. WebSocket notification sent to client
   Backend → Frontend: SCAN_COMPLETE event
   
7. User views results
   Frontend → GET /api/v1/security/scans/{scan_id}/results
   
8. Results displayed and can be exported
   Frontend: Generate PDF/CSV report
```

## Technology Choices and Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | Next.js 14+ | SSR, excellent DX, built-in routing, TypeScript support |
| Backend | FastAPI | High performance, async support, automatic API docs, type hints |
| Database | PostgreSQL | ACID compliance, complex queries, reliability, scalability |
| Cache | Redis | High-speed caching, pub/sub for notifications, session storage |
| Authentication | JWT + OAuth2 | Stateless, scalable, industry standard, secure |
| Message Queue | RabbitMQ | Reliability, multiple consumer support, asynchronous processing |
| API Documentation | OpenAPI/Swagger | Auto-generated, interactive, industry standard |
| Containerization | Docker | Consistency, isolation, scalability, DevOps friendly |
| Monitoring | Prometheus + Grafana | Time-series metrics, alerting, visualization |
| Logging | ELK Stack | Centralized logging, powerful search, analysis |

## Scalability Notes for Production

### Horizontal Scaling
- **Stateless Design**: All services are stateless for easy scaling
- **Load Balancing**: Multiple backend instances behind load balancer
- **Database Replication**: Read replicas for query scaling
- **Caching Layer**: Redis cluster for distributed caching

### Vertical Scaling
- **Resource Optimization**: FastAPI handles multiple async requests efficiently
- **Connection Pooling**: Database connection pooling prevents resource exhaustion
- **Memory Management**: Careful memory profiling and optimization

### Performance Optimization
- **API Response Caching**: Frequently accessed data cached in Redis
- **Database Indexing**: Strategic indexes on common query patterns
- **Async Processing**: Long-running tasks processed asynchronously
- **CDN Integration**: Static assets served via CDN

### Security Considerations
- **TLS/HTTPS**: All external communication encrypted
- **API Rate Limiting**: Prevents abuse and DDoS attacks
- **Input Validation**: All user inputs validated server-side
- **SQL Injection Prevention**: Parameterized queries throughout
- **CORS Policy**: Strict CORS headers for frontend communication
- **Secret Management**: Environment variables, no secrets in code

### Monitoring & Observability
- **Health Checks**: Regular health checks for all services
- **Distributed Tracing**: Track requests across services
- **Application Metrics**: Monitor key performance indicators
- **Error Tracking**: Centralized error logging and alerting
- **Audit Logging**: All sensitive operations logged

## Deployment Architecture

```
Production Environment:
├── Kubernetes Cluster
│   ├── Frontend Pods (Next.js)
│   ├── Backend Pods (FastAPI)
│   ├── Worker Pods (Celery/Background jobs)
│   └── Database Pods (PostgreSQL)
├── Managed Services
│   ├── Redis Cluster
│   ├── RabbitMQ Service
│   └── S3/Object Storage
└── Observability
    ├── Prometheus
    ├── Grafana
    └── ELK Stack
```

## Summary

This architecture provides:
- ✅ Scalability for growth from MVP to enterprise scale
- ✅ Clear separation of concerns for maintainability
- ✅ Asynchronous processing for performance
- ✅ Security by design with multiple layers
- ✅ Observable and monitorable system
- ✅ Cloud-native and containerized
- ✅ Modern tech stack with strong community support
