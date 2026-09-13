'use client'

import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card } from './Card'

interface CategoryData {
  category: string
  count: number
  risk_score: number
}

interface ApplicationCategoriesChartProps {
  data: CategoryData[]
  isLoading?: boolean
}

export function ApplicationCategoriesChart({ data, isLoading = false }: ApplicationCategoriesChartProps) {
  if (isLoading) {
    return (
      <Card title="Applications by Category" subtitle="Count and risk per category">
        <div className="h-80 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading chart...</div>
        </div>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card title="Applications by Category" subtitle="Count and risk per category">
        <div className="h-80 flex items-center justify-center bg-slate-900/50 rounded">
          <div className="text-slate-500">No data available</div>
        </div>
      </Card>
    )
  }

  return (
    <Card title="Applications by Category" subtitle="Count and risk per category">
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="category" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '0.5rem',
              }}
            />
            <Legend />
            <Bar dataKey="count" fill="#3b82f6" name="Application Count" />
            <Bar dataKey="risk_score" fill="#ef6e3c" name="Avg Risk Score" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
