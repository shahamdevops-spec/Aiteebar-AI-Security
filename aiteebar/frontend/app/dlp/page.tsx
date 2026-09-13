import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'

interface DLPViolation {
  id: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  action: string
}

export default function DLPPage() {
  const violations: DLPViolation[] = [
    {
      id: '1',
      type: 'Credit Card Detected',
      severity: 'critical',
      timestamp: '2024-01-15T10:30:00Z',
      action: 'Blocked',
    },
    {
      id: '2',
      type: 'API Key Exposure',
      severity: 'high',
      timestamp: '2024-01-15T09:15:00Z',
      action: 'Quarantined',
    },
    {
      id: '3',
      type: 'PII Fragment Match',
      severity: 'medium',
      timestamp: '2024-01-14T15:45:00Z',
      action: 'Logged',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">Data Loss Prevention</h1>
        <p className="text-slate-400 mt-2">Monitor data loss prevention violations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-400">12</div>
            <div className="text-sm text-slate-400 mt-2">Total Violations</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-400">3</div>
            <div className="text-sm text-slate-400 mt-2">This Month</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400">92%</div>
            <div className="text-sm text-slate-400 mt-2">Blocked Rate</div>
          </div>
        </Card>
      </div>

      <Card title="Recent Violations">
        <Table<DLPViolation>
          columns={[
            { key: 'type', label: 'Type' },
            {
              key: 'severity',
              label: 'Severity',
              render: (severity) => <Badge variant={severity}>{severity.toUpperCase()}</Badge>,
            },
            { key: 'action', label: 'Action Taken' },
            {
              key: 'timestamp',
              label: 'Time',
              render: (timestamp) => new Date(timestamp).toLocaleString(),
            },
          ]}
          data={violations}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
