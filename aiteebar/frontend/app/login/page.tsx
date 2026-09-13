'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import { setAccessToken, setCurrentUser, validatePassword } from '@/lib/auth'
import { DEMO_CREDENTIALS } from '@/lib/constants'
import { Card } from '@/components/Card'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDemoHint, setShowDemoHint] = useState(true)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await api.login(email, password)

      if (response.data.access_token) {
        setAccessToken(response.data.access_token)

        // Fetch current user
        try {
          const userResponse = await api.getCurrentUser()
          setCurrentUser(userResponse.data)
        } catch (err) {
          console.error('Failed to fetch user:', err)
        }

        router.push('/dashboard')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Invalid email or password'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = async (credentials: typeof DEMO_CREDENTIALS.ADMIN) => {
    setEmail(credentials.email)
    setPassword(credentials.password)
    setShowDemoHint(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🔒</div>
          <h1 className="text-4xl font-bold text-slate-100 mb-2">Aiteebar</h1>
          <p className="text-slate-400">AI-Powered Security Intelligence</p>
        </div>

        {/* Login Form */}
        <Card className="mb-6">
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-slate-700 text-slate-100 rounded-lg px-4 py-2 border border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-700 text-slate-100 rounded-lg px-4 py-2 border border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                required
              />
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-900/20 border border-red-700 text-red-400 px-4 py-2 rounded">
                {error}
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2 rounded-lg transition-colors"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </Card>

        {/* Demo credentials */}
        {showDemoHint && (
          <Card className="bg-blue-900/20 border-blue-700 mb-6">
            <div>
              <h3 className="font-semibold text-blue-400 mb-3">Demo Credentials</h3>
              <div className="space-y-2 text-sm">
                {[
                  { label: 'Admin', cred: DEMO_CREDENTIALS.ADMIN },
                  { label: 'Analyst', cred: DEMO_CREDENTIALS.ANALYST },
                  { label: 'Viewer', cred: DEMO_CREDENTIALS.VIEWER },
                ].map(({ label, cred }) => (
                  <button
                    key={cred.email}
                    type="button"
                    onClick={() => handleDemoLogin(cred)}
                    className="w-full text-left px-3 py-2 bg-slate-800/50 hover:bg-slate-700 rounded border border-slate-600 transition-colors"
                  >
                    <div className="font-medium text-slate-300">{label}</div>
                    <div className="text-xs text-slate-400">{cred.email}</div>
                  </button>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-slate-400 text-sm">
          <p>This is a demo application</p>
          <p className="mt-2">
            <Link href="/" className="text-blue-400 hover:text-blue-300">
              Back to home
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
