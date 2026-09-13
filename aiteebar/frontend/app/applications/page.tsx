import React from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { RiskScore } from '@/components/RiskScore'

export default function ApplicationsPage() {
  const applications = [
    {
      id: 1,
      name: 'ChatGPT Integration',
      provider: 'OpenAI',
      risk: 65,
      status: 'active',
      apiCalls: 125000,
    },
    {
      id: 2,
      name: 'Claude API',
      provider: 'Anthropic',
      risk: 42,
      status: 'active',
      apiCalls: 89000,
    },
    {
      id: 3,
      name: 'Gemini Enterprise',
      provider: 'Google',
      risk: 78,
      status: 'pending',
      apiCalls: 45000,
    },
    {
      id: 4,
      name: 'Internal ML Service',
      provider: 'Custom',
      risk: 38,
      status: 'active',
      apiCalls: 156000,
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">AI Applications</h1>
        <p className="text-slate-400 mt-2">Monitor and manage your AI application integrations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {applications.map((app) => (
          <Card key={app.id} title={app.name} subtitle={`Provider: ${app.provider}`}>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Risk Level</span>
                <RiskScore score={app.risk} size="sm" showLabel={false} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Status</span>
                <Badge variant={app.status === 'active' ? 'active' : 'pending'}>
                  {app.status}
                </Badge>
              </div>
              <div className="pt-2 border-t border-slate-700">
                <div className="text-sm text-slate-400">
                  API Calls (24h): <span className="text-slate-200">{(app.apiCalls / 1000).toFixed(0)}k</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
