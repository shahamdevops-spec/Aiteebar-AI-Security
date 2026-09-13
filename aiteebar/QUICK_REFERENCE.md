# Aiteebar Docker Quick Reference

Fast reference guide for common Docker operations.

## 🚀 Get Started (5 minutes)

```powershell
# Windows PowerShell
.\scripts\generate-env.ps1
docker-compose up -d
docker-compose ps
```

```bash
# Linux/macOS
bash scripts/generate-env.sh
docker-compose up -d
docker-compose ps
```

## 📍 Service URLs

| Service | URL | Username/Info |
|---------|-----|---------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Swagger Docs | http://localhost:8000/docs | - |
| API ReDoc | http://localhost:8000/redoc | - |
| Database UI (Adminer) | http://localhost:8080 | user: `aiteebar` |
| Ollama AI | http://localhost:11434/api | - |

## 🔧 Most Common Commands

### Check Status
```bash
docker-compose ps                    # List all services
docker-compose ps backend            # Specific service
docker stats                         # Resource usage
```

### View Logs
```bash
docker-compose logs -f               # All services
docker-compose logs -f backend       # Specific service
docker-compose logs --tail=50        # Last 50 lines
```

### Start/Stop
```bash
docker-compose up -d                 # Start all (background)
docker-compose down                  # Stop all (keeps data)
docker-compose down -v               # Stop and delete volumes
docker-compose restart               # Restart all
docker-compose restart backend       # Restart one service
```

### Execute Commands
```bash
# Python shell
docker-compose exec backend python

# Database shell
docker-compose exec postgres psql -U aiteebar -d aiteebar_db

# Bash shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Run specific command
docker-compose exec backend pip list
docker-compose exec frontend npm list
```

## 🗄️ Database Operations

### Backup Database
```bash
docker-compose exec -T postgres pg_dump -U aiteebar aiteebar_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U aiteebar aiteebar_db < backup.sql
```

### Connect to Database
```bash
docker-compose exec postgres psql -U aiteebar -d aiteebar_db
```

### Reset Database
```powershell
# Windows
.\scripts\reset-db.ps1 -Force
```

```bash
# Linux/macOS
bash scripts/reset-db.sh
```

### Run Migrations
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic current
docker-compose exec backend alembic downgrade -1
```

## 🆘 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build backend

# Check health
docker-compose ps
```

### Port Already in Use
```bash
# Find process
lsof -i :3000              # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Change port in .env
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

### Database Connection Failed
```bash
# Check database is running
docker-compose exec postgres pg_isready -U aiteebar

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
docker-compose exec backend curl http://localhost:8000/health

# Check CORS in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Check API URL in frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🐳 Optional Services

### Enable Ollama AI
```bash
docker-compose --profile with-ollama up -d
```

### Enable Redis Cache
```bash
docker-compose --profile with-redis up -d
```

### Enable Adminer (DB UI)
```bash
docker-compose --profile with-adminer up -d
```

### Enable All Optional Services
```bash
docker-compose --profile with-ollama --profile with-redis --profile with-adminer up -d
```

## 📊 Docker Management

### Clean Up
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a

# Remove unused + volumes
docker system prune -a --volumes
```

### Inspect Services
```bash
# Detailed service info
docker-compose ps -a

# Service logs with timestamps
docker-compose logs --timestamps -f backend

# Resource usage
docker stats

# Network information
docker network ls
docker network inspect aiteebar-network
```

## 💾 Volumes Management

### Persist Data
Data is automatically persisted in volumes:
- `postgres_data` - PostgreSQL database
- `redis_data` - Redis cache (if enabled)
- `ollama_data` - Ollama models (if enabled)

### Inspect Volumes
```bash
docker volume ls
docker volume inspect aiteebar_postgres_data
```

### Backup Volume
```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 📝 Configuration

### View Current Configuration
```bash
# Show environment variables
docker-compose config

# Show specific service config
grep -A 20 "backend:" docker-compose.yml
```

### Update Environment
```bash
# Edit .env file
nano .env  # or your preferred editor

# Restart services to apply
docker-compose restart
```

## 🔍 Debugging

### Enable Debug Mode
```bash
# Edit .env
BACKEND_DEBUG=true
DEBUG=true

# Restart backend
docker-compose restart backend
```

### View Build Logs
```bash
# Build with verbose output
docker-compose build --no-cache --progress=plain backend
```

### Check Container Internals
```bash
# List files in container
docker-compose exec backend ls -la

# Check installed packages
docker-compose exec backend pip list
docker-compose exec frontend npm list

# View environment variables
docker-compose exec backend env | sort
```

## 🚀 Development Workflow

### After Code Changes
```bash
# Backend Python changes
docker-compose exec backend pip install -r requirements.txt
docker-compose restart backend

# Frontend Node changes
docker-compose exec frontend npm install
# (Frontend auto-reloads)

# Database schema changes
docker-compose exec backend alembic revision --autogenerate -m "message"
docker-compose exec backend alembic upgrade head
```

### Run Tests
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

### Code Quality
```bash
# Backend linting
docker-compose exec backend flake8
docker-compose exec backend black --check .
docker-compose exec backend mypy .

# Frontend linting
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format
```

## 📋 Environment Variables Quick Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| DATABASE_URL | PostgreSQL connection string | Database |
| JWT_SECRET_KEY | (generated) | Auth tokens |
| BACKEND_DEBUG | true | Debug mode |
| NEXT_PUBLIC_API_URL | http://localhost:8000/api | Frontend API |
| CORS_ORIGINS | http://localhost:3000 | CORS policy |
| OLLAMA_BASE_URL | http://ollama:11434 | AI runtime |

See `.env.example` for complete list.

## 🆘 Emergency Commands

### Nuclear Option (⚠️ Deletes Everything)
```bash
# Stop, remove, delete volumes
docker-compose down -v

# Clean up images
docker system prune -a --volumes

# Start fresh
docker-compose up -d --build
```

### Quick Service Restart
```bash
docker-compose restart
```

### Force Pull Latest Images
```bash
docker-compose pull
docker-compose up -d --build
```

## 📚 Detailed Documentation

- **Full Guide:** See `docker/README.md`
- **Development Setup:** See `docs/DEVELOPMENT.md`
- **Architecture:** See `docs/ARCHITECTURE.md`
- **Setup Summary:** See `DOCKER_SETUP_SUMMARY.md`

## 💡 Pro Tips

1. **Always use `-d` flag:** `docker-compose up -d` runs in background
2. **Follow logs:** `docker-compose logs -f` to debug issues
3. **Check health:** `docker-compose ps` shows service status
4. **Backup first:** Always backup database before reset
5. **Use profiles:** Enable optional services only when needed
6. **Monitor resources:** Use `docker stats` to watch usage
7. **Clean regularly:** Run `docker system prune -a` weekly

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Production Ready ✅
