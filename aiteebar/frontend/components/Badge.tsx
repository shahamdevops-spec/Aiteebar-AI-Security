import React from 'react'

type BadgeVariant = 'low' | 'medium' | 'high' | 'critical' | 'active' | 'inactive' | 'pending' | 'success' | 'error' | 'warning' | 'default'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  low: 'bg-green-900/30 text-green-400 border border-green-700',
  medium: 'bg-yellow-900/30 text-yellow-400 border border-yellow-700',
  high: 'bg-orange-900/30 text-orange-400 border border-orange-700',
  critical: 'bg-red-900/30 text-red-400 border border-red-700',
  active: 'bg-blue-900/30 text-blue-400 border border-blue-700',
  inactive: 'bg-gray-900/30 text-gray-400 border border-gray-700',
  pending: 'bg-yellow-900/30 text-yellow-400 border border-yellow-700',
  success: 'bg-green-900/30 text-green-400 border border-green-700',
  error: 'bg-red-900/30 text-red-400 border border-red-700',
  warning: 'bg-orange-900/30 text-orange-400 border border-orange-700',
  default: 'bg-slate-700 text-slate-300 border border-slate-600',
}

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  )
}
