'use client'

import React from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { Chart } from '@/components/Chart'

export default function GraphPage() {
  return (
    <div>
      <PageHeader
        title="Threat Graph"
        description="Visualize relationships between threats, applications, and agents."
        backHref="/dashboard"
      />

      <Card className="mb-6">
        <Chart
          title="Threat Network"
          subtitle="Interconnected threats and vulnerabilities"
          height="h-96"
        />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <div className="space-y-3">
            <h3 className="font-semibold text-slate-100">Network Statistics</h3>
            <div>
              <div className="text-sm text-slate-400">Total Nodes</div>
              <div className="text-2xl font-bold text-blue-400">342</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Connections</div>
              <div className="text-2xl font-bold text-purple-400">1,245</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Critical Paths</div>
              <div className="text-2xl font-bold text-red-400">12</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="space-y-3">
            <h3 className="font-semibold text-slate-100">Most Connected</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">API Gateway</span>
                <span className="text-slate-300">42 connections</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Auth Service</span>
                <span className="text-slate-300">38 connections</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Database</span>
                <span className="text-slate-300">35 connections</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
