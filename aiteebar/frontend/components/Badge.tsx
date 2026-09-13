import React from 'react'

type BadgeVariant = 'low' | 'medium' | 'high' | 'critical' | 'active' | 'inactive' | 'pending' | 'success' | 'error' | 'warning' | 'default'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  low: 'bg-gradient-to-r from-green-900/40 to-emerald-900/40 text-green-300 border border-green-500/40 hover:border-green-400/60',
  medium: 'bg-gradient-to-r from-yellow-900/40 to-amber-900/40 text-yellow-300 border border-yellow-500/40 hover:border-yellow-400/60',
  high: 'bg-gradient-to-r from-orange-900/40 to-orange-800/40 text-orange-300 border border-orange-500/40 hover:border-orange-400/60',
  critical: 'bg-gradient-to-r from-red-900/40 to-rose-900/40 text-red-300 border border-red-500/40 hover:border-red-400/60',
  active: 'bg-gradient-to-r from-blue-900/40 to-cyan-900/40 text-cyan-300 border border-cyan-500/40 hover:border-cyan-400/60',
  inactive: 'bg-gradient-to-r from-gray-900/40 to-slate-900/40 text-gray-300 border border-gray-500/40 hover:border-gray-400/60',
  pending: 'bg-gradient-to-r from-yellow-900/40 to-amber-900/40 text-yellow-300 border border-yellow-500/40 hover:border-yellow-400/60',
  success: 'bg-gradient-to-r from-green-900/40 to-emerald-900/40 text-green-300 border border-green-500/40 hover:border-green-400/60',
  error: 'bg-gradient-to-r from-red-900/40 to-rose-900/40 text-red-300 border border-red-500/40 hover:border-red-400/60',
  warning: 'bg-gradient-to-r from-orange-900/40 to-orange-800/40 text-orange-300 border border-orange-500/40 hover:border-orange-400/60',
  default: 'bg-gradient-to-r from-slate-700/60 to-slate-800/60 text-slate-300 border border-slate-600/50 hover:border-slate-500/70',
}

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-semibold ${variantStyles[variant]} transition-all duration-200 ${className}`}
    >
      {children}
    </span>
  )
}
