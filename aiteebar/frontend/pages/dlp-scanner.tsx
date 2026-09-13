'use client'

import React, { useState } from 'react'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { Table } from '../components/Table'

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

export default function DLPScanner() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
          source: 'dlp_demo_interface',
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300 mb-2">
            🛡️ DLP Scanner
          </h1>
          <p className="text-slate-400">
            Detect sensitive data in real-time using pattern matching
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-2">
            <Card className="h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-cyan-300">Text Input</h2>
                <span className="text-sm text-slate-400">
                  {text.length} characters
                </span>
              </div>

              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste text to scan for sensitive data... (emails, API keys, passwords, credit cards, etc)"
                className="flex-1 p-4 rounded-lg bg-slate-700/50 border border-slate-600/50 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 resize-none font-mono text-sm"
              />

              <div className="flex gap-3 mt-4">
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
            </Card>
          </div>

          {/* Info Panel */}
          <div className="flex flex-col gap-4">
            {/* Detected Types */}
            <Card className="flex-1">
              <h3 className="text-lg font-semibold text-cyan-300 mb-4">
                📊 Data Types
              </h3>
              {result ? (
                <div className="space-y-2">
                  {result.data_types_found.length > 0 ? (
                    result.data_types_found.map((type) => (
                      <Badge key={type} variant="default" className="block text-center">
                        {type}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-slate-400 text-sm">No sensitive data found</p>
                  )}
                </div>
              ) : (
                <p className="text-slate-400 text-sm">Run a scan to see detected types</p>
              )}
            </Card>

            {/* Stats */}
            {result && (
              <>
                <Card>
                  <h3 className="text-lg font-semibold text-cyan-300 mb-4">
                    ⚡ Statistics
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Total Detections</span>
                      <span className="text-cyan-300 font-semibold">
                        {result.total_detections}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Scan Time</span>
                      <span className="text-cyan-300 font-semibold">
                        {result.processing_time_ms.toFixed(2)}ms
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Text Length</span>
                      <span className="text-cyan-300 font-semibold">
                        {result.text_length} chars
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Scan ID</span>
                      <span className="text-cyan-300 font-semibold text-xs">
                        {result.scan_id.substring(0, 10)}...
                      </span>
                    </div>
                  </div>
                </Card>

                {/* Severity Breakdown */}
                <Card>
                  <h3 className="text-lg font-semibold text-cyan-300 mb-4">
                    🎚️ Severity
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(result.severity_breakdown).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between">
                        <Badge variant={getSeverityColor(severity)}>
                          {severity}: {count}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
            <p className="font-semibold">❌ Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Results Table */}
        {result && result.detections.length > 0 && (
          <div className="mt-6">
            <Card className="bg-slate-800/50">
              <h2 className="text-xl font-semibold text-cyan-300 mb-4">
                🔍 Detection Results ({result.total_detections})
              </h2>

              <div className="overflow-x-auto">
                <Table
                  columns={[
                    {
                      key: 'data_type' as const,
                      label: 'Type',
                      render: (value) => (
                        <span className="font-mono text-sm text-cyan-300">
                          {value}
                        </span>
                      ),
                    },
                    {
                      key: 'severity' as const,
                      label: 'Severity',
                      render: (value) => (
                        <Badge variant={getSeverityColor(value)}>
                          {value}
                        </Badge>
                      ),
                    },
                    {
                      key: 'confidence' as const,
                      label: 'Confidence',
                      render: (value) => (
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${
                                value >= 90
                                  ? 'bg-red-500'
                                  : value >= 70
                                    ? 'bg-orange-500'
                                    : 'bg-yellow-500'
                              }`}
                              style={{ width: `${value}%` }}
                            />
                          </div>
                          <span className="text-sm text-slate-300">
                            {value.toFixed(1)}%
                          </span>
                        </div>
                      ),
                    },
                    {
                      key: 'matched_content' as const,
                      label: 'Matched',
                      render: (value) => (
                        <code className="text-xs bg-slate-900/50 px-2 py-1 rounded text-slate-300">
                          {value}
                        </code>
                      ),
                    },
                    {
                      key: 'position' as const,
                      label: 'Position',
                      render: (value) => (
                        <span className="text-slate-400 text-sm">
                          char {value}
                        </span>
                      ),
                    },
                  ]}
                  data={result.detections}
                  rowKey={(row) => `${row.position}-${row.data_type}`}
                />
              </div>
            </Card>
          </div>
        )}

        {/* Empty State */}
        {result && result.detections.length === 0 && (
          <div className="mt-6 p-8 text-center border border-dashed border-slate-600 rounded-lg">
            <p className="text-4xl mb-3">✅</p>
            <h3 className="text-lg font-semibold text-green-300 mb-2">
              No Sensitive Data Detected
            </h3>
            <p className="text-slate-400">
              The scanned text does not contain any detectable sensitive data patterns
            </p>
          </div>
        )}

        {/* Test Examples */}
        <div className="mt-12">
          <Card>
            <h3 className="text-lg font-semibold text-cyan-300 mb-4">
              📝 Test Examples
            </h3>
            <p className="text-slate-400 text-sm mb-4">
              Try pasting these examples to see DLP detection in action:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                {
                  label: 'Email + Phone',
                  text: 'Contact me at john.doe@company.com or +1-555-123-4567',
                },
                {
                  label: 'API Key',
                  text: 'My API key is sk_live_4eC39HqLyjWDarhtT663 for production',
                },
                {
                  label: 'Credentials',
                  text: 'password = "MySecurePass123" and API_KEY="abc123def456"',
                },
                {
                  label: 'CNIC',
                  text: 'My CNIC is 12345-6789012-1',
                },
              ].map((example) => (
                <button
                  key={example.label}
                  onClick={() => setText(example.text)}
                  className="p-3 text-left border border-slate-600/50 rounded-lg hover:border-cyan-500/50 hover:bg-slate-800/50 transition-all"
                >
                  <p className="font-semibold text-slate-300 text-sm mb-1">
                    {example.label}
                  </p>
                  <p className="text-xs text-slate-400 font-mono truncate">
                    {example.text}
                  </p>
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
