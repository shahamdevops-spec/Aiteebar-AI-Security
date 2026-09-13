# Aiteebar AI Security

A production-ready AI-powered security analysis and threat intelligence platform built with modern web technologies.

## 🚀 Overview

Aiteebar AI Security is an MVP (Minimum Viable Product) designed to provide:

- **Security Analysis**: Advanced threat detection and vulnerability assessment
- **Threat Intelligence**: Real-time threat data aggregation and correlation
- **Risk Management**: Comprehensive risk scoring and prioritization
- **Compliance Tracking**: Audit trails and compliance reporting
- **User Management**: Role-based access control and team collaboration

## 📋 Technology Stack

### Frontend
- **Framework**: Next.js 14+ with React
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query / TanStack Query
- **Package Manager**: npm

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7+
- **Message Queue**: RabbitMQ
- **ORM**: SQLAlchemy
- **API Documentation**: OpenAPI/Swagger

### DevOps
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (for production)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## 📁 Project Structure

```
aiteebar/
├── frontend/                 # Next.js React application
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── pages/               # API routes (if needed)
│   ├── styles/              # Global styles
│   ├── public/              # Static assets
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── api/            # API route definitions
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── database/       # Database configuration
│   │   └── core/           # Core utilities (auth, config)
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Example environment file
│
├── database/               # Database configurations and scripts
│   ├── migrations/         # Database migration files
│   └── seeds/              # Seed data scripts
│
├── docker/                 # Docker configurations
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
├── docs/                   # Project documentation
│   ├── ARCHITECTURE.md     # System architecture
│   ├── DEVELOPMENT.md      # Development guide
│   ├── API_DESIGN.md       # API design documentation
│   └── README.md           # This file
│
├── scripts/                # Utility scripts
│   ├── setup.sh           # Setup script
│   └── seed_database.py   # Database seeding
│
├── .gitignore             # Git ignore rules
├── .env.example           # Example environment variables
└── README.md              # Project README
```

## ⚡ Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/aiteebar-ai-security.git
cd aiteebar

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Services will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Local development setup and commands
- **[API_DESIGN.md](docs/API_DESIGN.md)** - REST API design and specifications

## 🔧 Configuration

### Environment Variables

All required environment variables are documented in `.env.example`. Copy this file to `.env` and configure for your environment.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `NEXT_PUBLIC_API_URL` - Backend API URL (frontend)

## 🚀 Running Services

### Start All Services
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### View Service Logs
```bash
docker-compose logs -f <service-name>
# Example: docker-compose logs -f backend
```

## 🔌 API Access

### Frontend
- **URL**: http://localhost:3000
- **Purpose**: Web application interface

### Backend API
- **URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Database Management (Adminer)
- **URL**: http://localhost:8080
- **System**: PostgreSQL
- **Server**: `db`
- **Username**: `aiteebar`
- **Password**: `aiteebar_password`
- **Database**: `aiteebar_db`

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm run test

# Run in watch mode
npm run test:watch
```

## 📊 Database

### Available PostgreSQL Commands

```bash
# Connect to database
psql postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db

# Run migrations
cd backend && alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback migration
alembic downgrade -1
```

## 🔐 Security Features

- JWT token-based authentication
- OAuth2 integration support
- Role-based access control (RBAC)
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## 📈 Monitoring & Logging

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db
```

### Logs
- Docker: `docker-compose logs -f <service>`
- Application logs are available in `/var/log/` inside containers
- Access logs in frontend browser console

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make your changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/feature-name`
4. Submit a pull request

## 📝 Development Workflow

1. **Create Issue** - Describe the feature or bug
2. **Create Branch** - `feature/issue-name` or `bugfix/issue-name`
3. **Develop** - Make changes locally
4. **Test** - Write tests for new features
5. **Commit** - Use clear, descriptive commit messages
6. **Push** - Push to your branch
7. **Create PR** - Submit pull request with description
8. **Review** - Get code review from team
9. **Merge** - Merge to main branch

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database service
docker-compose restart db

# Check connection
psql postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db
```

### Frontend Can't Connect to Backend
- Check if backend is running: `curl http://localhost:8000/docs`
- Check CORS configuration in `.env`
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

## 📦 Dependencies

### Frontend
- Next.js 14+
- React 18+
- TypeScript
- Tailwind CSS
- React Query
- Axios or Fetch API

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Python-jose (JWT)
- Alembic (Migrations)
- Psycopg2 (PostgreSQL driver)

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Team

- **Project Lead**: Your Name
- **Frontend Lead**: Frontend Developer
- **Backend Lead**: Backend Developer
- **DevOps**: DevOps Engineer

## 📞 Support

For issues and questions:
1. Check [DEVELOPMENT.md](docs/DEVELOPMENT.md) for common issues
2. Check existing GitHub issues
3. Create new issue with detailed description
4. Contact team via Slack/Email

## 🎯 Roadmap

### MVP (Current)
- ✅ User authentication and authorization
- ✅ Security scan creation and management
- ✅ Vulnerability detection and reporting
- ✅ Basic threat intelligence

### Phase 2
- [ ] Advanced threat intelligence dashboard
- [ ] Automated scanning with webhooks
- [ ] Custom report generation
- [ ] API integrations (SIEM, etc.)

### Phase 3
- [ ] Machine learning threat detection
- [ ] Predictive analytics
- [ ] Advanced visualization
- [ ] Mobile application

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [JWT Introduction](https://jwt.io/introduction)

---

**Last Updated**: January 2024  
**Status**: Active Development 🚀
