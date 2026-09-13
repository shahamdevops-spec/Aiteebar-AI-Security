# API Design Guide - Aiteebar AI Security

## REST API Principles

The Aiteebar AI Security API follows RESTful design principles for consistency, predictability, and ease of use.

### Core Principles

1. **Resource-Oriented Design**
   - Every resource has a unique URL
   - Use nouns for endpoints, not verbs
   - Example: `/api/v1/security-scans` not `/api/v1/getScan`

2. **Standard HTTP Methods**
   - `GET` - Retrieve resources
   - `POST` - Create new resources
   - `PUT` - Replace entire resources
   - `PATCH` - Partial resource updates
   - `DELETE` - Remove resources

3. **Consistent Naming**
   - API paths: kebab-case (`/security-scans`)
   - JSON fields: camelCase (`securityScanId`)
   - Query parameters: camelCase (`sortBy`, `filterBy`)

4. **URL Structure**
   ```
   /api/{version}/{resource}/{resource-id}/{sub-resource}
   /api/v1/security-scans/scan-123/results
   /api/v1/users/user-456/organizations
   ```

## Authentication Flow

### Overview
The API uses JWT (JSON Web Tokens) for stateless authentication with support for OAuth2 integration.

### Login Process

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "accessToken": "eyJhbGc...",
  "refreshToken": "eyJhbGc...",
  "expiresIn": 86400,
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "analyst"
  }
}
```

### Token Usage

```http
GET /api/v1/security-scans
Authorization: Bearer eyJhbGc...
Content-Type: application/json

Response: 200 OK
[
  {
    "id": "scan-123",
    "type": "vulnerability",
    "status": "completed",
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```

### Token Refresh

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGc..."
}

Response: 200 OK
{
  "accessToken": "eyJhbGc...",
  "expiresIn": 86400
}
```

### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{}

Response: 200 OK
{
  "message": "Logged out successfully"
}
```

### OAuth2 Integration

```http
GET /api/v1/auth/oauth/google
Query: ?redirectUrl=https://app.example.com/callback

Response: 302 Redirect
Location: https://accounts.google.com/o/oauth2/auth?...

# After user authenticates with Google
GET /api/v1/auth/oauth/callback
Query: ?code=4/0AY-e8...&state=abc123

Response: 302 Redirect
Location: https://app.example.com/callback?token=eyJhbGc...
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-123",
    "email": "user@example.com",
    "role": "analyst",
    "organization_id": "org-456",
    "iat": 1705316400,
    "exp": 1705402800
  },
  "signature": "..."
}
```

## Authorization Model (Role-Based Access Control)

### Role Definitions

#### 1. Admin
- **Permissions**: Full system access
- **Capabilities**:
  - User management (create, read, update, delete)
  - Organization settings
  - Billing and subscription
  - System configuration
  - View all scans and reports
  - Manage other users and roles
- **API Access**: All endpoints
- **Example**: `GET /api/v1/users` ✅

#### 2. Analyst
- **Permissions**: Security operations and analysis
- **Capabilities**:
  - Create and manage security scans
  - View and analyze vulnerabilities
  - Create and share reports
  - Manage team members (limited)
  - Cannot manage billing or system settings
- **API Access**: Most endpoints except admin operations
- **Example**: `POST /api/v1/security-scans` ✅, `DELETE /api/v1/users/user-123` ❌

#### 3. Viewer
- **Permissions**: Read-only access
- **Capabilities**:
  - View security scans
  - View reports and results
  - View threat intelligence
  - Cannot create or modify resources
  - Cannot manage users
- **API Access**: Only GET endpoints on permitted resources
- **Example**: `GET /api/v1/security-scans` ✅, `POST /api/v1/security-scans` ❌

#### 4. Integrator
- **Permissions**: API-only access for third-party integration
- **Capabilities**:
  - Call API endpoints programmatically
  - Limited to specific integrations
  - No web UI access
  - API key based authentication
- **API Access**: Specific endpoints based on integration scope
- **Example**: Webhook triggers for automated scanning

### Permission Matrix

| Endpoint | Admin | Analyst | Viewer | Integrator |
|----------|-------|---------|--------|------------|
| `GET /security-scans` | ✅ | ✅ | ✅ | ✅ |
| `POST /security-scans` | ✅ | ✅ | ❌ | ✅ |
| `PATCH /security-scans/{id}` | ✅ | ✅ | ❌ | ❌ |
| `DELETE /security-scans/{id}` | ✅ | ✅ | ❌ | ❌ |
| `GET /users` | ✅ | ❌ | ❌ | ❌ |
| `POST /users` | ✅ | ❌ | ❌ | ❌ |
| `PATCH /users/{id}` | ✅ | ✅ (self) | ❌ | ❌ |
| `DELETE /users/{id}` | ✅ | ❌ | ❌ | ❌ |
| `GET /organizations` | ✅ | ✅ | ✅ | ✅ |
| `PATCH /organizations/{id}` | ✅ | ❌ | ❌ | ❌ |

### Authorization Check Example

```python
# In FastAPI endpoint
@router.post("/security-scans")
async def create_scan(
    scan: ScanCreate,
    current_user: User = Depends(get_current_user)
):
    # Check if user is Analyst or Admin
    if current_user.role not in [Role.ANALYST, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Create scan...
    return created_scan
```

## API Versioning Strategy

### Version Format
- URL-based: `/api/v1/`, `/api/v2/`, etc.
- Current version: `v1`
- Next version in development: `v2`

### Versioning Rules

1. **Breaking Changes** → Major Version Bump
   - Removing endpoints
   - Changing response schema
   - Changing parameter types
   - Example: `/api/v1/` → `/api/v2/`

2. **Non-Breaking Changes** → Minor Version (no version change)
   - Adding new endpoints
   - Adding optional fields
   - Adding new query parameters
   - Example: Both available in `/api/v1/`

3. **Bug Fixes** → Patch Version (no version change)
   - Fixing response formatting
   - Performance improvements
   - Security patches

### Deprecation Policy

```
Current Version (v1):       ✅ Active Support
Previous Version (v0):      ⚠️  Deprecation Period (6 months)
Old Version (v-1 and older): ❌ Unsupported
```

### Deprecation Headers

When deprecating an API version, include these headers:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 01 Jul 2024 23:59:59 GMT
Link: </api/v2/...>; rel="successor-version"

{
  "data": [...],
  "_deprecation": {
    "message": "This API version is deprecated",
    "migrateUrl": "https://docs.example.com/migration-guide",
    "sunsetDate": "2024-07-01T23:59:59Z"
  }
}
```

## Error Response Format

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "status": 400,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-12345-abcde",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_FAILED` | 401 | Missing or invalid credentials |
| `AUTHORIZATION_FAILED` | 403 | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Resource already exists or conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Response Examples

```json
// 400 - Validation Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "status": 400,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-12345-abcde",
    "details": {
      "errors": [
        {
          "field": "email",
          "message": "Must be a valid email address"
        },
        {
          "field": "password",
          "message": "Must be at least 8 characters"
        }
      ]
    }
  }
}
```

```json
// 401 - Authentication Failed
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials",
    "status": 401,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-12345-abcde"
  }
}
```

```json
// 403 - Authorization Failed
{
  "error": {
    "code": "AUTHORIZATION_FAILED",
    "message": "You do not have permission to access this resource",
    "status": 403,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-12345-abcde",
    "details": {
      "requiredRole": "analyst",
      "userRole": "viewer"
    }
  }
}
```

```json
// 404 - Not Found
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Security scan not found",
    "status": 404,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-12345-abcde",
    "details": {
      "resourceType": "SecurityScan",
      "resourceId": "scan-999"
    }
  }
}
```

## Rate Limiting Approach

### Rate Limiting Strategy
- **Algorithm**: Token bucket
- **Scope**: Per user / Per IP address
- **Window**: Hourly limit with per-minute burst

### Default Limits

| User Type | Hourly Limit | Per Minute Burst | Notes |
|-----------|--------------|------------------|-------|
| Authenticated | 1000 | 50 | Full API access |
| Free Tier | 100 | 10 | Limited features |
| Premium Tier | 5000 | 200 | Priority processing |
| API Key | 10000 | 500 | Integrations |
| Anonymous | 20 | 5 | No auth required |

### Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1705402800
X-RateLimit-ResetAfter: 3600

{
  "data": [...]
}
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705402800
X-RateLimit-ResetAfter: 3600
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "status": 429,
    "timestamp": "2024-01-15T10:30:00Z",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "resetTime": "2024-01-15T11:30:00Z"
    }
  }
}
```

## Example Endpoints Structure

### Security Scans

```http
# Create a new scan
POST /api/v1/security-scans
Content-Type: application/json
Authorization: Bearer token

{
  "name": "Full System Scan",
  "scanType": "vulnerability",
  "targets": ["192.168.1.0/24"],
  "intensity": "high"
}

Response: 201 Created
{
  "id": "scan-123",
  "name": "Full System Scan",
  "scanType": "vulnerability",
  "status": "pending",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

```http
# List scans with filtering and pagination
GET /api/v1/security-scans?status=completed&limit=10&offset=0&sortBy=createdAt&sortOrder=desc
Authorization: Bearer token

Response: 200 OK
{
  "data": [
    {
      "id": "scan-123",
      "name": "Full System Scan",
      "status": "completed",
      "createdAt": "2024-01-15T10:30:00Z",
      "results": {
        "vulnerabilities": 42,
        "severity": "high"
      }
    }
  ],
  "pagination": {
    "total": 125,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

```http
# Get scan details
GET /api/v1/security-scans/scan-123
Authorization: Bearer token

Response: 200 OK
{
  "id": "scan-123",
  "name": "Full System Scan",
  "status": "completed",
  "createdAt": "2024-01-15T10:30:00Z",
  "completedAt": "2024-01-15T10:45:00Z",
  "results": {
    "vulnerabilities": 42,
    "criticalCount": 3,
    "highCount": 12,
    "mediumCount": 27
  }
}
```

```http
# Update scan configuration
PATCH /api/v1/security-scans/scan-123
Content-Type: application/json
Authorization: Bearer token

{
  "name": "Updated Scan Name"
}

Response: 200 OK
{
  "id": "scan-123",
  "name": "Updated Scan Name",
  "status": "completed"
}
```

```http
# Delete scan
DELETE /api/v1/security-scans/scan-123
Authorization: Bearer token

Response: 204 No Content
```

### Pagination and Filtering

```http
GET /api/v1/security-scans?limit=20&offset=40&sortBy=createdAt&sortOrder=desc&filter[status]=completed&filter[severity]=high

Query Parameters:
- limit: 20 (max results per page)
- offset: 40 (skip first 40 results)
- sortBy: createdAt (field to sort by)
- sortOrder: desc (asc or desc)
- filter[status]: completed
- filter[severity]: high

Response: 200 OK
{
  "data": [...],
  "pagination": {
    "total": 500,
    "limit": 20,
    "offset": 40,
    "hasMore": true,
    "nextUrl": "/api/v1/security-scans?limit=20&offset=60&..."
  }
}
```

## API Documentation Standards

All endpoints must include:
- Clear description of purpose
- Required and optional parameters
- Request/response examples
- Error cases and responses
- Rate limiting information
- Required authentication/authorization

### API Documentation Tools
- **Swagger/OpenAPI**: Auto-generated at `/api/v1/docs`
- **ReDoc**: Alternative UI at `/api/v1/redoc`
- **Postman**: Collection available in `/postman/`

## Best Practices

1. **Always validate inputs** server-side
2. **Use appropriate HTTP status codes**
3. **Return meaningful error messages**
4. **Include request IDs** for debugging
5. **Use pagination** for large result sets
6. **Cache appropriately** with Cache-Control headers
7. **Document breaking changes** in release notes
8. **Support CORS** properly
9. **Use HTTPS** in production
10. **Implement idempotency** for POST requests with idempotency keys
