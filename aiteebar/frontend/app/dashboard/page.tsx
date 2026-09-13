import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { RiskScore } from '@/components/RiskScore'
import { Chart } from '@/components/Chart'
import { Table } from '@/components/Table'

interface SecurityEvent {
  id: string
  name: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  application: string
}

const recentEvents: SecurityEvent[] = [
  {
    id: '1',
    name: 'Suspicious Login Attempt',
    severity: 'high',
    timestamp: '2024-01-15T10:30:00Z',
    application: 'ChatGPT Integration',
  },
  {
    id: '2',
    name: 'API Rate Limit Exceeded',
    severity: 'medium',
    timestamp: '2024-01-15T09:15:00Z',
    application: 'Claude API',
  },
  {
    id: '3',
    name: 'Certificate Expiration Warning',
    severity: 'medium',
    timestamp: '2024-01-14T15:45:00Z',
    application: 'Internal Service',
  },
  {
    id: '4',
    name: 'Malware Signature Detected',
    severity: 'critical',
    timestamp: '2024-01-14T12:20:00Z',
    application: 'Gemini API',
  },
]

export default function DashboardPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
        <p className="text-slate-400 mt-2">Welcome back! Here's your security overview.</p>
      </div>

      {/* Risk Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="flex flex-col items-center justify-center py-8">
          <RiskScore score={72} label="Overall Risk" size="lg" />
        </Card>
        <Card className="flex flex-col items-center justify-center py-8">
          <RiskScore score={45} label="Application Risk" size="lg" />
        </Card>
        <Card className="flex flex-col items-center justify-center py-8">
          <RiskScore score={88} label="API Risk" size="lg" />
        </Card>
        <Card className="flex flex-col items-center justify-center py-8">
          <RiskScore score={32} label="Agent Risk" size="lg" />
        </Card>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400">24</div>
            <div className="text-sm text-slate-400 mt-2">AI Applications</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400">15</div>
            <div className="text-sm text-slate-400 mt-2">Active Agents</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-400">7</div>
            <div className="text-sm text-slate-400 mt-2">Critical Events</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400">94%</div>
            <div className="text-sm text-slate-400 mt-2">Policy Compliance</div>
          </div>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Chart
          title="Risk Timeline"
          subtitle="Last 30 days"
          height="h-80"
        />
        <Chart
          title="Event Distribution"
          subtitle="By severity level"
          height="h-80"
        />
      </div>

      {/* Recent Events */}
      <Card title="Recent Security Events" subtitle="Last 24 hours">
        <Table<SecurityEvent>
          columns={[
            { key: 'name', label: 'Event' },
            {
              key: 'severity',
              label: 'Severity',
              render: (severity) => <Badge variant={severity}>{severity.toUpperCase()}</Badge>,
            },
            { key: 'application', label: 'Application' },
            {
              key: 'timestamp',
              label: 'Time',
              render: (timestamp) => {
                const date = new Date(timestamp)
                return date.toLocaleTimeString()
              },
            },
          ]}
          data={recentEvents}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
