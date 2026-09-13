'use client'

import React, { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import PageHeader from '@/components/PageHeader'
import { MetricCard } from '@/components/MetricCard'
import { RiskDistributionChart } from '@/components/RiskDistributionChart'
import { ApplicationCategoriesChart } from '@/components/ApplicationCategoriesChart'
import { RecentEventsTable } from '@/components/RecentEventsTable'
import { RecentActivityTimeline } from '@/components/RecentActivityTimeline'
import { TopRiskyAgentsTable } from '@/components/TopRiskyAgentsTable'
import { TopRiskyApplicationsTable } from '@/components/TopRiskyApplicationsTable'
import { Card } from '@/components/Card'

interface Metrics {
  total_applications: number
  total_agents: number
  mcp_connections: number
  high_risk_applications: number
  critical_agents: number
  sensitive_data_events: number
  blocked_actions: number
}

interface RiskData {
  low: number
  medium: number
  high: number
  critical: number
}

interface CategoryData {
  category: string
  count: number
  risk_score: number
}

interface SecurityEvent {
  id: string
  name: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  application: string
  description?: string
}

interface Activity {
  id: string
  agent_name: string
  action: string
  status: string
  timestamp: string
  details?: string
}

interface Agent {
  id: string
  name: string
  risk_score: number
  status: string
  application: string
  last_activity?: string
}

interface Application {
  id: string
  name: string
  risk_level: number
  status: string
  provider: string
  agent_count: number
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [riskData, setRiskData] = useState<RiskData | null>(null)
  const [categories, setCategories] = useState<CategoryData[]>([])
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [topAgents, setTopAgents] = useState<Agent[]>([])
  const [topApplications, setTopApplications] = useState<Application[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const getMockData = () => {
    return {
      metrics: {
        total_applications: 38,
        total_agents: 7,
        mcp_connections: 12,
        high_risk_applications: 8,
        critical_agents: 2,
        sensitive_data_events: 14,
        blocked_actions: 3,
      },
      riskData: {
        low: 5,
        medium: 15,
        high: 12,
        critical: 6,
      },
      categories: [
        { category: 'LLM', count: 12, risk_score: 58 },
        { category: 'Data Processing', count: 8, risk_score: 65 },
        { category: 'Automation', count: 10, risk_score: 52 },
        { category: 'Analytics', count: 8, risk_score: 48 },
      ],
      events: [
        {
          id: '1',
          name: 'Unauthorized API Access',
          severity: 'critical',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          application: 'Claude',
        },
        {
          id: '2',
          name: 'Rate Limit Exceeded',
          severity: 'high',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          application: 'ChatGPT',
        },
        {
          id: '3',
          name: 'Unusual Data Access Pattern',
          severity: 'medium',
          timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          application: 'Gemini',
        },
      ],
      activities: [
        {
          id: '1',
          agent_name: 'Customer Support Agent',
          action: 'EXECUTE',
          status: 'executed',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        },
        {
          id: '2',
          agent_name: 'Developer Agent',
          action: 'READ',
          status: 'executed',
          timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        },
        {
          id: '3',
          agent_name: 'Finance Assistant',
          action: 'WRITE',
          status: 'blocked',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        },
      ],
      agents: [
        {
          id: '1',
          name: 'Finance Assistant',
          risk_score: 78,
          status: 'active',
          application: 'ChatGPT',
          last_activity: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        },
        {
          id: '2',
          name: 'Customer Support Agent',
          risk_score: 62,
          status: 'active',
          application: 'Claude',
          last_activity: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        },
        {
          id: '3',
          name: 'HR Assistant',
          risk_score: 65,
          status: 'active',
          application: 'Claude',
          last_activity: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        },
      ],
      applications: [
        {
          id: '1',
          name: 'Gemini Enterprise',
          risk_level: 78,
          status: 'active',
          provider: 'Google',
          agent_count: 3,
        },
        {
          id: '2',
          name: 'ChatGPT Integration',
          risk_level: 65,
          status: 'active',
          provider: 'OpenAI',
          agent_count: 2,
        },
        {
          id: '3',
          name: 'Claude API',
          risk_level: 42,
          status: 'active',
          provider: 'Anthropic',
          agent_count: 2,
        },
      ],
    }
  }

  const fetchDashboardData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [metricsRes, riskRes, catRes, eventsRes, actRes, agentsRes, appsRes] =
        await Promise.all([
          api.get('/v1/dashboard/metrics'),
          api.get('/v1/dashboard/risk-distribution'),
          api.get('/v1/dashboard/application-categories'),
          api.get('/v1/dashboard/recent-events'),
          api.get('/v1/dashboard/recent-activity'),
          api.get('/v1/dashboard/top-risky-agents'),
          api.get('/v1/dashboard/top-risky-applications'),
        ])

      const mock = getMockData()

      setMetrics(metricsRes.data)
      setRiskData(riskRes.data)
      setCategories(catRes.data)
      // Use mock data if API returns empty arrays
      setEvents(eventsRes.data && eventsRes.data.length > 0 ? eventsRes.data : mock.events)
      setActivities(actRes.data && actRes.data.length > 0 ? actRes.data : mock.activities)
      setTopAgents(agentsRes.data && agentsRes.data.length > 0 ? agentsRes.data : mock.agents)
      setTopApplications(appsRes.data && appsRes.data.length > 0 ? appsRes.data : mock.applications)
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err)
      // Use mock data as fallback for demo purposes
      const mock = getMockData()
      setMetrics(mock.metrics)
      setRiskData(mock.riskData)
      setCategories(mock.categories)
      setEvents(mock.events)
      setActivities(mock.activities)
      setTopAgents(mock.agents)
      setTopApplications(mock.applications)
      setError('Using demo data. Some features may be limited.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading && !metrics) {
    return (
      <div className="space-y-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
          <p className="text-slate-400 mt-2">Loading your security overview...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-800 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <PageHeader
        title="Dashboard"
        description="Welcome back! Here's your security overview."
        showBackButton={false}
        actions={
          <button
            onClick={fetchDashboardData}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
          >
            {isLoading ? 'Refreshing...' : '🔄 Refresh'}
          </button>
        }
      />

      {/* Error Alert */}
      {error && (
        <div className={`mb-6 p-4 rounded-lg border ${
          error.includes('demo')
            ? 'bg-blue-900/20 border-blue-700 text-blue-400'
            : 'bg-red-900/20 border-red-700 text-red-400'
        }`}>
          {error.includes('demo') ? '💡 ' : '⚠️ '}{error}
        </div>
      )}

      {/* Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            label="AI Applications"
            value={metrics.total_applications}
            icon="🔧"
            color="blue"
          />
          <MetricCard
            label="Active Agents"
            value={metrics.total_agents}
            icon="🤖"
            color="purple"
          />
          <MetricCard
            label="High Risk Apps"
            value={metrics.high_risk_applications}
            icon="⚠️"
            color="orange"
          />
          <MetricCard
            label="Critical Agents"
            value={metrics.critical_agents}
            icon="🚨"
            color="red"
          />
        </div>
      )}

      {/* Secondary Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            label="MCP Connections"
            value={metrics.mcp_connections}
            icon="⚙️"
            color="blue"
          />
          <MetricCard
            label="Sensitive Data Events"
            value={metrics.sensitive_data_events}
            icon="🔐"
            color="orange"
          />
          <MetricCard
            label="Blocked Actions"
            value={metrics.blocked_actions}
            icon="🛑"
            color="red"
          />
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {riskData && (
          <RiskDistributionChart data={riskData} isLoading={isLoading} />
        )}
        {categories.length > 0 && (
          <ApplicationCategoriesChart data={categories} isLoading={isLoading} />
        )}
      </div>

      {/* Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <RecentEventsTable events={events} isLoading={isLoading} />
        <RecentActivityTimeline activities={activities} isLoading={isLoading} />
      </div>

      {/* Top Risky Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopRiskyAgentsTable agents={topAgents} isLoading={isLoading} />
        <TopRiskyApplicationsTable applications={topApplications} isLoading={isLoading} />
      </div>
    </div>
  )
}
