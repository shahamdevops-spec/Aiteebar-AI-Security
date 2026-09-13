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
  blue: 'text-blue-300 bg-gradient-to-br from-blue-900/40 to-blue-800/40 border border-blue-500/20',
  green: 'text-green-300 bg-gradient-to-br from-green-900/40 to-green-800/40 border border-green-500/20',
  orange: 'text-orange-300 bg-gradient-to-br from-orange-900/40 to-orange-800/40 border border-orange-500/20',
  red: 'text-red-300 bg-gradient-to-br from-red-900/40 to-red-800/40 border border-red-500/20',
  purple: 'text-purple-300 bg-gradient-to-br from-purple-900/40 to-purple-800/40 border border-purple-500/20',
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
    <Card className="group">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-3">{label}</p>
          <div className="flex items-baseline gap-3">
            <div className="text-4xl font-bold bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">{value}</div>
            {trend && (
              <div className={`text-sm font-semibold px-2 py-1 rounded-lg ${trend.direction === 'up' ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'}`}>
                {trend.direction === 'up' && '📈'}
                {trend.direction === 'down' && '📉'}
                {trend.direction === 'stable' && '➡️'}
                {' '}{trend.percentage}%
              </div>
            )}
          </div>
        </div>
        <div className={`text-4xl p-4 rounded-xl ${colorClass} flex items-center justify-center w-16 h-16`}>
          {icon}
        </div>
      </div>
    </Card>
  )
}
