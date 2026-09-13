import React from 'react'
import { Card } from './Card'
import { Badge } from './Badge'
import { RiskScore } from './RiskScore'
import { Table } from './Table'

interface RiskyAgent {
  id: string
  name: string
  risk_score: number
  status: string
  application: string
  last_activity?: string
}

interface TopRiskyAgentsTableProps {
  agents: RiskyAgent[]
  isLoading?: boolean
}

export function TopRiskyAgentsTable({ agents, isLoading = false }: TopRiskyAgentsTableProps) {
  if (isLoading) {
    return (
      <Card title="Top Risky Agents" subtitle="Agents with highest risk scores">
        <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading agents...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card title="Top Risky Agents" subtitle="Agents with highest risk scores">
      <Table<RiskyAgent>
        columns={[
          { key: 'name', label: 'Agent Name' },
          {
            key: 'risk_score',
            label: 'Risk Score',
            render: (score) => {
              let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low'
              if (score >= 75) riskLevel = 'critical'
              else if (score >= 50) riskLevel = 'high'
              else if (score >= 25) riskLevel = 'medium'
              return <RiskScore score={score} size="sm" showLabel={false} />
            },
          },
          {
            key: 'status',
            label: 'Status',
            render: (status) => (
              <Badge
                variant={
                  status === 'active'
                    ? 'active'
                    : status === 'critical'
                      ? 'critical'
                      : 'inactive'
                }
              >
                {status}
              </Badge>
            ),
          },
          { key: 'application', label: 'Application' },
          {
            key: 'last_activity',
            label: 'Last Activity',
            render: (timestamp) =>
              timestamp ? new Date(timestamp).toLocaleTimeString() : 'Never',
          },
        ]}
        data={agents}
        rowKey="id"
      />
    </Card>
  )
}
