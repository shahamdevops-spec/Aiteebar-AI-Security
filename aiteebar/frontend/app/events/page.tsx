import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'

interface SecurityEvent {
  id: string
  name: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  source: string
}

export default function EventsPage() {
  const events: SecurityEvent[] = [
    {
      id: '1',
      name: 'Unauthorized API Access',
      severity: 'critical',
      timestamp: '2024-01-15T10:30:00Z',
      source: 'API Gateway',
    },
    {
      id: '2',
      name: 'High Memory Usage',
      severity: 'high',
      timestamp: '2024-01-15T09:45:00Z',
      source: 'Agent Monitor',
    },
    {
      id: '3',
      name: 'Certificate Expires Soon',
      severity: 'medium',
      timestamp: '2024-01-14T15:20:00Z',
      source: 'Certificate Manager',
    },
    {
      id: '4',
      name: 'Service Health Check',
      severity: 'low',
      timestamp: '2024-01-14T12:00:00Z',
      source: 'Health Monitor',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">Security Events</h1>
        <p className="text-slate-400 mt-2">View all security events and alerts.</p>
      </div>

      <Card title="Recent Events">
        <Table<SecurityEvent>
          columns={[
            { key: 'name', label: 'Event' },
            {
              key: 'severity',
              label: 'Severity',
              render: (severity) => <Badge variant={severity}>{severity.toUpperCase()}</Badge>,
            },
            { key: 'source', label: 'Source' },
            {
              key: 'timestamp',
              label: 'Time',
              render: (timestamp) => new Date(timestamp).toLocaleString(),
            },
          ]}
          data={events}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
