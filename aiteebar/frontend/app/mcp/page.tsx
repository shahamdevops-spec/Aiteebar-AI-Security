'use client'

import React from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'

export default function MCPPage() {
  const tools = [
    { id: 1, name: 'Network Scanner', category: 'Reconnaissance', status: 'available' },
    { id: 2, name: 'Port Analyzer', category: 'Analysis', status: 'available' },
    { id: 3, name: 'Credential Checker', category: 'Validation', status: 'maintenance' },
    { id: 4, name: 'Threat Correlator', category: 'Analysis', status: 'available' },
  ]

  return (
    <div>
      <PageHeader
        title="MCP Tools"
        description="Manage Model Context Protocol tools and integrations."
        backHref="/dashboard"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tools.map((tool) => (
          <Card key={tool.id} title={tool.name} subtitle={tool.category}>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Status</span>
              <Badge variant={tool.status === 'available' ? 'active' : 'pending'}>
                {tool.status}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
