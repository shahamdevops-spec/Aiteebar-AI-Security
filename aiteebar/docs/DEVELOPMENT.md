# Development Guide - Aiteebar AI Security

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows (with WSL2)
- **Git**: 2.30+
- **Docker & Docker Compose**: 20.10+
- **Node.js**: 18.17+ (for frontend)
- **Python**: 3.11+ (for backend)
- **PostgreSQL**: 14+ (or use Docker)
- **Redis**: 7+ (or use Docker)

### Required Tools
```bash
# Install Node.js (if not using Docker)
# Visit: https://nodejs.org/

# Install Python 3.11+ (if not using Docker)
# Visit: https://www.python.org/downloads/

# Install Docker & Docker Compose
# Visit: https://www.docker.com/products/docker-desktop

# Install Git
# Visit: https://git-scm.com/
```

## Local Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd "C:\Users\Ntech\Desktop\Aiteebar AI Security"
cd aiteebar
```

### 2. Copy Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your local values
# For development, defaults in .env.example should work
```

### 3. Setup with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (30-60 seconds)
docker-compose ps

# Verify services
# PostgreSQL: localhost:5432
# Redis: localhost:6379
# Backend: localhost:8000
# Frontend: localhost:3000
```

### 4. Alternative: Setup Without Docker

#### Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

#### Database Setup (PostgreSQL)

```bash
# Install PostgreSQL 14+
# macOS: brew install postgresql@14
# Linux: sudo apt-get install postgresql
# Windows: Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL service
# macOS: brew services start postgresql@14
# Linux: sudo systemctl start postgresql
# Windows: Services > PostgreSQL should start automatically

# Create database and user
createdb aiteebar_db
createuser aiteebar --createdb
psql aiteebar_db -c "ALTER USER aiteebar WITH PASSWORD 'aiteebar_password';"

# Run migrations
cd backend
python -m alembic upgrade head
```

## Running Services Locally

### Using Docker Compose (Recommended)

```bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Individual Service Commands

#### Backend (FastAPI)

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With environment variables
export BACKEND_DEBUG=true
uvicorn app.main:app --reload
```

#### Frontend (Next.js)

```bash
# Development mode
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Build and export static site
npm run export
```

#### Database

```bash
# Connect to database
psql postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of change"

# Rollback last migration
alembic downgrade -1
```

#### Redis

```bash
# Connect to Redis
redis-cli

# Check connection
ping

# Flush all data
FLUSHALL

# View all keys
KEYS *
```

## Database Setup Details

### Initial Setup

```bash
# Create PostgreSQL user and database
sudo -u postgres psql

postgres=# CREATE USER aiteebar WITH PASSWORD 'aiteebar_password';
postgres=# CREATE DATABASE aiteebar_db OWNER aiteebar;
postgres=# GRANT ALL PRIVILEGES ON DATABASE aiteebar_db TO aiteebar;
postgres=# \q
```

### Running Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Check migration history
alembic history

# Downgrade to specific revision
alembic downgrade <revision>
```

### Seeding Sample Data

```bash
# Run seed script (after migrations)
python scripts/seed_database.py

# This will populate:
# - Sample users (admin, analyst, viewer)
# - Sample organizations
# - Sample security scans
# - Sample vulnerabilities
```

### Database Backup & Restore

```bash
# Backup database
pg_dump postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db > backup.sql

# Restore database
psql postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db < backup.sql
```

## Common Development Commands

### Frontend Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Format code
npm run format

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch
```

### Backend Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black .

# Run linter
flake8

# Type checking
mypy .

# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "message"
```

### Docker Commands

```bash
# Build all services
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs

# Follow logs for specific service
docker-compose logs -f backend

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove all data (volumes)
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

## Environment Variables Guide

### Critical for Development

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis cache connection |
| `JWT_SECRET_KEY` | Generate new key | JWT token signing |
| `BACKEND_DEBUG` | `true` | Debug mode for backend |
| `NODE_ENV` | `development` | Frontend environment |

### Generating Secure Keys

```bash
# Generate JWT secret (32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key (32 bytes for AES-256)
python -c "import secrets; print(secrets.token_hex(32))"
```

## Port References

| Service | Port | URL |
|---------|------|-----|
| Frontend (Next.js) | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs (Swagger) | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Adminer (DB UI) | 8080 | http://localhost:8080 |

## Accessing Services

### Frontend
- URL: `http://localhost:3000`
- Default credentials: See seed data

### Backend API
- URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Database UI (Adminer)
- URL: `http://localhost:8080`
- System: PostgreSQL
- Server: `db`
- Username: `aiteebar`
- Password: `aiteebar_password`
- Database: `aiteebar_db`

## Troubleshooting Guide

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process (Linux/macOS)
kill -9 <PID>

# Change port in development
# Frontend: npm run dev -- -p 3001
# Backend: uvicorn app.main:app --port 8001
```

### Issue: Database Connection Failed

```bash
# Check PostgreSQL is running
# macOS: brew services list
# Linux: sudo systemctl status postgresql
# Windows: Services > PostgreSQL (should be running)

# Test connection
psql postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db

# If failed, reset database
dropdb aiteebar_db
createdb aiteebar_db
alembic upgrade head
```

### Issue: Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis-server
# Docker: docker run -d -p 6379:6379 redis
```

### Issue: Module Not Found / Import Errors

```bash
# Backend - Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Frontend - Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Docker Services Won't Start

```bash
# Check Docker daemon
docker --version
docker ps

# Rebuild images
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check logs for errors
docker-compose logs
```

### Issue: Frontend Can't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check CORS configuration in .env
CORS_ORIGINS=http://localhost:3000

# Check API URL in frontend .env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Issue: Database Migrations Failed

```bash
# Check migration status
alembic current

# Downgrade to previous version
alembic downgrade -1

# Check migration files for errors
ls app/database/migrations/versions/

# Recreate migration
alembic revision --autogenerate -m "description"
```

## Performance Tips

### Frontend Optimization
- Use Chrome DevTools to profile
- Enable production builds for testing
- Check Network tab for slow requests
- Use React DevTools to identify re-renders

### Backend Optimization
- Monitor with `uvicorn --log-level info`
- Use `/docs` endpoint for API performance
- Check database query performance with `EXPLAIN ANALYZE`
- Monitor Redis cache hit rate

### Database Optimization
- Use appropriate indexes on frequently queried columns
- Monitor slow query log: `SET log_statement = 'all';`
- Regular VACUUM and ANALYZE: `VACUUM ANALYZE;`

## Useful Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Docker Docs**: https://docs.docker.com/
- **Redis Docs**: https://redis.io/documentation

## Getting Help

1. Check this guide first
2. Check service logs: `docker-compose logs <service>`
3. Check GitHub issues
4. Ask in team chat/Slack
5. Consult service documentation
