'use client'

import React from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { RiskScore } from '@/components/RiskScore'
import { Chart } from '@/components/Chart'

export default function RiskPage() {
  const riskMetrics = [
    { label: 'Overall Risk', score: 72, trend: 'up' },
    { label: 'Application Risk', score: 45, trend: 'down' },
    { label: 'API Risk', score: 88, trend: 'up' },
    { label: 'Agent Risk', score: 32, trend: 'stable' },
    { label: 'Data Risk', score: 55, trend: 'up' },
    { label: 'Compliance Risk', score: 28, trend: 'down' },
  ]

  return (
    <div>
      <PageHeader
        title="Risk Assessment"
        description="Comprehensive risk analysis and scoring."
        backHref="/dashboard"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {riskMetrics.map((metric) => (
          <Card key={metric.label}>
            <div className="flex flex-col items-center">
              <RiskScore score={metric.score} label={metric.label} size="md" />
              <div className="mt-4 text-sm text-slate-400">
                {metric.trend === 'up' && '📈 Increasing'}
                {metric.trend === 'down' && '📉 Decreasing'}
                {metric.trend === 'stable' && '➡️ Stable'}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart
          title="Risk Trend (30 Days)"
          subtitle="Historical risk progression"
          height="h-80"
        />
        <Chart
          title="Risk Breakdown"
          subtitle="By category"
          height="h-80"
        />
      </div>
    </div>
  )
}
