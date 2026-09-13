'use client'

import React from 'react'
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from './Card'

interface RiskDistributionChartProps {
  data: {
    low: number
    medium: number
    high: number
    critical: number
  }
  isLoading?: boolean
}

const COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef6e3c',
  critical: '#dc2626',
}

export function RiskDistributionChart({ data, isLoading = false }: RiskDistributionChartProps) {
  const chartData = [
    { name: 'Low', value: data.low, fill: COLORS.low },
    { name: 'Medium', value: data.medium, fill: COLORS.medium },
    { name: 'High', value: data.high, fill: COLORS.high },
    { name: 'Critical', value: data.critical, fill: COLORS.critical },
  ]

  const total = data.low + data.medium + data.high + data.critical

  if (isLoading) {
    return (
      <Card title="Risk Distribution" subtitle="Application risk levels">
        <div className="h-80 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading chart...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card title="Risk Distribution" subtitle="Application risk levels">
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value, percent }) =>
                `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
              }
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry) => (
                <Cell key={`cell-${entry.name}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '0.5rem',
              }}
              formatter={(value: number) => [`${value} apps`, 'Count']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 grid grid-cols-4 gap-2 text-sm">
        <div className="text-center">
          <div className="text-green-400 font-semibold">{data.low}</div>
          <div className="text-slate-400">Low</div>
        </div>
        <div className="text-center">
          <div className="text-yellow-400 font-semibold">{data.medium}</div>
          <div className="text-slate-400">Medium</div>
        </div>
        <div className="text-center">
          <div className="text-orange-400 font-semibold">{data.high}</div>
          <div className="text-slate-400">High</div>
        </div>
        <div className="text-center">
          <div className="text-red-400 font-semibold">{data.critical}</div>
          <div className="text-slate-400">Critical</div>
        </div>
      </div>
    </Card>
  )
}
