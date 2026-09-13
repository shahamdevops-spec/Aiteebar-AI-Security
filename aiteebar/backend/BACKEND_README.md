# Aiteebar AI Security - FastAPI Backend

Production-ready FastAPI backend for AI security analysis and threat intelligence platform.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [Configuration](#configuration)
5. [Running the Server](#running-the-server)
6. [API Documentation](#api-documentation)
7. [Development Guide](#development-guide)

## Overview

**FastAPI Backend** for Aiteebar AI Security with:
- ✅ Production-ready structure
- ✅ Dependency injection
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Database connection pooling
- ✅ Comprehensive exception handling
- ✅ Request/response logging
- ✅ CORS middleware
- ✅ Health check endpoints

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # App initialization
│   ├── main.py                  # FastAPI app with middleware & handlers
│   ├── config.py                # Configuration with Pydantic Settings
│   ├── database.py              # SQLAlchemy setup & session management
│   ├── security.py              # Password hashing & JWT handling
│   ├── exceptions.py            # Custom exception classes
│   ├── dependencies.py          # Dependency injection utilities
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── routers/                 # API route modules
│   ├── services/                # Business logic services
│   ├── engines/                 # Risk, DLP, threat detection engines
│   └── utils/                   # Utility functions
├── alembic/                     # Database migrations
│   ├── env.py                   # Alembic configuration
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration files
├── tests/                       # Test suite
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
└── BACKEND_README.md            # This file
```

## Setup & Installation

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or poetry

### 2. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Verify schema
psql -U aiteebar -d aiteebar_db -c "\dt"
```

### 4. Load Seed Data (Optional)

```bash
# Load demo data
psql -U aiteebar -d aiteebar_db < database/seed_data.sql
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db
DATABASE_POOL_SIZE=5
DATABASE_ECHO=false

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DEBUG=true

# Security
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=development
```

### Configuration Management

Settings are managed in `app/config.py` using Pydantic Settings:

```python
from app.config import settings

print(settings.app_name)
print(settings.jwt_secret_key)
print(settings.is_development)
```

## Running the Server

### Development Mode

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py entry point
python -m app.main
```

### Production Mode

```bash
# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker

```bash
# Build image
docker build -t aiteebar-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET_KEY=... \
  aiteebar-backend
```

## API Documentation

### Health Check

```bash
# Check if API is running
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/health/db
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Development Guide

### Creating a New Route

1. **Create a router** (`app/routers/users.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/")
async def list_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all users"""
    # Implementation
    pass
```

2. **Register in main.py**:

```python
from app.routers import users

app.include_router(users.router)
```

### Creating a Service

1. **Create service** (`app/services/user_service.py`):

```python
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        db_user = User(**user_data.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
```

2. **Use in routes**:

```python
from app.services.user_service import UserService

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)
```

### Authentication

```python
from app.security import create_access_token, verify_password

# Hash password
password_hash = hash_password("mypassword")

# Verify password
if verify_password("mypassword", password_hash):
    # Password matches
    pass

# Create token
token = create_access_token(subject="user@example.com")

# Use in endpoint
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]  # User identifier
    return {"user_id": user_id}
```

### Database Queries

```python
from sqlalchemy import select
from app.models import AIApplication
from app.database import SessionLocal

# Using session
db = SessionLocal()
apps = db.query(AIApplication).filter(AIApplication.risk_level == 'HIGH').all()

# Using select (SQLAlchemy 2.0 style)
stmt = select(AIApplication).where(AIApplication.risk_level == 'HIGH')
apps = db.execute(stmt).scalars().all()
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_users.py::test_create_user
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Check history
alembic history
```

## Middleware & Exception Handling

### Middleware

- **CORS**: Configured for localhost:3000 and 3001
- **Trusted Host**: Restricts requests to trusted hosts
- **Request Logging**: Logs all requests and responses with duration
- **Exception Handling**: Structured error responses

### Exception Handling

```python
from app.exceptions import (
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError,
    DatabaseError,
)

# Raise custom exceptions
raise ValidationError("Invalid email format", details={"field": "email"})
raise ResourceNotFoundError("User", user_id)
raise AuthenticationError("Invalid credentials")
```

## Performance Tips

1. **Use connection pooling** (configured in database.py)
2. **Enable database query caching** with Redis
3. **Use async/await** for I/O operations
4. **Index frequently queried columns** (done in schema)
5. **Paginate large result sets**
6. **Use lazy loading** for relationships

## Common Issues

### Database Connection Errors

```bash
# Check PostgreSQL is running
psql -U aiteebar -d aiteebar_db -c "SELECT 1"

# Verify connection string in .env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### JWT Token Errors

```bash
# Verify secret key length (minimum 32 characters)
# Make sure algorithm matches (HS256 recommended)

JWT_SECRET_KEY=your-super-secret-key-must-be-32-chars-minimum
JWT_ALGORITHM=HS256
```

### Module Import Errors

```bash
# Make sure app directory has __init__.py
# Verify Python path includes backend directory

# From backend directory:
python -c "from app.main import app; print(app.title)"
```

## Deployment

### Docker

```bash
# Build and run
docker-compose up -d backend

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### Kubernetes

```bash
# Create deployment
kubectl apply -f k8s/backend.yaml

# Check status
kubectl get pods -l app=backend

# View logs
kubectl logs -f pod/backend-xxx
```

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **JWT Guide**: https://tools.ietf.org/html/rfc7519

## Support

For issues or questions:
1. Check the logs: `docker-compose logs backend`
2. Verify configuration in `.env`
3. Check database connectivity
4. Review API documentation at `/docs`

---

**Status**: ✅ Production-Ready  
**Last Updated**: 2024-01-15  
**Version**: 0.1.0
