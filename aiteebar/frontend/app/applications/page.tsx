'use client'

import React from 'react'
import PageHeader from '@/components/PageHeader'
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
      <PageHeader
        title="AI Applications"
        description="Monitor and manage your AI application integrations."
        backHref="/dashboard"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {applications.map((app) => {
          const riskColor = app.risk >= 75 ? 'from-red-900/40 to-rose-900/40 border-red-500/30' :
                           app.risk >= 50 ? 'from-orange-900/40 to-amber-900/40 border-orange-500/30' :
                           app.risk >= 25 ? 'from-yellow-900/40 to-yellow-900/40 border-yellow-500/30' :
                           'from-green-900/40 to-emerald-900/40 border-green-500/30';

          return (
            <div
              key={app.id}
              className={`group relative bg-gradient-to-br ${riskColor} rounded-xl border p-6 backdrop-blur-sm hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-300 cursor-pointer hover:scale-105`}
            >
              {/* Gradient Overlay on Hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/5 group-hover:to-cyan-500/5 rounded-xl transition-all"></div>

              <div className="relative">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1 group-hover:text-cyan-300 transition-colors">{app.name}</h3>
                    <p className="text-sm text-slate-400">{app.provider}</p>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center">
                    <span className="text-xl">🔧</span>
                  </div>
                </div>

                {/* Divider */}
                <div className="border-t border-slate-700/50 my-4"></div>

                {/* Content Grid */}
                <div className="space-y-4">
                  {/* Risk Level */}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-wider">Risk Level</p>
                      <p className="text-sm text-slate-200 mt-1">
                        {app.risk >= 75 ? 'Critical' : app.risk >= 50 ? 'High' : app.risk >= 25 ? 'Medium' : 'Low'}
                      </p>
                    </div>
                    <div className="w-16 h-16 flex items-center justify-center">
                      <RiskScore score={app.risk} size="sm" showLabel={false} />
                    </div>
                  </div>

                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-slate-400 uppercase tracking-wider">Status</p>
                    <Badge variant={app.status === 'active' ? 'active' : 'pending'}>
                      {app.status === 'active' ? '🟢 Active' : '🟡 Pending'}
                    </Badge>
                  </div>

                  {/* API Calls */}
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-slate-400 uppercase tracking-wider">API Calls (24h)</p>
                    <p className="text-lg font-semibold text-cyan-300">{(app.apiCalls / 1000).toFixed(0)}k</p>
                  </div>
                </div>

                {/* Footer Action */}
                <div className="mt-6 pt-4 border-t border-slate-700/50">
                  <button className="w-full py-2 px-4 bg-gradient-to-r from-blue-600/50 to-cyan-600/50 hover:from-blue-600 hover:to-cyan-600 rounded-lg text-sm font-semibold text-white transition-all group-hover:shadow-lg group-hover:shadow-cyan-500/20">
                    View Details →
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}
