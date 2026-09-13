'use client'

import React, { useEffect, useState } from 'react'
import PageHeader from '@/components/PageHeader'
import { api } from '@/lib/api'

interface MatrixTechnique {
  id: string
  name: string
  detected: boolean
  subtechnique_count: number
}

interface MatrixTactic {
  id: string
  name: string
  techniques: MatrixTechnique[]
}

interface Matrix {
  provenance: { source: string; retrieved: string; note: string }
  tactics: MatrixTactic[]
}

interface Coverage {
  covered_count: number
  total_techniques: number
  coverage_percent: number
}

interface DetectedBy {
  detection: string
  type: string
  confidence: string
  rationale: string
}

interface TechniqueDetail {
  id: string
  name: string
  url: string
  tactics: { id: string; name: string }[]
  subtechniques: { id: string; name: string }[]
  detected: boolean
  detected_by: DetectedBy[]
}

export default function AtlasPage() {
  const [matrix, setMatrix] = useState<Matrix | null>(null)
  const [coverage, setCoverage] = useState<Coverage | null>(null)
  const [selected, setSelected] = useState<TechniqueDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [detectedOnly, setDetectedOnly] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const [m, c] = await Promise.all([
          api.get<Matrix>('/atlas/matrix'),
          api.get<Coverage>('/atlas/coverage'),
        ])
        setMatrix(m.data)
        setCoverage(c.data)
        setError('')
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Could not load the ATLAS matrix')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const openTechnique = async (id: string) => {
    try {
      const response = await api.get<TechniqueDetail>(`/atlas/techniques/${id}`)
      setSelected(response.data)
    } catch {
      setError(`Could not load ${id}`)
    }
  }

  if (loading) {
    return <div className="py-20 text-center text-slate-400">Loading ATLAS matrix…</div>
  }

  if (error && !matrix) {
    return <div className="py-20 text-center text-red-300">{error}</div>
  }

  return (
    <div>
      <PageHeader
        title="MITRE ATLAS"
        description="Adversarial threat coverage for AI systems"
        backHref="/dashboard"
      />

      {coverage && (
        <div className="grid sm:grid-cols-3 gap-4 mb-6">
          <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
            <p className="text-xs uppercase tracking-wider text-slate-500">Techniques detected</p>
            <p className="text-3xl font-bold text-cyan-300 mt-1">
              {coverage.covered_count}
              <span className="text-lg text-slate-500"> / {coverage.total_techniques}</span>
            </p>
          </div>
          <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
            <p className="text-xs uppercase tracking-wider text-slate-500">Coverage</p>
            <p className="text-3xl font-bold text-slate-100 mt-1">{coverage.coverage_percent}%</p>
            <div className="h-1.5 rounded-full bg-slate-900 mt-3 overflow-hidden">
              <div className="h-full bg-cyan-500" style={{ width: `${coverage.coverage_percent}%` }} />
            </div>
          </div>
          <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
            <p className="text-xs uppercase tracking-wider text-slate-500">Not covered</p>
            <p className="text-3xl font-bold text-slate-400 mt-1">
              {coverage.total_techniques - coverage.covered_count}
            </p>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={detectedOnly}
            onChange={(e) => setDetectedOnly(e.target.checked)}
            className="w-4 h-4 accent-cyan-500"
          />
          <span className="text-sm text-slate-300">Show only what we detect</span>
        </label>
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded border border-cyan-500/50 bg-cyan-500/20 inline-block" />
            Detected
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded border border-slate-700 bg-slate-800/40 inline-block" />
            Not covered
          </span>
        </div>
      </div>

      <div className="overflow-x-auto pb-4">
        <div className="flex gap-3 min-w-max">
          {matrix?.tactics.map((tactic) => {
            const shown = detectedOnly
              ? tactic.techniques.filter((t) => t.detected)
              : tactic.techniques
            const hits = tactic.techniques.filter((t) => t.detected).length

            return (
              <div key={tactic.id} className="w-56 shrink-0">
                <div className="mb-2 px-1">
                  <p className="text-sm font-semibold text-slate-200 leading-tight">{tactic.name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {hits}/{tactic.techniques.length} · {tactic.id}
                  </p>
                </div>

                <div className="space-y-1.5">
                  {shown.map((technique) => (
                    <button
                      key={technique.id}
                      onClick={() => openTechnique(technique.id)}
                      className={`w-full text-left px-2.5 py-2 rounded border text-xs transition-colors ${
                        technique.detected
                          ? 'border-cyan-500/50 bg-cyan-500/15 text-cyan-100 hover:bg-cyan-500/25'
                          : 'border-slate-700/60 bg-slate-800/40 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                      }`}
                    >
                      <span className="block leading-snug">{technique.name}</span>
                      <span className="block text-[10px] opacity-60 mt-0.5 font-mono">
                        {technique.id}
                        {technique.subtechnique_count > 0 && ` · ${technique.subtechnique_count} sub`}
                      </span>
                    </button>
                  ))}
                  {shown.length === 0 && (
                    <p className="text-xs text-slate-600 px-2 py-3">none detected</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {matrix && (
        <p className="text-xs text-slate-600 mt-2">
          Reference data retrieved {matrix.provenance.retrieved} from {matrix.provenance.source}
        </p>
      )}

      {selected && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-slate-700/60 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-mono text-slate-500">{selected.id}</p>
                <h3 className="text-xl font-bold text-slate-100 mt-1">{selected.name}</h3>
                <p className="text-sm text-slate-400 mt-1">
                  {selected.tactics.map((t) => t.name).join(' · ')}
                </p>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-slate-500 hover:text-slate-200 text-xl leading-none"
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-5">
              <div>
                <span className={`inline-block px-3 py-1 rounded text-sm font-semibold border ${
                  selected.detected
                    ? 'border-cyan-500/40 bg-cyan-500/15 text-cyan-300'
                    : 'border-slate-600 bg-slate-800 text-slate-400'
                }`}>
                  {selected.detected ? 'Detected by this platform' : 'Not covered'}
                </span>
              </div>

              {selected.detected_by.length > 0 ? (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">Detected by</p>
                  <div className="space-y-3">
                    {selected.detected_by.map((d, i) => (
                      <div key={i} className="rounded-lg bg-slate-800/60 border border-slate-700/50 p-3">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-sm font-medium text-slate-200 font-mono">
                            {d.detection}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded border ${
                            d.confidence === 'direct'
                              ? 'border-emerald-500/40 text-emerald-300 bg-emerald-500/10'
                              : 'border-amber-500/40 text-amber-300 bg-amber-500/10'
                          }`}>
                            {d.confidence}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{d.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500">
                  Nothing in the platform currently detects this technique.
                </p>
              )}

              {selected.subtechniques.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">
                    Sub-techniques
                  </p>
                  <ul className="space-y-1">
                    {selected.subtechniques.map((sub) => (
                      <li key={sub.id} className="text-sm text-slate-300">
                        <span className="font-mono text-xs text-slate-500 mr-2">{sub.id}</span>
                        {sub.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <a
                href={selected.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-sm text-cyan-400 hover:text-cyan-300"
              >
                View on atlas.mitre.org →
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
