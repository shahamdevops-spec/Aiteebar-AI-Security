import React from 'react'

type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

interface RiskScoreProps {
  score: number // 0-100
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

function getRiskLevel(score: number): RiskLevel {
  if (score < 25) return 'low'
  if (score < 50) return 'medium'
  if (score < 75) return 'high'
  return 'critical'
}

function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'low':
      return 'text-green-400'
    case 'medium':
      return 'text-yellow-400'
    case 'high':
      return 'text-orange-400'
    case 'critical':
      return 'text-red-400'
  }
}

function getRiskBgColor(level: RiskLevel): string {
  switch (level) {
    case 'low':
      return 'from-green-900/20 to-green-900/10'
    case 'medium':
      return 'from-yellow-900/20 to-yellow-900/10'
    case 'high':
      return 'from-orange-900/20 to-orange-900/10'
    case 'critical':
      return 'from-red-900/20 to-red-900/10'
  }
}

function getRiskLabel(level: RiskLevel): string {
  switch (level) {
    case 'low':
      return 'Low'
    case 'medium':
      return 'Medium'
    case 'high':
      return 'High'
    case 'critical':
      return 'Critical'
  }
}

const sizeStyles = {
  sm: {
    container: 'w-12 h-12',
    text: 'text-sm',
    label: 'text-xs',
  },
  md: {
    container: 'w-20 h-20',
    text: 'text-2xl',
    label: 'text-sm',
  },
  lg: {
    container: 'w-28 h-28',
    text: 'text-4xl',
    label: 'text-base',
  },
}

export function RiskScore({
  score,
  label,
  size = 'md',
  showLabel = true,
}: RiskScoreProps) {
  const riskLevel = getRiskLevel(score)
  const styles = sizeStyles[size]
  const colorClass = getRiskColor(riskLevel)
  const bgColorClass = getRiskBgColor(riskLevel)
  const riskLabelText = getRiskLabel(riskLevel)

  return (
    <div className="flex flex-col items-center">
      <div
        className={`${styles.container} flex items-center justify-center rounded-full bg-gradient-to-br ${bgColorClass} border-2 ${colorClass.replace('text', 'border')}`}
      >
        <div className={`font-bold ${styles.text} ${colorClass}`}>{score}</div>
      </div>
      {showLabel && (
        <div className="mt-2 text-center">
          <div className={`font-semibold ${colorClass} ${styles.label}`}>
            {riskLabelText}
          </div>
          {label && <div className="text-slate-400 text-xs mt-1">{label}</div>}
        </div>
      )}
    </div>
  )
}
