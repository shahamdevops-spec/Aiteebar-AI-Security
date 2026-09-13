import React from 'react'
import { Card } from './Card'
import { Badge } from './Badge'

interface Activity {
  id: string
  agent_name: string
  action: string
  status: string
  timestamp: string
  // agent_metadata is a JSON column, so this arrives as an object, not a
  // string. Rendering it directly throws "Objects are not valid as a React
  // child" and blanks the whole dashboard.
  details?: string | Record<string, unknown> | null
  resource?: string | null
}

/** Reduce whatever `details` holds to something renderable. */
function summarise(details: Activity['details']): string {
  if (!details) return ''
  if (typeof details === 'string') return details
  const entries = Object.entries(details)
  if (entries.length === 0) return ''
  return entries.map(([key, value]) => `${key}: ${String(value)}`).join(' · ')
}

interface RecentActivityTimelineProps {
  activities: Activity[]
  isLoading?: boolean
}

const actionIcons: Record<string, string> = {
  scan: '🔍',
  detect: '🚨',
  block: '🛑',
  alert: '⚠️',
  check: '✓',
  update: '🔄',
  create: '➕',
  delete: '🗑️',
  'default': '●',
}

export function RecentActivityTimeline({ activities, isLoading = false }: RecentActivityTimelineProps) {
  if (isLoading) {
    return (
      <Card title="Recent Activity" subtitle="Agent activity and operations">
        <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded animate-pulse">
          <div className="text-slate-500">Loading activity...</div>
        </div>
      </Card>
    )
  }

  if (activities.length === 0) {
    return (
      <Card title="Recent Activity" subtitle="Agent activity and operations">
        <div className="text-center py-8 text-slate-400">No recent activity</div>
      </Card>
    )
  }

  return (
    <Card title="Recent Activity" subtitle="Agent activity and operations">
      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex gap-4 pb-4 border-b border-slate-700 last:border-0">
            <div className="text-2xl flex-shrink-0">
              {actionIcons[activity.action.toLowerCase()] || actionIcons['default']}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-slate-100">{activity.agent_name}</p>
                  <p className="text-sm text-slate-400 capitalize">{activity.action}</p>
                </div>
                <Badge
                  variant={
                    activity.status === 'success'
                      ? 'success'
                      : activity.status === 'failed'
                        ? 'error'
                        : activity.status === 'pending'
                          ? 'pending'
                          : 'default'
                  }
                >
                  {activity.status}
                </Badge>
              </div>
              {activity.resource && (
                <p className="text-xs text-slate-400 mt-1 truncate">{activity.resource}</p>
              )}
              {summarise(activity.details) && (
                <p className="text-xs text-slate-500 mt-1 truncate">{summarise(activity.details)}</p>
              )}
              <p className="text-xs text-slate-500 mt-1">
                {new Date(activity.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
