'use client'

import React from 'react'
import PageHeader from '@/components/PageHeader'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'

export default function SettingsPage() {
  return (
    <div>
      <PageHeader
        title="Settings"
        description="Manage your account and application settings."
        backHref="/dashboard"
      />

      {/* Profile Settings */}
      <Card title="Profile Settings" subtitle="Update your account information" className="mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Full Name
            </label>
            <input
              type="text"
              defaultValue="John Doe"
              className="w-full bg-slate-700 text-slate-100 rounded-lg px-4 py-2 border border-slate-600"
              disabled
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Email Address
            </label>
            <input
              type="email"
              defaultValue="john@example.com"
              className="w-full bg-slate-700 text-slate-100 rounded-lg px-4 py-2 border border-slate-600"
              disabled
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Role
            </label>
            <div className="flex items-center">
              <Badge variant="active">Admin</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Security Settings */}
      <Card title="Security Settings" subtitle="Manage security preferences" className="mb-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
            <div>
              <div className="font-medium text-slate-100">Two-Factor Authentication</div>
              <div className="text-sm text-slate-400">Add an extra layer of security</div>
            </div>
            <Badge variant="default">Not Enabled</Badge>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
            <div>
              <div className="font-medium text-slate-100">API Keys</div>
              <div className="text-sm text-slate-400">Manage your API access tokens</div>
            </div>
            <span className="text-sm text-slate-400">3 keys</span>
          </div>
        </div>
      </Card>

      {/* Notifications */}
      <Card title="Notifications" subtitle="Manage notification preferences" className="mb-6">
        <div className="space-y-3">
          {[
            { name: 'Critical Alerts', enabled: true },
            { name: 'High Priority Events', enabled: true },
            { name: 'Policy Violations', enabled: false },
            { name: 'Weekly Reports', enabled: true },
          ].map((notification) => (
            <div key={notification.name} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
              <span className="text-slate-300">{notification.name}</span>
              <input
                type="checkbox"
                defaultChecked={notification.enabled}
                className="w-4 h-4"
                disabled
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Integrations */}
      <Card title="Integrations" subtitle="Manage connected services" className="mb-6">
        <div className="space-y-3">
          {[
            { name: 'Slack', connected: true },
            { name: 'PagerDuty', connected: false },
            { name: 'Datadog', connected: true },
            { name: 'Splunk', connected: false },
          ].map((integration) => (
            <div key={integration.name} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
              <span className="text-slate-300">{integration.name}</span>
              <Badge variant={integration.connected ? 'active' : 'inactive'}>
                {integration.connected ? '✓ Connected' : 'Disconnected'}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
