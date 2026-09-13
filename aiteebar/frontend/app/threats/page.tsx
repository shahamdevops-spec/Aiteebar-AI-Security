'use client'

import React, { useState, useEffect } from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'
import { MetricCard } from '@/components/MetricCard'

interface Threat {
  id: string
  agent_id: string
  threat_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
  confidence: number
  description: string
  affected_resources: string[]
  evidence: Record<string, any>
  recommended_action: string
  timestamp: string
  resolved: boolean
}

interface ThreatSummary {
  total_threats: number
  severity_breakdown: Record<string, number>
  threat_types: Record<string, number>
  most_common_threat: string
  trend: string
  high_severity_count: number
}

export default function ThreatsPage() {
  const [threats, setThreats] = useState<Threat[]>([])
  const [summary, setSummary] = useState<ThreatSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedSeverity, setSelectedSeverity] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch threats
        const threatRes = await fetch('http://localhost:8000/api/threats/events?limit=100&days=7')
        if (threatRes.ok) {
          const threatData = await threatRes.json()
          setThreats(threatData)
        }

        // Fetch summary
        const summaryRes = await fetch('http://localhost:8000/api/threats/summary?days=7')
        if (summaryRes.ok) {
          const summaryData = await summaryRes.json()
          setSummary(summaryData)
        }
      } catch (error) {
        console.error('Failed to fetch threat data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const getSeverityColor = (severity: string): any => {
    switch (severity) {
      case 'critical':
        return 'critical'
      case 'high':
        return 'high'
      case 'medium':
        return 'medium'
      case 'low':
        return 'low'
      default:
        return 'default'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return '📈'
      case 'decreasing':
        return '📉'
      default:
        return '➡️'
    }
  }

  const filteredThreats = selectedSeverity
    ? threats.filter((t) => t.severity === selectedSeverity)
    : threats

  return (
    <div>
      <PageHeader
        title="Threat Detection"
        description="Monitor AI agent threat behaviors and security risks"
        backHref="/dashboard"
      />

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            label="Total Threats"
            value={summary.total_threats}
            icon="⚠️"
            color="blue"
          />
          <MetricCard
            label="Critical"
            value={summary.severity_breakdown.CRITICAL || 0}
            icon="🔴"
            color="red"
            trend={{
              direction: summary.trend === 'increasing' ? 'up' : 'down',
              percentage: 5,
            }}
          />
          <MetricCard
            label="High"
            value={summary.severity_breakdown.HIGH || 0}
            icon="🟠"
            color="orange"
          />
          <MetricCard
            label="Medium & Low"
            value={(summary.severity_breakdown.MEDIUM || 0) + (summary.severity_breakdown.LOW || 0)}
            icon="🟡"
            color="purple"
          />
        </div>
      )}

      {/* Statistics Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-300">Threat Breakdown</h3>
              <div className="space-y-2">
                {Object.entries(summary.threat_types)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="text-sm text-slate-300">{type.replace('Rule', '')}</span>
                      <Badge variant="default" className="text-xs">
                        {count}
                      </Badge>
                    </div>
                  ))}
              </div>
            </div>
          </Card>

          <Card>
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-300">Threat Trend</h3>
              <div className="text-4xl font-bold text-cyan-300 mb-2">
                {getTrendIcon(summary.trend)}
              </div>
              <p className="text-sm text-slate-400">
                Threats are{' '}
                <span className={summary.trend === 'increasing' ? 'text-red-400 font-semibold' : 'text-green-400 font-semibold'}>
                  {summary.trend}
                </span>
              </p>
            </div>
          </Card>

          <Card>
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-300">High Severity</h3>
              <div className="text-4xl font-bold text-red-400">
                {summary.high_severity_count}
              </div>
              <p className="text-sm text-slate-400">
                CRITICAL + HIGH threats in last 7 days
              </p>
            </div>
          </Card>
        </div>
      )}

      {/* Threat Severity Filters */}
      <Card title="🎯 Active Threats" className="mb-8">
        <div className="mb-6 flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedSeverity(null)}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              selectedSeverity === null
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            All ({threats.length})
          </button>
          {['critical', 'high', 'medium', 'low'].map((severity) => {
            const count = threats.filter((t) => t.severity === severity).length
            return (
              <button
                key={severity}
                onClick={() => setSelectedSeverity(severity)}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  selectedSeverity === severity
                    ? 'bg-cyan-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {severity.charAt(0).toUpperCase() + severity.slice(1)} ({count})
              </button>
            )
          })}
        </div>

        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading threats...</div>
        ) : filteredThreats.length > 0 ? (
          <Table<Threat>
            columns={[
              {
                key: 'threat_type',
                label: 'Threat Type',
                render: (value) => (
                  <span className="font-mono text-sm text-cyan-300">
                    {value.replace('Rule', '')}
                  </span>
                ),
              },
              {
                key: 'severity',
                label: 'Severity',
                render: (severity) => (
                  <Badge variant={getSeverityColor(severity)}>
                    {(severity as string).toUpperCase()}
                  </Badge>
                ),
              },
              {
                key: 'risk_score',
                label: 'Risk Score',
                render: (value) => (
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          value >= 80
                            ? 'bg-red-500'
                            : value >= 60
                              ? 'bg-orange-500'
                              : 'bg-yellow-500'
                        }`}
                        style={{ width: `${value}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-300">{value.toFixed(0)}%</span>
                  </div>
                ),
              },
              {
                key: 'description',
                label: 'Description',
                render: (value) => (
                  <p className="text-sm text-slate-300 truncate max-w-xs">{value}</p>
                ),
              },
              {
                key: 'timestamp',
                label: 'Detected',
                render: (value) => (
                  <span className="text-xs text-slate-400">
                    {new Date(value).toLocaleString()}
                  </span>
                ),
              },
            ]}
            data={filteredThreats}
            rowKey="id"
          />
        ) : (
          <div className="text-center py-8">
            <p className="text-4xl mb-3">✅</p>
            <p className="text-slate-400">No threats detected</p>
          </div>
        )}
      </Card>

      {/* Threat Details */}
      {filteredThreats.length > 0 && (
        <div className="space-y-4">
          {filteredThreats.slice(0, 5).map((threat) => (
            <Card key={threat.id} className="border border-slate-700">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-100">
                      {threat.threat_type.replace('Rule', '')}
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">{threat.description}</p>
                  </div>
                  <Badge variant={getSeverityColor(threat.severity)}>
                    {threat.severity.toUpperCase()}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div className="bg-slate-800/50 p-2 rounded">
                    <p className="text-slate-400">Risk Score</p>
                    <p className="text-cyan-300 font-semibold">{threat.risk_score.toFixed(1)}%</p>
                  </div>
                  <div className="bg-slate-800/50 p-2 rounded">
                    <p className="text-slate-400">Confidence</p>
                    <p className="text-cyan-300 font-semibold">{threat.confidence.toFixed(1)}%</p>
                  </div>
                  <div className="bg-slate-800/50 p-2 rounded">
                    <p className="text-slate-400">Agent ID</p>
                    <p className="text-cyan-300 font-mono text-xs">{threat.agent_id.slice(0, 8)}...</p>
                  </div>
                  <div className="bg-slate-800/50 p-2 rounded">
                    <p className="text-slate-400">Status</p>
                    <p className={`font-semibold ${threat.resolved ? 'text-green-400' : 'text-orange-400'}`}>
                      {threat.resolved ? 'Resolved' : 'Active'}
                    </p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-300 mb-2">Recommended Action</p>
                  <p className="text-sm text-slate-300 bg-slate-800/50 p-2 rounded border border-slate-700">
                    {threat.recommended_action}
                  </p>
                </div>

                {threat.affected_resources.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-slate-300 mb-2">Affected Resources</p>
                    <div className="flex flex-wrap gap-2">
                      {threat.affected_resources.map((resource, idx) => (
                        <Badge key={idx} variant="default">
                          {resource}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
