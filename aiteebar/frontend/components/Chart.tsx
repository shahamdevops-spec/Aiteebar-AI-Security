import React from 'react'

interface ChartProps {
  title?: string
  subtitle?: string
  height?: string
  children?: React.ReactNode
}

export function Chart({ title, subtitle, height = 'h-64', children }: ChartProps) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      {(title || subtitle) && (
        <div className="mb-6">
          {title && <h3 className="text-lg font-semibold text-slate-100">{title}</h3>}
          {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className={`${height} flex items-center justify-center bg-slate-900/50 rounded border border-slate-700 border-dashed`}>
        {children || (
          <div className="text-center">
            <div className="text-slate-500 text-sm">
              📊 Chart placeholder
            </div>
            <div className="text-slate-600 text-xs mt-1">
              Integrate your charting library here
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
