# 🚀 Complete Setup & Run Guide for Aiteebar AI Security

## Overview

This guide will help you set up and run the complete Aiteebar AI Security stack:
- **Frontend**: Next.js 14 (Port 3000)
- **Backend**: FastAPI (Port 8000)
- **Database**: PostgreSQL (Port 5432)
- **Optional**: Redis, Ollama, Adminer

## ⚙️ Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose (optional but recommended)

## 🎯 Option 1: Run Full Stack with Docker Compose (Recommended)

### Step 1: Navigate to Project Root

```bash
cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar"
```

### Step 2: Start All Services

```bash
docker-compose up -d
```

### Step 3: Wait for Services to Start

Services startup times:
- PostgreSQL: ~5 seconds
- Backend (FastAPI): ~10 seconds
- Frontend (Next.js): ~15 seconds

### Step 4: Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Adminer | http://localhost:8080 | Database management (optional) |
| Redis | localhost:6379 | Caching (optional) |

### Step 5: Login with Demo Credentials

```
Admin:     admin@aiteebar.ai      / Demo@123
Analyst:   analyst@aiteebar.ai    / Demo@123
Viewer:    viewer@aiteebar.ai     / Demo@123
```

### Step 6: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Step 7: Stop Services

```bash
docker-compose down
```

---

## 🔧 Option 2: Run Locally Without Docker (Manual Setup)

### Part A: Setup Database

#### 1. Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Install with default settings
- Remember the password you set for `postgres` user

**Linux/Mac:**
```bash
# macOS with Homebrew
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

#### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE aiteebar_db;
CREATE USER aiteebar WITH PASSWORD 'aiteebar_password';
ALTER ROLE aiteebar SET client_encoding TO 'utf8';
ALTER ROLE aiteebar SET default_transaction_isolation TO 'read committed';
ALTER ROLE aiteebar SET default_transaction_deferrable TO on;
ALTER ROLE aiteebar SET default_transaction_read_committed TO on;
ALTER ROLE aiteebar SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE aiteebar_db TO aiteebar;
\q
```

#### 3. Verify Connection

```bash
psql -U aiteebar -d aiteebar_db -h localhost
```

---

### Part B: Setup & Start Backend

#### 1. Navigate to Backend

```bash
cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar\backend"
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Create .env File

Create `backend/.env`:

> **No PostgreSQL? Use SQLite (zero install).** For local development you can skip
> installing PostgreSQL entirely by pointing `DATABASE_URL` at a SQLite file. The app
> creates its tables automatically on first run. Just use this one line as your whole
> `backend/.env`:
>
> ```env
> DATABASE_URL=sqlite:///./aiteebar.db
> ```
>
> Then run `python scripts/init_db.py` and `python scripts/seed_users.py`, and start the
> server. Everything else below (PostgreSQL) is the alternative for a production-like setup.

```env
# Database
DATABASE_URL=postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db
DATABASE_POOL_SIZE=5
DATABASE_ECHO=false

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DEBUG=true

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
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

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed demo users
python scripts/seed_users.py
```

#### 6. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output should show:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### 7. Verify Backend

Open in browser: http://localhost:8000/docs

You should see Swagger API documentation with all endpoints.

---

### Part C: Setup & Start Frontend

#### 1. Open New Terminal & Navigate to Frontend

```bash
cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar\frontend"
```

#### 2. Create .env.local File

```bash
cp .env.local.example .env.local
```

Content should be:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Aiteebar AI Security
NEXT_PUBLIC_APP_VERSION=0.1.0
NEXT_PUBLIC_ENABLE_DEMO_MODE=true
```

#### 3. Install Dependencies

```bash
npm install
```

**Note:** This will install Recharts and all other packages.

#### 4. Start Frontend Server

```bash
npm run dev
```

**Output should show:**
```
> aiteebar-frontend@0.1.0 dev
> next dev

> ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### 5. Open in Browser

http://localhost:3000

---

## 📊 What You'll See

### Home Page (http://localhost:3000)
- Landing page with features overview
- "Get Started" button redirects to login
- Responsive design showcase

### Login Page (http://localhost:3000/login)
- Email and password inputs
- Demo credentials cards (click to auto-fill)
- Error messages if credentials are wrong
- Links to homepage

### Dashboard (http://localhost:3000/dashboard)
After login, you'll see:

**Metric Cards:**
- 📊 Total Applications
- 🤖 Total Agents
- ⚠️ High Risk Applications
- 🚨 Critical Agents
- ⚙️ MCP Connections
- 🔐 Sensitive Data Events
- 🛑 Blocked Actions

**Charts:**
- 📈 Risk Distribution (Pie chart)
- 📊 Applications by Category (Bar chart)

**Tables:**
- 🔴 Recent Security Events
- ⏱️ Recent Agent Activity Timeline
- ⚠️ Top Risky Agents
- 🔴 Top Risky Applications

**Features:**
- 🔄 Refresh button for live updates
- Loading states while fetching
- Mobile-responsive layout
- Dark cybersecurity theme

### Sidebar Navigation
- Dashboard
- Applications
- Agents
- MCP Tools
- Security Events
- DLP Violations
- Policies
- Risk Assessment
- Threat Graph
- Settings

---

## 🧪 Testing the Application

### Test 1: User Authentication

1. Go to http://localhost:3000/login
2. Click "Admin" demo credentials
3. Click "Sign In"
4. Should redirect to http://localhost:3000/dashboard

### Test 2: Dashboard Loads

1. Verify all metric cards display numbers
2. Check charts render without errors
3. Tables should show sample data
4. Refresh button should reload data

### Test 3: Navigation

1. Click sidebar items
2. Verify pages load
3. Check mobile toggle (if screen < 1024px)
4. Click profile dropdown and logout

### Test 4: API Connectivity

1. Open http://localhost:8000/docs
2. Try endpoints:
   - `POST /api/v1/auth/login` - Login
   - `GET /api/v1/auth/me` - Get user
   - `GET /api/v1/dashboard/metrics` - Get metrics
3. Add Authorization header for protected endpoints

---

## 📁 Project Structure (What You've Built)

```
aiteebar/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app (routing, middleware)
│   │   ├── config.py                # Configuration with Pydantic
│   │   ├── database.py              # SQLAlchemy setup
│   │   ├── security.py              # JWT & password handling
│   │   ├── models.py                # SQLAlchemy ORM models (650+ lines)
│   │   ├── exceptions.py            # Custom exception handling
│   │   ├── dependencies.py          # Dependency injection
│   │   ├── routers/
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   └── dashboard.py        # Dashboard API endpoints ✨ NEW
│   │   └── schemas/
│   │       └── user.py             # Pydantic schemas
│   ├── scripts/
│   │   └── seed_users.py           # Demo user creation
│   ├── tests/
│   │   └── test_auth.py            # Authentication tests
│   ├── alembic/                    # Database migrations
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home page
│   │   ├── login/
│   │   │   └── page.tsx            # Login page
│   │   ├── dashboard/
│   │   │   ├── layout.tsx          # Dashboard layout
│   │   │   └── page.tsx            # Dashboard with charts ✨ UPDATED
│   │   ├── applications/           # Pages for all features
│   │   ├── agents/
│   │   ├── events/
│   │   ├── dlp/
│   │   ├── policies/
│   │   ├── risk/
│   │   ├── graph/
│   │   └── settings/
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── RiskScore.tsx
│   │   ├── Table.tsx
│   │   ├── Chart.tsx
│   │   ├── MetricCard.tsx          # ✨ NEW
│   │   ├── RiskDistributionChart.tsx # ✨ NEW
│   │   ├── ApplicationCategoriesChart.tsx # ✨ NEW
│   │   ├── RecentEventsTable.tsx   # ✨ NEW
│   │   ├── RecentActivityTimeline.tsx # ✨ NEW
│   │   ├── TopRiskyAgentsTable.tsx # ✨ NEW
│   │   └── TopRiskyApplicationsTable.tsx # ✨ NEW
│   ├── lib/
│   │   ├── api.ts                  # Axios client
│   │   ├── auth.ts                 # Auth utilities
│   │   ├── constants.ts            # Constants
│   │   └── utils.ts                # Helper functions
│   ├── styles/
│   │   ├── globals.css
│   │   └── colors.ts
│   ├── package.json                # Dependencies + Recharts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.js
│   └── .env.local.example
│
├── database/                        # Database scripts
│   ├── schema.sql
│   ├── seed_data.sql
│   └── init-db.sh
│
├── docker-compose.yml              # Docker orchestration
├── .gitignore
├── .env.example
└── README.md
```

---

## 🐛 Troubleshooting

### Frontend Won't Start

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run dev
```

### Backend Connection Error

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U aiteebar -d aiteebar_db -c "SELECT 1"

# Check connection string in .env
DATABASE_URL=postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db
```

### Port Already in Use

```bash
# Port 3000 (Frontend)
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Port 8000 (Backend)
lsof -ti:8000 | xargs kill -9
```

---

## 📊 What's Working

✅ **Authentication System**
- User registration & login
- JWT token generation
- Password hashing with bcrypt
- Role-based access control

✅ **Dashboard**
- 7 metric cards
- 2 interactive Recharts charts
- 4 data tables with real data
- Activity timeline

✅ **Navigation**
- Responsive sidebar
- Mobile hamburger menu
- Active page highlighting
- User profile dropdown

✅ **Database**
- PostgreSQL schema with 11 tables
- Alembic migrations
- Demo data seeding
- Indexes for performance

✅ **API**
- FastAPI with async endpoints
- JWT authentication middleware
- Error handling
- CORS configuration

✅ **Frontend UI**
- Dark cybersecurity theme
- Tailwind CSS styling
- Responsive design
- Loading states

---

## 📋 What's Next After This Demo

1. **User Management Endpoints** - List, update, delete users
2. **Applications CRUD** - Create/update/delete AI applications
3. **Agents CRUD** - Manage AI agents
4. **Real-time Updates** - WebSocket for live data
5. **Additional Pages** - Implement remaining pages with data
6. **Export Features** - CSV/PDF exports
7. **Advanced Filters** - Date ranges, search, sorting
8. **Notifications** - Alert system

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f` | View logs |
| `npm run dev` | Start frontend dev server |
| `uvicorn app.main:app --reload` | Start backend |
| `alembic upgrade head` | Run migrations |
| `python scripts/seed_users.py` | Seed demo users |

---

**Ready to see your project live!** 🚀
