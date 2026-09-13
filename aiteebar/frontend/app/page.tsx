'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { isAuthenticated } from '@/lib/auth'
import { Navbar } from '@/components/Navbar'

export default function Home() {
  const router = useRouter()
  const authenticated = isAuthenticated()

  useEffect(() => {
    if (authenticated) {
      router.push('/dashboard')
    }
  }, [authenticated, router])

  if (authenticated) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Redirecting to dashboard...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold">🔒 Aiteebar AI Security</h1>
            </div>
            <div className="flex gap-4">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 rounded"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h2 className="text-5xl font-bold mb-6">
            AI-Powered Security Intelligence
          </h2>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Advanced threat detection, vulnerability assessment, and security analysis
            powered by artificial intelligence. Protect your AI infrastructure today.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold inline-block"
            >
              Get Started
            </Link>
            <button className="px-8 py-3 border border-blue-500 text-blue-400 hover:bg-blue-950 rounded-lg font-semibold">
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-slate-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold mb-12 text-center">Key Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-slate-700 p-6 rounded-lg">
              <div className="text-4xl mb-4">🔍</div>
              <h4 className="text-xl font-bold mb-2">Threat Detection</h4>
              <p className="text-slate-300">
                Real-time threat detection and vulnerability scanning with AI-powered analysis.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-slate-700 p-6 rounded-lg">
              <div className="text-4xl mb-4">📊</div>
              <h4 className="text-xl font-bold mb-2">Intelligence Reports</h4>
              <p className="text-slate-300">
                Comprehensive threat intelligence dashboards with actionable insights.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-slate-700 p-6 rounded-lg">
              <div className="text-4xl mb-4">🛡️</div>
              <h4 className="text-xl font-bold mb-2">Risk Management</h4>
              <p className="text-slate-300">
                Advanced risk scoring and prioritization to focus on critical threats.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Status Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-slate-800 p-8 rounded-lg border border-slate-700">
          <h3 className="text-2xl font-bold mb-4">Getting Started</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-2xl">1️⃣</span>
              <div>
                <div className="font-semibold">Sign In</div>
                <div className="text-slate-400 text-sm">Create an account or use demo credentials</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl">2️⃣</span>
              <div>
                <div className="font-semibold">Configure Applications</div>
                <div className="text-slate-400 text-sm">Add your AI applications and integrations</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl">3️⃣</span>
              <div>
                <div className="font-semibold">Monitor & Analyze</div>
                <div className="text-slate-400 text-sm">Track threats and get actionable insights</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-400">
          <p>&copy; 2024 Aiteebar AI Security. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
