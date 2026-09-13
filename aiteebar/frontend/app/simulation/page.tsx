'use client'

import React, { useState } from 'react'
import axios from 'axios'

interface SimulationEvent {
  step: number
  timestamp: string
  action: string
  status: 'pending' | 'executed' | 'blocked'
  risk_score: number
}

export default function SimulationPage() {
  const [isRunning, setIsRunning] = useState(false)
  const [events, setEvents] = useState<SimulationEvent[]>([])
  const [finalRisk, setFinalRisk] = useState(0)

  const startSimulation = async () => {
    setIsRunning(true)
    setEvents([])

    try {
      const response = await axios.get('http://localhost:8000/api/simulation/attack-sequence', {
        responseType: 'stream'
      })

      // Stream parsing would go here
      const data = await response.data.text()
      const lines = data.split('\\n').filter(l => l.trim())
      
      lines.forEach(line => {
        try {
          const event = JSON.parse(line)
          setEvents(prev => [...prev, event])
          setFinalRisk(event.risk_score)
        } catch(e) {
          // Skip invalid JSON
        }
      })
    } catch (error) {
      console.error('Simulation failed:', error)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Security Simulation</h1>
        
        <button
          onClick={startSimulation}
          disabled={isRunning}
          className="mb-8 px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400"
        >
          {isRunning ? 'Running...' : 'Start Attack Simulation'}
        </button>

        {finalRisk > 0 && (
          <div className="bg-white p-8 rounded-lg shadow mb-8">
            <h2 className="text-2xl font-bold mb-4">Risk: {finalRisk.toFixed(0)}/100</h2>
            <p className="text-lg">Status: BLOCKED ✓</p>
          </div>
        )}

        <div className="space-y-4">
          {events.map((event, idx) => (
            <div key={idx} className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-bold">Step {event.step}: {event.action}</h3>
              <p className="text-sm text-gray-600">Status: {event.status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
