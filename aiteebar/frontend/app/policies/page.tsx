'use client'

import React, { useState, useEffect } from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { api } from '@/lib/api'

interface Trigger {
  field: string
  operator: string
  value: string
}

interface PolicyCondition {
  entity_type?: string
  triggers: Trigger[]
  logic: 'AND' | 'OR'
}

interface Policy {
  id: string
  name: string
  description?: string
  condition: PolicyCondition
  action: PolicyAction
  priority: number
  enabled: boolean
  created_at: string
}

type PolicyAction = 'ALLOW' | 'WARN' | 'REQUIRE_APPROVAL' | 'BLOCK'

// Mirrors PolicyEngine._evaluate_trigger in the backend.
const OPERATORS = [
  { value: 'equals', label: 'equals' },
  { value: 'contains', label: 'contains' },
  { value: 'starts_with', label: 'starts with' },
  { value: 'ends_with', label: 'ends with' },
  { value: 'in', label: 'in list (comma-separated)' },
  { value: 'greater_than', label: 'greater than' },
  { value: 'less_than', label: 'less than' },
  { value: 'regex', label: 'matches regex' },
]

// Fields available on the event dict the policy engine evaluates against.
const FIELDS = [
  'data_type',
  'destination',
  'source',
  'event_type',
  'agent_id',
  'tool_name',
  'action_type',
  'risk_score',
  'user_role',
]

const ACTIONS: { value: PolicyAction; label: string; badge: string }[] = [
  { value: 'ALLOW', label: 'Allow', badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
  { value: 'WARN', label: 'Warn', badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
  { value: 'REQUIRE_APPROVAL', label: 'Require Approval', badge: 'bg-sky-500/15 text-sky-300 border-sky-500/30' },
  { value: 'BLOCK', label: 'Block', badge: 'bg-red-500/15 text-red-300 border-red-500/30' },
]

const EMPTY_FORM = {
  name: '',
  description: '',
  entity_type: 'agent',
  action: 'WARN' as PolicyAction,
  priority: 100,
  enabled: true,
  logic: 'AND' as 'AND' | 'OR',
  triggers: [{ field: 'data_type', operator: 'equals', value: '' }] as Trigger[],
}

const inputClass =
  'w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100 ' +
  'placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 transition-colors'

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)

  useEffect(() => {
    loadPolicies()
  }, [])

  const loadPolicies = async () => {
    setLoading(true)
    try {
      const response = await api.get<Policy[]>('/policies')
      setPolicies(response.data)
      setError('')
    } catch (err: any) {
      setError(describeError(err, 'Could not load policies'))
    } finally {
      setLoading(false)
    }
  }

  // The write endpoints are admin-only, so surface the reason rather than
  // letting the request fail silently.
  const describeError = (err: any, fallback: string) => {
    const status = err?.response?.status
    if (status === 401) return 'Not signed in. Sign in as an admin to manage policies.'
    if (status === 403) return 'Your account is not an admin. Only admins can manage policies.'
    return err?.response?.data?.detail || fallback
  }

  const openCreate = () => {
    setForm(EMPTY_FORM)
    setEditingId(null)
    setError('')
    setShowForm(true)
  }

  const openEdit = (policy: Policy) => {
    setForm({
      name: policy.name,
      description: policy.description || '',
      entity_type: policy.condition?.entity_type || 'agent',
      action: policy.action,
      priority: policy.priority,
      enabled: policy.enabled,
      logic: policy.condition?.logic || 'AND',
      triggers: policy.condition?.triggers?.length
        ? policy.condition.triggers
        : [{ field: 'data_type', operator: 'equals', value: '' }],
    })
    setEditingId(policy.id)
    setError('')
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  const updateTrigger = (index: number, key: keyof Trigger, value: string) => {
    setForm({
      ...form,
      triggers: form.triggers.map((t, i) => (i === index ? { ...t, [key]: value } : t)),
    })
  }

  const addTrigger = () => {
    setForm({
      ...form,
      triggers: [...form.triggers, { field: 'data_type', operator: 'equals', value: '' }],
    })
  }

  const removeTrigger = (index: number) => {
    setForm({ ...form, triggers: form.triggers.filter((_, i) => i !== index) })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!form.name.trim()) {
      setError('Policy name is required')
      return
    }
    if (form.triggers.some((t) => !t.field || !t.value.trim())) {
      setError('Every condition needs a field and a value')
      return
    }

    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      condition: {
        entity_type: form.entity_type,
        triggers: form.triggers,
        logic: form.logic,
      },
      action: form.action,
      priority: form.priority,
      enabled: form.enabled,
    }

    setSaving(true)
    setError('')
    try {
      if (editingId) {
        await api.put(`/policies/${editingId}`, payload)
      } else {
        await api.post('/policies', payload)
      }
      closeForm()
      await loadPolicies()
    } catch (err: any) {
      setError(describeError(err, 'Could not save policy'))
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (policy: Policy) => {
    if (!confirm(`Delete policy "${policy.name}"? This cannot be undone.`)) return

    try {
      await api.delete(`/policies/${policy.id}`)
      await loadPolicies()
    } catch (err: any) {
      setError(describeError(err, 'Could not delete policy'))
    }
  }

  const badgeFor = (action: PolicyAction) =>
    ACTIONS.find((a) => a.value === action)?.badge ||
    'bg-slate-500/15 text-slate-300 border-slate-500/30'

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <div className="max-w-5xl mx-auto">
        <PageHeader
          title="Security Policies"
          description="Define and enforce rules that allow, warn, gate, or block agent activity"
          actions={
            <button
              onClick={showForm ? closeForm : openCreate}
              className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition-colors"
            >
              {showForm ? 'Cancel' : '+ Create Policy'}
            </button>
          }
        />

        {error && (
          <div className="mb-6 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        {showForm && (
          <Card
            className="mb-8"
            title={editingId ? 'Edit Policy' : 'New Policy'}
            subtitle="Conditions are evaluated against each security event in priority order"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Name</label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="Block Confidential Data Exfiltration"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Action</label>
                  <select
                    value={form.action}
                    onChange={(e) => setForm({ ...form, action: e.target.value as PolicyAction })}
                    className={inputClass}
                  >
                    {ACTIONS.map((a) => (
                      <option key={a.value} value={a.value}>
                        {a.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-2">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={2}
                  placeholder="Optional. What this policy protects against."
                  className={inputClass}
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm text-slate-400">Conditions</label>
                  <div className="flex items-center gap-3">
                    <select
                      value={form.logic}
                      onChange={(e) => setForm({ ...form, logic: e.target.value as 'AND' | 'OR' })}
                      className="px-3 py-1.5 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-200 text-sm"
                    >
                      <option value="AND">Match ALL (AND)</option>
                      <option value="OR">Match ANY (OR)</option>
                    </select>
                    <button
                      type="button"
                      onClick={addTrigger}
                      className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-100 text-sm transition-colors"
                    >
                      + Condition
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  {form.triggers.map((trigger, index) => (
                    <div key={index} className="flex flex-wrap gap-2 items-center">
                      <select
                        value={trigger.field}
                        onChange={(e) => updateTrigger(index, 'field', e.target.value)}
                        className={`${inputClass} flex-1 min-w-[9rem]`}
                      >
                        {FIELDS.map((f) => (
                          <option key={f} value={f}>
                            {f}
                          </option>
                        ))}
                      </select>

                      <select
                        value={trigger.operator}
                        onChange={(e) => updateTrigger(index, 'operator', e.target.value)}
                        className={`${inputClass} flex-1 min-w-[9rem]`}
                      >
                        {OPERATORS.map((op) => (
                          <option key={op.value} value={op.value}>
                            {op.label}
                          </option>
                        ))}
                      </select>

                      <input
                        type="text"
                        value={trigger.value}
                        onChange={(e) => updateTrigger(index, 'value', e.target.value)}
                        placeholder="CNIC"
                        className={`${inputClass} flex-1 min-w-[9rem]`}
                      />

                      <button
                        type="button"
                        onClick={() => removeTrigger(index)}
                        disabled={form.triggers.length === 1}
                        className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-red-500/20 text-slate-400 hover:text-red-300 disabled:opacity-30 disabled:hover:bg-slate-800 disabled:hover:text-slate-400 transition-colors"
                        title={form.triggers.length === 1 ? 'A policy needs at least one condition' : 'Remove'}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-4 items-end">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Applies to</label>
                  <select
                    value={form.entity_type}
                    onChange={(e) => setForm({ ...form, entity_type: e.target.value })}
                    className={inputClass}
                  >
                    <option value="agent">Agent</option>
                    <option value="application">Application</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Priority <span className="text-slate-500">(lower wins)</span>
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={form.priority}
                    onChange={(e) => setForm({ ...form, priority: parseInt(e.target.value) || 0 })}
                    className={inputClass}
                  />
                </div>

                <label className="flex items-center gap-2 cursor-pointer pb-2">
                  <input
                    type="checkbox"
                    checked={form.enabled}
                    onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
                    className="w-4 h-4 accent-cyan-500"
                  />
                  <span className="text-sm text-slate-300">Enabled</span>
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={closeForm}
                  className="px-5 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium transition-colors"
                >
                  {saving ? 'Saving…' : editingId ? 'Save Changes' : 'Create Policy'}
                </button>
              </div>
            </form>
          </Card>
        )}

        <div className="space-y-4">
          {loading ? (
            <Card>
              <p className="text-center text-slate-400 py-6">Loading policies…</p>
            </Card>
          ) : policies.length === 0 ? (
            <Card>
              <div className="text-center py-10">
                <p className="text-slate-300 font-medium">No policies yet</p>
                <p className="text-slate-500 text-sm mt-1">
                  Create one to start enforcing rules on agent activity.
                </p>
              </div>
            </Card>
          ) : (
            policies.map((policy) => (
              <Card key={policy.id}>
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-100">{policy.name}</h3>
                    {policy.description && (
                      <p className="text-sm text-slate-400 mt-1">{policy.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-2.5 py-1 rounded-md border text-xs font-semibold ${badgeFor(policy.action)}`}>
                      {policy.action}
                    </span>
                    {!policy.enabled && (
                      <span className="px-2.5 py-1 rounded-md border border-slate-600 text-slate-400 text-xs">
                        Disabled
                      </span>
                    )}
                  </div>
                </div>

                <div className="rounded-lg bg-slate-900/60 border border-slate-700/50 p-3 mb-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">
                    Match {policy.condition?.logic === 'OR' ? 'any' : 'all'}
                  </p>
                  <ul className="space-y-1">
                    {(policy.condition?.triggers || []).map((trigger, i) => (
                      <li key={i} className="text-sm font-mono text-slate-300">
                        <span className="text-cyan-400">{trigger.field}</span>{' '}
                        <span className="text-slate-500">{trigger.operator}</span>{' '}
                        <span className="text-amber-300">&quot;{trigger.value}&quot;</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">Priority {policy.priority}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openEdit(policy)}
                      className="px-3 py-1.5 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(policy)}
                      className="px-3 py-1.5 rounded-lg text-sm text-red-400 hover:bg-red-500/15 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
