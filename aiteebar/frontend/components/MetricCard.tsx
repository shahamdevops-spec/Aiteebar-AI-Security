import React from 'react'
import { Card } from './Card'

interface MetricCardProps {
  label: string
  value: number | string
  icon: string
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple'
  trend?: {
    direction: 'up' | 'down' | 'stable'
    percentage: number
  }
}

const colorStyles = {
  blue: 'text-blue-400 bg-blue-900/20',
  green: 'text-green-400 bg-green-900/20',
  orange: 'text-orange-400 bg-orange-900/20',
  red: 'text-red-400 bg-red-900/20',
  purple: 'text-purple-400 bg-purple-900/20',
}

export function MetricCard({
  label,
  value,
  icon,
  color = 'blue',
  trend,
}: MetricCardProps) {
  const colorClass = colorStyles[color]

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-2">{label}</p>
          <div className="flex items-baseline gap-2">
            <div className="text-3xl font-bold text-slate-100">{value}</div>
            {trend && (
              <div className={`text-sm ${trend.direction === 'up' ? 'text-red-400' : 'text-green-400'}`}>
                {trend.direction === 'up' && '📈'}
                {trend.direction === 'down' && '📉'}
                {trend.direction === 'stable' && '➡️'}
                {' '}{trend.percentage}%
              </div>
            )}
          </div>
        </div>
        <div className={`text-4xl p-3 rounded-lg ${colorClass}`}>
          {icon}
        </div>
      </div>
    </Card>
  )
}
