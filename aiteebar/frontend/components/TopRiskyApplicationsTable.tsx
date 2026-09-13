import React from 'react'
import { Card } from './Card'
import { Badge } from './Badge'
import { RiskScore } from './RiskScore'
import { Table } from './Table'

interface RiskyApplication {
  id: string
  name: string
  risk_level: number
  status: string
  provider: string
  agent_count: number
}

interface TopRiskyApplicationsTableProps {
  applications: RiskyApplication[]
  isLoading?: boolean
}

export function TopRiskyApplicationsTable({
  applications,
  isLoading = false,
}: TopRiskyApplicationsTableProps) {
  if (isLoading) {
    return (
      <Card title="Top Risky Applications" subtitle="Applications with highest risk levels">
        <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading applications...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card title="Top Risky Applications" subtitle="Applications with highest risk levels">
      <Table<RiskyApplication>
        columns={[
          { key: 'name', label: 'Application' },
          {
            key: 'risk_level',
            label: 'Risk Level',
            render: (level) => <RiskScore score={level} size="sm" showLabel={false} />,
          },
          {
            key: 'status',
            label: 'Status',
            render: (status) => (
              <Badge variant={status === 'active' ? 'active' : 'pending'}>
                {status}
              </Badge>
            ),
          },
          { key: 'provider', label: 'Provider' },
          {
            key: 'agent_count',
            label: 'Agents',
            render: (count) => (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-slate-700">
                {count}
              </span>
            ),
          },
        ]}
        data={applications}
        rowKey="id"
      />
    </Card>
  )
}
