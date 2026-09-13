'use client'

import React, { useState, useEffect } from 'react'
import axios from 'axios'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'

interface Policy {
  id: string
  name: string
  description?: string
  action: 'ALLOW' | 'WARN' | 'REQUIRE_APPROVAL' | 'BLOCK'
  priority: number
  enabled: boolean
  created_at: string
}

const ACTIONS = [
  { value: 'ALLOW', label: 'Allow', color: 'bg-green-100' },
  { value: 'WARN', label: 'Warn', color: 'bg-yellow-100' },
  { value: 'REQUIRE_APPROVAL', label: 'Require Approval', color: 'bg-blue-100' },
  { value: 'BLOCK', label: 'Block', color: 'bg-red-100' },
]

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPolicies()
  }, [])

  const fetchPolicies = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/policies')
      setPolicies(response.data)
    } catch (error) {
      console.error('Failed to fetch policies:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <PageHeader
        title="Security Policies"
        subtitle="Define and enforce security policies for data protection"
      />

      <div className="max-w-7xl mx-auto mt-8">
        <button className="mb-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Create Policy
        </button>

        <div className="space-y-4">
          {loading ? (
            <p>Loading policies...</p>
          ) : policies.length === 0 ? (
            <Card>
              <p className="text-center text-gray-500 py-8">No policies configured</p>
            </Card>
          ) : (
            policies.map(policy => (
              <Card key={policy.id} className="p-6">
                <h3 className="text-xl font-bold">{policy.name}</h3>
                <span className="text-sm font-medium">{policy.action}</span>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
