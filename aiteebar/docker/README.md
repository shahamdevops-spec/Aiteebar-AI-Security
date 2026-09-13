# Docker Setup Guide - Aiteebar AI Security

Complete guide for running Aiteebar AI Security using Docker and Docker Compose.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Service Overview](#service-overview)
4. [Configuration](#configuration)
5. [Common Commands](#common-commands)
6. [Viewing Logs](#viewing-logs)
7. [Database Operations](#database-operations)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)

## 📦 Prerequisites

- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 1.29+ (included with Docker Desktop)
- **Git**: 2.30+
- **Disk Space**: Minimum 5GB for images and volumes
- **RAM**: Minimum 4GB available (8GB recommended)

### Verify Installation

```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/shahamdevops-spec/Aiteebar-AI-Security.git
cd aiteebar
```

### 2. Generate Environment File

**For Windows (PowerShell):**
```powershell
.\scripts\generate-env.ps1
```

**For Linux/macOS (Bash):**
```bash
bash scripts/generate-env.sh
```

Or manually:
```bash
cp .env.example .env
# Edit .env with your preferred editor and update values
```

### 3. Start All Services

```bash
docker-compose up -d
```

### 4. Verify Services Are Running

```bash
docker-compose ps
```

You should see:
- `aiteebar-postgres` - ✓ running
- `aiteebar-backend` - ✓ running  
- `aiteebar-frontend` - ✓ running
- `aiteebar-adminer` - ✓ running (optional)
- `aiteebar-ollama` - (optional, if enabled)

### 5. Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API ReDoc | http://localhost:8000/redoc | Alternative docs |
| Database UI | http://localhost:8080 | PostgreSQL management |
| Ollama | http://localhost:11434 | AI model API |

## 🏗️ Service Overview

### PostgreSQL Database (`aiteebar-postgres`)

- **Image**: postgres:15-alpine
- **Port**: 5432
- **Purpose**: Primary data storage
- **Volumes**: `postgres_data:/var/lib/postgresql/data`
- **Health Check**: Active

**Connection String:**
```
postgresql://aiteebar:aiteebar_password@postgres:5432/aiteebar_db
```

### FastAPI Backend (`aiteebar-backend`)

- **Image**: Custom (built from `backend/Dockerfile`)
- **Port**: 8000
- **Purpose**: REST API server
- **Dependencies**: PostgreSQL, Redis (optional)
- **Environment**: Development mode with auto-reload
- **Volumes**: `./backend:/app` (live reload)

**Health Check Endpoint:**
```
GET http://localhost:8000/health
```

### Next.js Frontend (`aiteebar-frontend`)

- **Image**: Custom (built from `frontend/Dockerfile`)
- **Port**: 3000
- **Purpose**: Web application interface
- **Dependencies**: Backend API
- **Volumes**: `./frontend:/app` (live reload)

**Health Check Endpoint:**
```
GET http://localhost:3000
```

### PostgreSQL UI - Adminer (`aiteebar-adminer`)

- **Image**: adminer:latest
- **Port**: 8080
- **Purpose**: Database management interface
- **Profile**: `with-adminer` (optional)

**Login Credentials:**
- System: PostgreSQL
- Server: `postgres`
- Username: `aiteebar`
- Password: (from `.env` `POSTGRES_PASSWORD`)
- Database: `aiteebar_db`

### Ollama AI Runtime (`aiteebar-ollama`)

- **Image**: ollama/ollama:latest
- **Port**: 11434
- **Purpose**: Local AI model inference
- **Profile**: `with-ollama` (optional)
- **Volumes**: `ollama_data:/root/.ollama`

**Base URL:** `http://ollama:11434`

### Redis Cache (`aiteebar-redis`)

- **Image**: redis:7-alpine
- **Port**: 6379
- **Purpose**: Session storage and caching
- **Profile**: `with-redis` (optional)
- **Volumes**: `redis_data:/data`

## ⚙️ Configuration

### Environment Variables

All configuration is managed through `.env` file. Key variables:

```bash
# Database
POSTGRES_USER=aiteebar
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=aiteebar_db

# Backend
JWT_SECRET_KEY=your-secure-jwt-key
BACKEND_DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NODE_ENV=development

# AI/ML
OLLAMA_BASE_URL=http://ollama:11434
OPENAI_API_KEY=sk-your-key
```

### Enable Optional Services

Use Docker Compose profiles to enable optional services:

```bash
# With Ollama AI support
docker-compose --profile with-ollama up -d

# With Redis caching
docker-compose --profile with-redis up -d

# With database UI
docker-compose --profile with-adminer up -d

# All optional services
docker-compose --profile with-ollama --profile with-redis --profile with-adminer up -d
```

## 🔧 Common Commands

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Start with specific profile
docker-compose --profile with-ollama up -d

# Start and watch output
docker-compose up

# Start specific service only
docker-compose up -d backend
```

### Stop Services

```bash
# Stop all services (keeps volumes)
docker-compose down

# Stop with volume cleanup (removes data!)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Restart and rebuild
docker-compose up -d --build
```

### View Service Status

```bash
# List all services and their status
docker-compose ps

# Show detailed information
docker-compose ps -a

# Check specific service
docker-compose ps backend
```

### Execute Commands in Container

```bash
# Run command in backend container
docker-compose exec backend python -c "import sys; print(sys.version)"

# Access Python shell
docker-compose exec backend python

# Access PostgreSQL psql
docker-compose exec postgres psql -U aiteebar -d aiteebar_db

# Access application bash
docker-compose exec backend bash
```

## 📋 Viewing Logs

### View All Logs

```bash
# View latest logs from all services
docker-compose logs

# View last 100 lines
docker-compose logs --tail=100

# Follow logs (like tail -f)
docker-compose logs -f
```

### View Specific Service Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres

# Combined with timestamp
docker-compose logs -f --timestamps backend
```

### View Logs Since Time

```bash
# Logs from the last 10 minutes
docker-compose logs --since 10m

# Logs from specific datetime
docker-compose logs --since 2024-01-15T10:00:00
```

## 💾 Database Operations

### Backup Database

```bash
# Backup to SQL file
docker-compose exec -T postgres pg_dump -U aiteebar aiteebar_db > backup.sql

# Compressed backup
docker-compose exec -T postgres pg_dump -U aiteebar aiteebar_db | gzip > backup.sql.gz
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T postgres psql -U aiteebar aiteebar_db < backup.sql

# Restore from compressed backup
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U aiteebar aiteebar_db
```

### Connect to Database

```bash
# Interactive PostgreSQL shell
docker-compose exec postgres psql -U aiteebar -d aiteebar_db

# Run SQL query
docker-compose exec -T postgres psql -U aiteebar -d aiteebar_db -c "SELECT version();"
```

### Run Database Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Rollback last migration
docker-compose exec backend alembic downgrade -1

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Reset Database

**Warning: This deletes all data!**

**PowerShell (Windows):**
```powershell
.\scripts\reset-db.ps1
```

**Bash (Linux/macOS):**
```bash
bash scripts/reset-db.sh
```

Or manually:
```bash
# Stop and remove containers with volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Check health status
docker-compose ps

# Restart service
docker-compose restart <service-name>

# Rebuild image
docker-compose up -d --build <service-name>
```

### Port Already in Use

```bash
# Find process using port
lsof -i :<port>  # macOS/Linux
netstat -ano | findstr :<port>  # Windows

# Change port in .env
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433
```

### Database Connection Failed

```bash
# Check database health
docker-compose exec postgres pg_isready -U aiteebar

# Check logs
docker-compose logs postgres

# Verify connection string in .env
DATABASE_URL=postgresql://aiteebar:aiteebar_password@postgres:5432/aiteebar_db
```

### Frontend Can't Connect to Backend

```bash
# Check backend is running
docker-compose exec backend curl http://localhost:8000/health

# Verify API URL in .env
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Check CORS configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Check network
docker-compose exec frontend curl http://backend:8000/health
```

### Out of Disk Space

```bash
# Clean up unused images and volumes
docker system prune -a

# More aggressive cleanup
docker system prune --volumes

# Check disk usage
docker system df
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Limit resource usage in docker-compose.yml
# Add to service:
#   deploy:
#     resources:
#       limits:
#         cpus: '0.5'
#         memory: 512M
```

### Rebuild Everything

```bash
# Complete reset
docker-compose down -v
docker system prune -a --volumes

# Start fresh
docker-compose up -d --build
```

## 🚢 Production Deployment

### Before Production

1. **Update Environment Variables:**
   ```bash
   # Use environment-specific .env.production
   ENVIRONMENT=production
   BACKEND_DEBUG=false
   NODE_ENV=production
   JWT_SECRET_KEY=<strong-random-key>
   ```

2. **Security Checklist:**
   - [ ] Change all default passwords
   - [ ] Update JWT secret with secure value
   - [ ] Enable HTTPS/TLS
   - [ ] Configure proper CORS origins
   - [ ] Enable rate limiting
   - [ ] Set up proper logging/monitoring
   - [ ] Use secret manager for credentials

3. **Performance Tuning:**
   ```yaml
   # Increase worker processes
   BACKEND_WORKERS=8
   
   # Adjust rate limits
   RATE_LIMIT_REQUESTS=5000
   
   # Database connection pool
   DATABASE_POOL_SIZE=20
   ```

4. **Monitoring Setup:**
   - [ ] Enable Prometheus metrics
   - [ ] Set up Grafana dashboards
   - [ ] Configure alerting
   - [ ] Enable structured logging (JSON)
   - [ ] Set up error tracking (Sentry)

### Production Deployment Options

**Option 1: Docker Swarm**
```bash
docker swarm init
docker stack deploy -c docker-compose.yml aiteebar
```

**Option 2: Kubernetes**
```bash
kubectl apply -f k8s/
```

**Option 3: Cloud Platforms**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)

## ❓ Getting Help

1. Check logs: `docker-compose logs -f`
2. Review [DEVELOPMENT.md](../docs/DEVELOPMENT.md)
3. Check [ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. Open GitHub issue with:
   - Docker version
   - Docker Compose version
   - OS information
   - Full error logs
   - Steps to reproduce

## 📝 Notes

- Containers use Alpine Linux for minimal size
- All services have health checks enabled
- Volumes persist data across container restarts
- Network `aiteebar-network` allows inter-service communication
- Development builds include live reload for fast iteration
- Production deployments should use multi-stage builds for smaller images
