import React from 'react'
import { Card } from './Card'
import { Badge } from './Badge'
import { Table } from './Table'

interface SecurityEvent {
  id: string
  name: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  application: string
  description?: string
}

interface RecentEventsTableProps {
  events: SecurityEvent[]
  isLoading?: boolean
}

export function RecentEventsTable({ events, isLoading = false }: RecentEventsTableProps) {
  if (isLoading) {
    return (
      <Card title="Recent Security Events" subtitle="Latest detected threats and incidents">
        <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading events...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card title="Recent Security Events" subtitle="Latest detected threats and incidents">
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
        data={events}
        rowKey="id"
      />
    </Card>
  )
}
