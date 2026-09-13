'use client'

import React, { useState } from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Table } from '@/components/Table'

interface Detection {
  data_type: string
  confidence: number
  severity: string
  matched_content: string
  context: string
  position: number
}

interface ScanResult {
  success: boolean
  scan_id: string
  timestamp: string
  text_length: number
  total_detections: number
  detections: Detection[]
  severity_breakdown: Record<string, number>
  data_types_found: string[]
  processing_time_ms: number
}

interface DLPViolation {
  id: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  action: string
}

export default function DLPPage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const violations: DLPViolation[] = [
    {
      id: '1',
      type: 'Credit Card Detected',
      severity: 'critical',
      timestamp: '2024-01-15T10:30:00Z',
      action: 'Blocked',
    },
    {
      id: '2',
      type: 'API Key Exposure',
      severity: 'high',
      timestamp: '2024-01-15T09:15:00Z',
      action: 'Quarantined',
    },
    {
      id: '3',
      type: 'PII Fragment Match',
      severity: 'medium',
      timestamp: '2024-01-14T15:45:00Z',
      action: 'Logged',
    },
  ]

  const handleScan = async () => {
    if (!text.trim()) {
      setError('Please enter text to scan')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/dlp/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          source: 'dlp_scanner',
          scan_id: `scan_${Date.now()}`,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string): any => {
    switch (severity) {
      case 'CRITICAL':
        return 'critical'
      case 'HIGH':
        return 'high'
      case 'MEDIUM':
        return 'medium'
      case 'LOW':
        return 'low'
      default:
        return 'default'
    }
  }

  const handleClear = () => {
    setText('')
    setResult(null)
    setError('')
  }

  return (
    <div>
      <PageHeader
        title="Data Loss Prevention"
        description="Monitor and scan for sensitive data detection with pattern matching"
        backHref="/dashboard"
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-400">12</div>
            <div className="text-sm text-slate-400 mt-2">Total Violations</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-400">3</div>
            <div className="text-sm text-slate-400 mt-2">This Month</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400">92%</div>
            <div className="text-sm text-slate-400 mt-2">Blocked Rate</div>
          </div>
        </Card>
      </div>

      {/* Scanner Section */}
      <Card title="🔍 Real-Time Scanner" className="mb-8">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Text to Scan ({text.length} characters)
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste text to scan for sensitive data... (emails, API keys, passwords, credit cards, CNIC, IBAN, etc)"
              className="w-full p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 resize-none font-mono text-sm"
              rows={6}
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleScan}
              disabled={loading || !text.trim()}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:from-slate-700 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Scanning...
                </>
              ) : (
                <>
                  <span>🔍</span>
                  Scan Text
                </>
              )}
            </button>
            <button
              onClick={handleClear}
              disabled={loading}
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 disabled:cursor-not-allowed text-slate-100 font-semibold rounded-lg transition-all duration-200"
            >
              Clear
            </button>
          </div>

          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
              <p className="font-semibold">❌ Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4 pt-4 border-t border-slate-700/50">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 p-3 rounded-lg">
                  <div className="text-sm text-slate-400">Total Detections</div>
                  <div className="text-2xl font-bold text-cyan-300">
                    {result.total_detections}
                  </div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded-lg">
                  <div className="text-sm text-slate-400">Scan Time</div>
                  <div className="text-2xl font-bold text-cyan-300">
                    {result.processing_time_ms.toFixed(2)}ms
                  </div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded-lg">
                  <div className="text-sm text-slate-400">Data Types</div>
                  <div className="text-2xl font-bold text-cyan-300">
                    {result.data_types_found.length}
                  </div>
                </div>
                <div className="bg-slate-800/50 p-3 rounded-lg">
                  <div className="text-sm text-slate-400">Text Length</div>
                  <div className="text-2xl font-bold text-cyan-300">
                    {result.text_length}
                  </div>
                </div>
              </div>

              {result.total_detections === 0 ? (
                <div className="p-6 text-center border border-dashed border-slate-600 rounded-lg">
                  <p className="text-4xl mb-3">✅</p>
                  <p className="text-green-300 font-semibold">No Sensitive Data Detected</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(result.severity_breakdown).map(([severity, count]) => (
                      <div
                        key={severity}
                        className="bg-slate-800/50 p-3 rounded-lg text-center border border-slate-600/50"
                      >
                        <div className="text-sm text-slate-400 mb-1">{severity}</div>
                        <Badge variant={getSeverityColor(severity)} className="block">
                          {count} found
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Scan Results Table */}
      {result && result.detections.length > 0 && (
        <Card title={`📊 Detection Results (${result.total_detections})`} className="mb-8">
          <Table<Detection>
            columns={[
              {
                key: 'data_type',
                label: 'Type',
                render: (value) => (
                  <span className="font-mono text-sm text-cyan-300">{value}</span>
                ),
              },
              {
                key: 'severity',
                label: 'Severity',
                render: (value) => (
                  <Badge variant={getSeverityColor(value)}>{value}</Badge>
                ),
              },
              {
                key: 'confidence',
                label: 'Confidence',
                render: (value) => (
                  <div className="flex items-center gap-2">
                    <div className="w-12 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          value >= 90
                            ? 'bg-red-500'
                            : value >= 70
                              ? 'bg-orange-500'
                              : 'bg-yellow-500'
                        }`}
                        style={{ width: `${value}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-300">{value.toFixed(0)}%</span>
                  </div>
                ),
              },
              {
                key: 'matched_content',
                label: 'Content',
                render: (value) => (
                  <code className="text-xs bg-slate-900/50 px-2 py-1 rounded text-slate-300">
                    {value}
                  </code>
                ),
              },
            ]}
            data={result.detections}
            rowKey={(row) => `${row.position}-${row.data_type}`}
          />
        </Card>
      )}

      {/* Historical Violations */}
      <Card title="Recent Violations">
        <Table<DLPViolation>
          columns={[
            { key: 'type', label: 'Type' },
            {
              key: 'severity',
              label: 'Severity',
              render: (severity) => (
                <Badge variant={severity as any}>
                  {severity.toUpperCase()}
                </Badge>
              ),
            },
            { key: 'action', label: 'Action Taken' },
            {
              key: 'timestamp',
              label: 'Time',
              render: (timestamp) => new Date(timestamp).toLocaleString(),
            },
          ]}
          data={violations}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
