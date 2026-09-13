import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'

interface Policy {
  id: string
  name: string
  status: 'active' | 'inactive'
  applications: number
  violations: number
}

export default function PoliciesPage() {
  const policies: Policy[] = [
    {
      id: '1',
      name: 'API Rate Limiting Policy',
      status: 'active',
      applications: 8,
      violations: 3,
    },
    {
      id: '2',
      name: 'Data Encryption Policy',
      status: 'active',
      applications: 12,
      violations: 0,
    },
    {
      id: '3',
      name: 'Access Control Policy',
      status: 'active',
      applications: 15,
      violations: 2,
    },
    {
      id: '4',
      name: 'Audit Logging Policy',
      status: 'inactive',
      applications: 5,
      violations: 0,
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">Security Policies</h1>
        <p className="text-slate-400 mt-2">Define and manage security policies.</p>
      </div>

      <Card title="Active Policies">
        <Table<Policy>
          columns={[
            { key: 'name', label: 'Policy Name' },
            {
              key: 'status',
              label: 'Status',
              render: (status) => <Badge variant={status}>{status}</Badge>,
            },
            {
              key: 'applications',
              label: 'Applications',
              render: (count) => <span className="text-slate-300">{count}</span>,
            },
            {
              key: 'violations',
              label: 'Violations',
              render: (count) => (
                <span className={count > 0 ? 'text-red-400' : 'text-green-400'}>
                  {count}
                </span>
              ),
            },
          ]}
          data={policies}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
