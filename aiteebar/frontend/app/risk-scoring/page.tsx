'use client'

import React, { useState } from 'react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { MetricCard } from '@/components/MetricCard'

interface RiskFactor {
  name: string
  value: number
  weight: number
  weighted_contribution: number
  explanation: string
  contributing_factors: Record<string, any>
}

interface RiskScore {
  entity_type: string
  entity_id: string
  overall_score: number
  risk_level: string
  factors: RiskFactor[]
  explanation: string
  detailed_explanation: string
  timestamp: string
}

export default function RiskScoringPage() {
  const [entityType, setEntityType] = useState('agent')
  const [entityId, setEntityId] = useState('')
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCalculate = async () => {
    if (!entityId.trim()) {
      setError('Please enter an entity ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(
        `http://localhost:8000/api/risk/score?entity_type=${entityType}&entity_id=${entityId}`
      )

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      setRiskScore(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Risk calculation failed')
      setRiskScore(null)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string): any => {
    switch (level) {
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

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return '🔴'
      case 'HIGH':
        return '🟠'
      case 'MEDIUM':
        return '🟡'
      case 'LOW':
        return '🟢'
      default:
        return '⚪'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300 mb-2">
            📊 Multi-Factor Risk Scoring
          </h1>
          <p className="text-slate-400">
            Comprehensive risk assessment combining 7 factors with explainable scoring
          </p>
        </div>

        {/* Input Section */}
        <Card className="mb-8">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Entity Type
                </label>
                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-slate-100 focus:outline-none focus:border-cyan-500"
                >
                  <option value="application">Application</option>
                  <option value="agent">Agent</option>
                  <option value="tool">Tool</option>
                  <option value="destination">Destination</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Entity ID
                </label>
                <input
                  type="text"
                  value={entityId}
                  onChange={(e) => setEntityId(e.target.value)}
                  placeholder="Paste entity UUID"
                  className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={handleCalculate}
                  disabled={loading || !entityId.trim()}
                  className="w-full px-6 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:from-slate-700 disabled:to-slate-600 text-white font-semibold rounded-lg transition-all"
                >
                  {loading ? 'Calculating...' : 'Calculate Risk'}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
                <p className="font-semibold">❌ Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}
          </div>
        </Card>

        {/* Risk Score Display */}
        {riskScore && (
          <div className="space-y-6">
            {/* Overall Score Card */}
            <Card className="border-2 border-cyan-500/30">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-slate-100">Overall Risk Score</h2>
                  <p className="text-sm text-slate-400 mt-1">{riskScore.explanation}</p>
                </div>
                <div className="text-right">
                  <div className="text-6xl font-bold text-cyan-300">
                    {riskScore.overall_score.toFixed(1)}
                  </div>
                  <div className="text-xl font-semibold mt-2">
                    <Badge variant={getRiskColor(riskScore.risk_level)}>
                      {getRiskIcon(riskScore.risk_level)} {riskScore.risk_level}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Risk Gauge */}
              <div className="mt-6">
                <div className="flex justify-between text-xs text-slate-400 mb-2">
                  <span>LOW (0)</span>
                  <span>MEDIUM (50)</span>
                  <span>HIGH (80)</span>
                  <span>CRITICAL (100)</span>
                </div>
                <div className="w-full h-4 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full relative">
                  <div
                    className="h-full rounded-full border-2 border-cyan-300 absolute"
                    style={{
                      width: '20px',
                      left: `calc(${(riskScore.overall_score / 100) * 100}% - 10px)`,
                      top: '-4px',
                      height: '24px',
                    }}
                  />
                </div>
              </div>
            </Card>

            {/* Risk Factors */}
            <Card title="🎯 Risk Factor Breakdown">
              <div className="space-y-4">
                {riskScore.factors
                  .sort((a, b) => b.weighted_contribution - a.weighted_contribution)
                  .map((factor, idx) => (
                    <div key={idx} className="border border-slate-700 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-cyan-300">{factor.name}</h4>
                          <p className="text-sm text-slate-400 mt-1">{factor.explanation}</p>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-cyan-300">
                            {factor.value.toFixed(1)}
                          </div>
                          <div className="text-xs text-slate-400">
                            Weight: {(factor.weight * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      {/* Factor Contribution Bar */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">Contribution</span>
                          <span className="text-cyan-300 font-semibold">
                            {factor.weighted_contribution.toFixed(2)}/100
                          </span>
                        </div>
                        <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                            style={{
                              width: `${(factor.weighted_contribution / 100) * 100}%`,
                            }}
                          />
                        </div>
                      </div>

                      {/* Contributing Factors */}
                      {Object.keys(factor.contributing_factors).length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-700">
                          <p className="text-xs font-semibold text-slate-400 mb-2">
                            Contributing Factors:
                          </p>
                          <div className="grid grid-cols-2 gap-2">
                            {Object.entries(factor.contributing_factors).map(([key, value]) => (
                              <div key={key} className="text-xs">
                                <span className="text-slate-400">{key}: </span>
                                <span className="text-slate-200 font-mono">
                                  {typeof value === 'object'
                                    ? JSON.stringify(value)
                                    : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </Card>

            {/* Detailed Breakdown */}
            <Card title="📋 Detailed Breakdown">
              <div className="bg-slate-900/50 p-4 rounded-lg font-mono text-sm text-slate-300 whitespace-pre-wrap">
                {riskScore.detailed_explanation}
              </div>
            </Card>

            {/* Information Panel */}
            <Card>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-cyan-300 mb-3">Risk Assessment Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Entity Type:</span>
                      <span className="text-slate-300">{riskScore.entity_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Entity ID:</span>
                      <span className="text-slate-300 font-mono text-xs">
                        {riskScore.entity_id.substring(0, 12)}...
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Assessment Date:</span>
                      <span className="text-slate-300">
                        {new Date(riskScore.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Factors Analyzed:</span>
                      <span className="text-slate-300">{riskScore.factors.length}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-cyan-300 mb-3">Risk Interpretation</h4>
                  <div className="space-y-2 text-sm text-slate-300">
                    <p>
                      • <strong>LOW (0-40):</strong> Minimal risk, standard monitoring
                    </p>
                    <p>
                      • <strong>MEDIUM (40-60):</strong> Monitor, schedule review
                    </p>
                    <p>
                      • <strong>HIGH (60-80):</strong> Restrict access, increase monitoring
                    </p>
                    <p>
                      • <strong>CRITICAL (80-100):</strong> Isolate, immediate investigation
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Explanation of Factors */}
        {!riskScore && (
          <Card title="📖 Risk Factor Explanation">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                {
                  name: 'Application Risk',
                  weight: 25,
                  desc: 'Risk score and security assessment of the parent application',
                },
                {
                  name: 'Agent Privilege Level',
                  weight: 20,
                  desc: 'Number of tools, data access scope, and agent status',
                },
                {
                  name: 'Data Sensitivity Level',
                  weight: 25,
                  desc: 'Types of sensitive data being accessed (CNIC, IBAN, etc)',
                },
                {
                  name: 'Tool Permission Scope',
                  weight: 15,
                  desc: 'Risk level and permissions of connected tools',
                },
                {
                  name: 'Destination Risk',
                  weight: 10,
                  desc: 'Internal vs external connections and destination risk scores',
                },
                {
                  name: 'Behavior Anomaly Score',
                  weight: 5,
                  desc: 'Detected threats and behavioral anomalies from threat detection',
                },
              ].map((factor, idx) => (
                <div key={idx} className="border border-slate-700 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-cyan-300">{factor.name}</h4>
                    <Badge variant="default">{factor.weight}%</Badge>
                  </div>
                  <p className="text-sm text-slate-400">{factor.desc}</p>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
