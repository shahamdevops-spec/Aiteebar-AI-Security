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

      setMetrics(metricsRes.data)
      setRiskData(riskRes.data)
      setCategories(catRes.data)
      setEvents(eventsRes.data)
      setActivities(actRes.data)
      setTopAgents(agentsRes.data)
      setTopApplications(appsRes.data)
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err)
      setError('Failed to load dashboard data. Please try again.')
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
        <div className="mb-6 p-4 bg-red-900/20 border border-red-700 text-red-400 rounded-lg">
          {error}
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
