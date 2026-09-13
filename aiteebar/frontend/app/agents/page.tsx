import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'

interface Agent {
  id: string
  name: string
  status: 'active' | 'inactive'
  tasksCompleted: number
  lastActivity: string
  tools: number
}

export default function AgentsPage() {
  const agents: Agent[] = [
    {
      id: '1',
      name: 'Threat Detection Agent',
      status: 'active',
      tasksCompleted: 1245,
      lastActivity: '2 minutes ago',
      tools: 12,
    },
    {
      id: '2',
      name: 'Vulnerability Scanner',
      status: 'active',
      tasksCompleted: 892,
      lastActivity: '5 minutes ago',
      tools: 8,
    },
    {
      id: '3',
      name: 'Policy Compliance Agent',
      status: 'inactive',
      tasksCompleted: 456,
      lastActivity: '2 hours ago',
      tools: 6,
    },
    {
      id: '4',
      name: 'Incident Response Agent',
      status: 'active',
      tasksCompleted: 234,
      lastActivity: '10 minutes ago',
      tools: 15,
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">AI Agents</h1>
        <p className="text-slate-400 mt-2">Monitor and manage autonomous security agents.</p>
      </div>

      <Card title="Active Agents">
        <Table<Agent>
          columns={[
            { key: 'name', label: 'Agent Name' },
            {
              key: 'status',
              label: 'Status',
              render: (status) => (
                <Badge variant={status}>
                  {status === 'active' ? '● Active' : '● Inactive'}
                </Badge>
              ),
            },
            {
              key: 'tasksCompleted',
              label: 'Tasks',
              render: (count) => <span className="text-slate-300">{count}</span>,
            },
            {
              key: 'tools',
              label: 'Tools',
              render: (count) => <span className="text-slate-300">{count}</span>,
            },
            { key: 'lastActivity', label: 'Last Activity' },
          ]}
          data={agents}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
