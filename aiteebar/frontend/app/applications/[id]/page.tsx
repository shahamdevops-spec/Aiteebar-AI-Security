'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { api } from '@/lib/api'

interface Application {
  id: string
  name: string
  vendor: string | null
  category: string | null
  description: string | null
  risk_score: number | null
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  privacy_score: number | null
  security_score: number | null
  data_handling_score: number | null
  enterprise_control_score: number | null
  integration_score: number | null
  permission_score: number | null
  mcp_support: boolean
  api_available: boolean
  data_residency: string | null
  is_demo: boolean
  last_assessed: string | null
}

interface Dimension {
  dimension: string
  score: number
  color: string
  label: string
  explanation: string
}

interface RiskAssessment {
  application_name: string
  overall_score: number
  risk_level: string
  risk_color: string
  dimensions: Dimension[]
  key_concerns: string[]
  recommended_controls: string[]
  assessed_at: string
  days_until_reassessment: number | null
  is_demo: boolean
}

const LEVEL_TEXT: Record<string, string> = {
  CRITICAL: 'text-red-300',
  HIGH: 'text-orange-300',
  MEDIUM: 'text-yellow-300',
  LOW: 'text-emerald-300',
}

const LEVEL_RING: Record<string, string> = {
  CRITICAL: 'border-red-500 text-red-300',
  HIGH: 'border-orange-500 text-orange-300',
  MEDIUM: 'border-yellow-500 text-yellow-300',
  LOW: 'border-emerald-500 text-emerald-300',
}

const DIMENSION_LABELS: Record<string, string> = {
  privacy: 'Privacy',
  security: 'Security',
  data_handling: 'Data Handling',
  enterprise_control: 'Enterprise Control',
  integration: 'Integration',
  permission: 'Permissions',
}

export default function ApplicationDetailPage() {
  const params = useParams() as { id: string }
  const router = useRouter()
  const applicationId = params?.id || ''

  const [app, setApp] = useState<Application | null>(null)
  const [risk, setRisk] = useState<RiskAssessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!applicationId) return

    const load = async () => {
      setLoading(true)
      try {
        const appResponse = await api.get<Application>(`/applications/${applicationId}`)
        setApp(appResponse.data)
        setError('')

        // The risk assessment is a separate concern: if it is unavailable the
        // page still renders the application itself rather than failing whole.
        try {
          const riskResponse = await api.get<RiskAssessment>(`/risk/applications/${applicationId}`)
          setRisk(riskResponse.data)
        } catch {
          setRisk(null)
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          setError('That application does not exist.')
        } else {
          setError(err?.response?.data?.detail || 'Could not load this application')
        }
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [applicationId])

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-400">Loading application…</div>
    )
  }

  if (error || !app) {
    return (
      <div className="max-w-xl mx-auto py-20 text-center">
        <p className="text-red-300 font-medium mb-4">{error || 'Application not found'}</p>
        <button
          onClick={() => router.push('/applications')}
          className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white transition-colors"
        >
          Back to applications
        </button>
      </div>
    )
  }

  const score = Math.round(app.risk_score ?? 0)
  const ring = LEVEL_RING[app.risk_level] || LEVEL_RING.MEDIUM

  // Prefer the assessment's dimensions; fall back to the columns on the row.
  const dimensions: Dimension[] = risk?.dimensions?.length
    ? risk.dimensions
    : ([
        ['privacy', app.privacy_score],
        ['security', app.security_score],
        ['data_handling', app.data_handling_score],
        ['enterprise_control', app.enterprise_control_score],
        ['integration', app.integration_score],
        ['permission', app.permission_score],
      ] as const)
        .filter(([, value]) => value !== null)
        .map(([name, value]) => ({
          dimension: name,
          score: Number(value),
          color: '#64748b',
          label: '',
          explanation: '',
        }))

  return (
    <div className="space-y-6">
      <PageHeader
        title={app.name}
        description={[app.vendor, app.category].filter(Boolean).join(' · ') || 'AI application'}
        backHref="/applications"
      />

      {app.is_demo && (
        <div className="px-4 py-3 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-300 text-sm">
          Demonstration data. These scores are illustrative, not a real assessment.
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <div className="flex flex-col items-center py-4">
            <div className={`w-32 h-32 rounded-full border-4 ${ring} flex flex-col items-center justify-center`}>
              <span className="text-4xl font-bold">{score}</span>
              <span className="text-xs text-slate-500">of 100</span>
            </div>
            <p className={`mt-4 text-lg font-semibold ${LEVEL_TEXT[app.risk_level]}`}>
              {app.risk_level} RISK
            </p>
            {app.last_assessed && (
              <p className="text-xs text-slate-500 mt-1">
                Assessed {new Date(app.last_assessed).toLocaleDateString()}
              </p>
            )}
            {risk?.days_until_reassessment != null && (
              <p className="text-xs text-slate-500">
                Reassess in {risk.days_until_reassessment} days
              </p>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-2" title="Overview">
          {app.description && (
            <p className="text-slate-300 mb-5 leading-relaxed">{app.description}</p>
          )}
          <dl className="grid sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">Vendor</dt>
              <dd className="text-slate-200">{app.vendor || '—'}</dd>
            </div>
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">Category</dt>
              <dd className="text-slate-200">{app.category || '—'}</dd>
            </div>
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">Data residency</dt>
              <dd className="text-slate-200">{app.data_residency || '—'}</dd>
            </div>
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">MCP support</dt>
              <dd className={app.mcp_support ? 'text-cyan-300' : 'text-slate-500'}>
                {app.mcp_support ? 'Yes' : 'No'}
              </dd>
            </div>
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">Public API</dt>
              <dd className={app.api_available ? 'text-cyan-300' : 'text-slate-500'}>
                {app.api_available ? 'Yes' : 'No'}
              </dd>
            </div>
            <div className="flex justify-between border-b border-slate-700/40 pb-2">
              <dt className="text-slate-500">ID</dt>
              <dd className="text-slate-400 font-mono text-xs">{app.id.slice(0, 8)}…</dd>
            </div>
          </dl>
        </Card>
      </div>

      {dimensions.length > 0 && (
        <Card title="Risk dimensions" subtitle="Lower is better on every axis">
          <div className="space-y-4">
            {dimensions.map((d) => {
              const value = Math.round(d.score)
              const barColor =
                value >= 75 ? 'bg-red-500' :
                value >= 50 ? 'bg-orange-500' :
                value >= 25 ? 'bg-yellow-500' : 'bg-emerald-500'

              return (
                <div key={d.dimension}>
                  <div className="flex justify-between items-baseline mb-1.5">
                    <span className="text-sm text-slate-200">
                      {DIMENSION_LABELS[d.dimension] || d.dimension}
                    </span>
                    <span className="text-sm font-semibold text-slate-300">
                      {value}
                      {d.label && <span className="text-slate-500 font-normal"> · {d.label}</span>}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-900/70 overflow-hidden">
                    <div className={`h-full ${barColor} transition-all`} style={{ width: `${value}%` }} />
                  </div>
                  {d.explanation && (
                    <p className="text-xs text-slate-500 mt-1.5">{d.explanation}</p>
                  )}
                </div>
              )
            })}
          </div>
        </Card>
      )}

      {risk && (risk.key_concerns?.length > 0 || risk.recommended_controls?.length > 0) && (
        <div className="grid lg:grid-cols-2 gap-6">
          {risk.key_concerns?.length > 0 && (
            <Card title="Key concerns">
              <ul className="space-y-2">
                {risk.key_concerns.map((concern, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-amber-400 shrink-0">▲</span>
                    <span>{concern}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {risk.recommended_controls?.length > 0 && (
            <Card title="Recommended controls">
              <ul className="space-y-2">
                {risk.recommended_controls.map((control, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-emerald-400 shrink-0">✓</span>
                    <span>{control}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}

      {/* No link to /applications/[id]/risk: that route and its six child
          components are still light-themed and render unreadably against the
          dark layout. Everything it shows is already on this page. */}
      <div className="flex gap-3">
        <button
          onClick={() => router.push('/applications')}
          className="px-5 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors"
        >
          ← Back to list
        </button>
      </div>
    </div>
  )
}
