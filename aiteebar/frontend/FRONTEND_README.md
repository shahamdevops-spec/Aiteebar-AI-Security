# Aiteebar AI Security - Next.js Frontend

Modern, production-ready Next.js 14+ frontend for AI security analysis platform with TypeScript, Tailwind CSS, and responsive design.

## 🎯 Overview

- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS with dark cybersecurity theme
- **Language**: TypeScript (strict mode)
- **State Management**: Zustand + React Query
- **HTTP Client**: Axios with JWT interceptors
- **Authentication**: JWT token-based with role-based access control

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with metadata
│   ├── page.tsx                 # Landing page (redirects to dashboard if authenticated)
│   ├── login/
│   │   └── page.tsx            # Login page with demo credentials
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout (auth-protected)
│   │   └── page.tsx            # Dashboard with risk overview
│   ├── applications/            # AI applications management
│   ├── agents/                  # AI agents monitoring
│   ├── mcp/                     # MCP tools management
│   ├── events/                  # Security events viewer
│   ├── dlp/                     # Data loss prevention
│   ├── policies/                # Security policies
│   ├── risk/                    # Risk assessment dashboard
│   ├── graph/                   # Threat network visualization
│   └── settings/                # User settings
├── components/                   # Reusable React components
│   ├── Navbar.tsx              # Top navigation bar
│   ├── Sidebar.tsx             # Side navigation (mobile responsive)
│   ├── Card.tsx                # Card wrapper component
│   ├── Badge.tsx               # Risk/status badges
│   ├── RiskScore.tsx           # Circular risk display
│   ├── Table.tsx               # Generic data table
│   └── Chart.tsx               # Chart placeholder
├── lib/                         # Utilities and helpers
│   ├── api.ts                  # Axios client with interceptors
│   ├── auth.ts                 # Auth utilities & token management
│   ├── constants.ts            # Constants and demo data
│   └── utils.ts                # Helper functions
├── styles/                      # Global styles
│   ├── globals.css             # Global CSS & animations
│   └── colors.ts               # Design tokens
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── next.config.js              # Next.js configuration
├── postcss.config.js           # PostCSS configuration
├── package.json                # Dependencies
└── .env.local.example          # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running at `http://localhost:8000`

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Start development server
npm run dev
```

### Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🔐 Authentication

### Demo Credentials

```
Admin:     admin@aiteebar.ai      / Admin@123
Analyst:   analyst@aiteebar.ai    / Analyst@123
Viewer:    viewer@aiteebar.ai     / Viewer@123
```

Login page displays demo credentials for quick testing. Each role has different permissions:
- **Admin**: Full access to all features
- **Analyst**: Create scans, view reports, manage policies
- **Viewer**: Read-only access

### JWT Token Management

Tokens are automatically:
- Stored in localStorage on login
- Attached to all API requests
- Validated on protected routes
- Cleared on logout or 401 errors

## 🎨 Design System

### Colors

**Risk Levels:**
- Low: `#10b981` (green)
- Medium: `#f59e0b` (amber)
- High: `#ef6e3c` (orange)
- Critical: `#dc2626` (red)

**Backgrounds:**
- Primary: `#0f172a` (slate-900)
- Secondary: `#1e293b` (slate-800)
- Tertiary: `#334155` (slate-700)

### Typography

- Display: 56px / 700 weight
- H1: 36px / 700 weight
- H2: 30px / 700 weight
- H3: 24px / 600 weight
- Body: 16px / 400 weight

### Components

**Card**
```tsx
<Card title="Section Title" subtitle="Description">
  <p>Content here</p>
</Card>
```

**Badge**
```tsx
<Badge variant="critical">Critical</Badge>
<Badge variant="high">High</Badge>
<Badge variant="medium">Medium</Badge>
```

**RiskScore**
```tsx
<RiskScore score={72} label="Overall Risk" size="lg" />
```

**Table**
```tsx
<Table columns={[...]} data={data} rowKey="id" />
```

## 📚 API Integration

### Making API Calls

```typescript
import { api } from '@/lib/api'

// Login
const response = await api.login(email, password)

// Get current user
const user = await api.getCurrentUser()

// Generic requests
const data = await api.get('/v1/applications')
const created = await api.post('/v1/applications', payload)
```

### API Endpoints

All endpoints are prefixed with `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api`)

- `POST /v1/auth/register` - Register user
- `POST /v1/auth/login` - Login
- `GET /v1/auth/me` - Get current user
- `GET /v1/applications` - List applications
- `GET /v1/agents` - List agents
- `GET /v1/events` - List events

## 🛠️ Development

### Build

```bash
npm run build
```

### Lint

```bash
npm run lint
```

### Type Check

```bash
npm run type-check
```

### Format

```bash
npm run format
```

## 📱 Responsive Design

- **Mobile** (<768px): Full-screen sidebar with hamburger toggle
- **Tablet** (768-1024px): Responsive grids and adjusted spacing
- **Desktop** (>1024px): Full sidebar with main content area

## 🔒 Security

- JWT tokens stored in localStorage
- Automatic token attachment to API requests
- Protected routes with auth guards
- CORS configured for backend
- Security headers in next.config.js
- No sensitive data in URLs

## 🚢 Deployment

### Production Build

```bash
npm run build
npm run start
```

### Docker

```bash
docker build -t aiteebar-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.example.com aiteebar-frontend
```

### Vercel

1. Push to GitHub
2. Import project in Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

## 📊 Dashboard Features

### Risk Overview
- Circular risk scores for different categories
- Risk level visualization with colors
- Historical trends

### Applications Management
- Grid view of AI applications
- Risk scores per application
- API call metrics
- Status indicators

### Security Events
- Real-time event monitoring
- Severity-based filtering
- Event details and timeline

### DLP Management
- Violation tracking
- Action history
- Compliance metrics

### Policy Management
- Policy configuration
- Application coverage
- Violation tracking

### Risk Assessment
- Multi-dimensional risk scoring
- Trend analysis
- Category breakdown

## 🔗 Integration Points

### Frontend ↔ Backend
- Login/Authentication: `/v1/auth/*`
- Applications: `/v1/applications`
- Agents: `/v1/agents`
- Events: `/v1/events`
- Policies: `/v1/policies`

## 📝 Environment Variables

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Application
NEXT_PUBLIC_APP_NAME=Aiteebar AI Security
NEXT_PUBLIC_APP_VERSION=0.1.0

# Features
NEXT_PUBLIC_ENABLE_DEMO_MODE=true
NEXT_PUBLIC_ENABLE_CHARTS=true
```

## 🐛 Common Issues

### Module Not Found
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
# Or use different port
npm run dev -- -p 3001
```

### API Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS settings on backend

## 📖 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)
- [Axios](https://axios-http.com)
- [React 18](https://react.dev)

## 📄 License

© 2024 Aiteebar AI Security. All rights reserved.

---

**Status**: ✅ Production-Ready  
**Last Updated**: 2024-01-15  
**Version**: 0.1.0
