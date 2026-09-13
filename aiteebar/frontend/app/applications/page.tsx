'use client'

import React, { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import PageHeader from '@/components/PageHeader'
import { api } from '@/lib/api'

interface Application {
  id: string
  name: string
  vendor: string | null
  category: string | null
  description: string | null
  risk_score: number | null
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  mcp_support: boolean
  api_available: boolean
  data_residency: string | null
  is_demo: boolean
}

interface ApplicationList {
  total: number
  limit: number
  offset: number
  applications: Application[]
}

const PAGE_SIZE = 12

const RISK_STYLES: Record<string, { card: string; ring: string; text: string }> = {
  CRITICAL: {
    card: 'from-red-900/40 to-rose-900/30 border-red-500/30',
    ring: 'border-red-500 text-red-300',
    text: 'text-red-300',
  },
  HIGH: {
    card: 'from-orange-900/40 to-amber-900/30 border-orange-500/30',
    ring: 'border-orange-500 text-orange-300',
    text: 'text-orange-300',
  },
  MEDIUM: {
    card: 'from-yellow-900/30 to-yellow-900/20 border-yellow-500/30',
    ring: 'border-yellow-500 text-yellow-300',
    text: 'text-yellow-300',
  },
  LOW: {
    card: 'from-emerald-900/30 to-green-900/20 border-emerald-500/30',
    ring: 'border-emerald-500 text-emerald-300',
    text: 'text-emerald-300',
  },
}

const styleFor = (level: string) => RISK_STYLES[level] || RISK_STYLES.MEDIUM

const inputClass =
  'px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100 ' +
  'placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 transition-colors'

export default function ApplicationsPage() {
  const router = useRouter()

  const [apps, setApps] = useState<Application[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [search, setSearch] = useState('')
  const [riskLevel, setRiskLevel] = useState('')
  const [sortBy, setSortBy] = useState('risk_score')
  const [page, setPage] = useState(0)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(page * PAGE_SIZE),
        sort_by: sortBy,
        sort_order: sortBy === 'risk_score' ? 'desc' : 'asc',
      })
      if (search.trim()) params.set('search', search.trim())
      if (riskLevel) params.set('risk_level', riskLevel)

      const response = await api.get<ApplicationList>(`/applications?${params}`)
      setApps(response.data.applications)
      setTotal(response.data.total)
      setError('')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Could not load applications')
    } finally {
      setLoading(false)
    }
  }, [page, search, riskLevel, sortBy])

  // Debounced so typing in the search box does not fire a request per keystroke.
  useEffect(() => {
    const timer = setTimeout(load, 250)
    return () => clearTimeout(timer)
  }, [load])

  const openDetails = (id: string) => router.push(`/applications/${id}`)

  const lastPage = Math.max(0, Math.ceil(total / PAGE_SIZE) - 1)

  return (
    <div>
      <PageHeader
        title="AI Applications"
        description="Monitor and manage your AI application integrations"
        backHref="/dashboard"
      />

      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => { setPage(0); setSearch(e.target.value) }}
          placeholder="Search name, vendor, or description…"
          className={`${inputClass} flex-1 min-w-[16rem]`}
        />
        <select
          value={riskLevel}
          onChange={(e) => { setPage(0); setRiskLevel(e.target.value) }}
          className={inputClass}
        >
          <option value="">All risk levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => { setPage(0); setSortBy(e.target.value) }}
          className={inputClass}
        >
          <option value="risk_score">Highest risk first</option>
          <option value="name">Name A-Z</option>
        </select>
      </div>

      {error && (
        <div className="mb-6 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          {error}
        </div>
      )}

      <p className="text-sm text-slate-500 mb-4">
        {loading ? 'Loading…' : `${total} application${total === 1 ? '' : 's'}`}
        {total > PAGE_SIZE && !loading && ` · page ${page + 1} of ${lastPage + 1}`}
      </p>

      {!loading && apps.length === 0 ? (
        <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-12 text-center">
          <p className="text-slate-300 font-medium">No applications match those filters</p>
          <p className="text-slate-500 text-sm mt-1">Try clearing the search or risk level.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {apps.map((app) => {
            const style = styleFor(app.risk_level)
            const score = Math.round(app.risk_score ?? 0)

            return (
              <div
                key={app.id}
                onClick={() => openDetails(app.id)}
                role="link"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter') openDetails(app.id) }}
                className={`group relative bg-gradient-to-br ${style.card} rounded-xl border p-6
                            cursor-pointer transition-all duration-300
                            hover:shadow-lg hover:shadow-cyan-500/10 hover:border-cyan-500/40
                            focus:outline-none focus:border-cyan-500/60`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0 pr-3">
                    <h3 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors truncate">
                      {app.name}
                    </h3>
                    <p className="text-sm text-slate-400">
                      {app.vendor || 'Unknown vendor'}
                      {app.category && <span className="text-slate-600"> · {app.category}</span>}
                    </p>
                  </div>
                  <div className={`shrink-0 w-14 h-14 rounded-full border-2 ${style.ring}
                                   flex items-center justify-center font-bold`}>
                    {score}
                  </div>
                </div>

                {app.description && (
                  <p className="text-sm text-slate-400 line-clamp-2 mb-4">{app.description}</p>
                )}

                <div className="border-t border-slate-700/50 pt-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500 uppercase tracking-wider">Risk level</span>
                    <span className={`text-sm font-semibold ${style.text}`}>{app.risk_level}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500 uppercase tracking-wider">Capabilities</span>
                    <div className="flex gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded border ${
                        app.mcp_support
                          ? 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10'
                          : 'border-slate-700 text-slate-600'}`}>
                        MCP
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded border ${
                        app.api_available
                          ? 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10'
                          : 'border-slate-700 text-slate-600'}`}>
                        API
                      </span>
                    </div>
                  </div>

                  {app.data_residency && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500 uppercase tracking-wider">Data residency</span>
                      <span className="text-sm text-slate-300">{app.data_residency}</span>
                    </div>
                  )}
                </div>

                <div className="mt-5 pt-4 border-t border-slate-700/50">
                  <button
                    onClick={(e) => { e.stopPropagation(); openDetails(app.id) }}
                    className="w-full py-2 px-4 rounded-lg text-sm font-semibold text-white
                               bg-gradient-to-r from-blue-600/50 to-cyan-600/50
                               hover:from-blue-600 hover:to-cyan-600 transition-all"
                  >
                    View Details →
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3 mt-8">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300
                       hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            ← Previous
          </button>
          <span className="text-sm text-slate-500">{page + 1} / {lastPage + 1}</span>
          <button
            onClick={() => setPage((p) => Math.min(lastPage, p + 1))}
            disabled={page >= lastPage}
            className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300
                       hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
