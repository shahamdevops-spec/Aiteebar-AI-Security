// These must stay in step with DEMO_USERS in backend/scripts/seed_users.py.
// A mismatch here is invisible until someone clicks a demo button and gets a
// 401, which is exactly how this broke before.
export const DEMO_CREDENTIALS = {
  ADMIN: {
    email: 'admin@aiteebar.ai',
    password: 'Demo@123',
    role: 'admin',
  },
  ANALYST: {
    email: 'analyst@aiteebar.ai',
    password: 'Demo@123',
    role: 'analyst',
  },
  VIEWER: {
    email: 'viewer@aiteebar.ai',
    password: 'Demo@123',
    role: 'viewer',
  },
}

export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
}

export const RISK_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef6e3c',
  critical: '#dc2626',
}

export const STATUS_LABELS = {
  active: 'Active',
  inactive: 'Inactive',
  pending: 'Pending',
  success: 'Success',
  error: 'Error',
  warning: 'Warning',
}

export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: '/v1/auth/register',
    LOGIN: '/v1/auth/login',
    ME: '/v1/auth/me',
  },
  APPLICATIONS: {
    LIST: '/v1/applications',
    DETAIL: (id: string) => `/v1/applications/${id}`,
    CREATE: '/v1/applications',
    UPDATE: (id: string) => `/v1/applications/${id}`,
    DELETE: (id: string) => `/v1/applications/${id}`,
  },
  AGENTS: {
    LIST: '/v1/agents',
    DETAIL: (id: string) => `/v1/agents/${id}`,
  },
  EVENTS: {
    LIST: '/v1/events',
    DETAIL: (id: string) => `/v1/events/${id}`,
  },
}
