'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { isAuthenticated } from '@/lib/auth'
import { Navbar } from '@/components/Navbar'

export default function Home() {
  const router = useRouter()
  const authenticated = isAuthenticated()

  const handleLearnMore = () => {
    const element = document.getElementById('features-section')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Grid Pattern Background */}
      <div className="absolute inset-0 opacity-5 pointer-events-none"
        style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(79, 172, 254, .05) 25%, rgba(79, 172, 254, .05) 26%, transparent 27%, transparent 74%, rgba(79, 172, 254, .05) 75%, rgba(79, 172, 254, .05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(79, 172, 254, .05) 25%, rgba(79, 172, 254, .05) 26%, transparent 27%, transparent 74%, rgba(79, 172, 254, .05) 75%, rgba(79, 172, 254, .05) 76%, transparent 77%, transparent)',
          backgroundSize: '60px 60px',
        }}
      ></div>

      {/* Navigation */}
      <nav className="relative border-b border-blue-900/30 bg-slate-950/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-cyan-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">🔒</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">Aiteebar</h1>
            </div>
            <div className="flex gap-4">
              <Link
                href="/login"
                className="px-6 py-2 text-sm font-medium bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-lg transition-all shadow-lg hover:shadow-blue-500/50"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
        <div className="text-center">
          <div className="mb-6 inline-block">
            <span className="px-4 py-2 bg-blue-500/20 text-blue-300 rounded-full text-sm font-semibold border border-blue-500/30">
              🚀 Advanced AI Security Platform
            </span>
          </div>
          <h2 className="text-6xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent">
              AI-Powered Security Intelligence
            </span>
          </h2>
          <p className="text-xl text-slate-300 mb-10 max-w-3xl mx-auto leading-relaxed">
            Advanced threat detection, vulnerability assessment, and security analysis
            powered by artificial intelligence. Protect your AI infrastructure with intelligent
            risk management and real-time threat analysis.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/login"
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-lg font-semibold inline-block transition-all shadow-lg hover:shadow-blue-500/50"
            >
              Get Started →
            </Link>
            <button
              onClick={handleLearnMore}
              className="px-8 py-3 border-2 border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 rounded-lg font-semibold cursor-pointer transition-all hover:border-cyan-400"
            >
              Learn More ↓
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features-section" className="relative bg-gradient-to-b from-blue-950/40 to-slate-950/60 py-24 border-t border-blue-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-4xl font-bold mb-16 text-center">
            <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              Key Features
            </span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group relative bg-gradient-to-br from-blue-900/20 to-slate-900/20 p-8 rounded-xl border border-blue-500/20 hover:border-blue-500/50 transition-all duration-300 hover:bg-blue-900/30 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/5 group-hover:to-cyan-500/5 rounded-xl transition-all"></div>
              <div className="relative text-5xl mb-4">🔍</div>
              <h4 className="text-xl font-bold mb-3 text-blue-100">Threat Detection</h4>
              <p className="text-slate-300 leading-relaxed">
                Real-time threat detection and vulnerability scanning with AI-powered analysis.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group relative bg-gradient-to-br from-cyan-900/20 to-slate-900/20 p-8 rounded-xl border border-cyan-500/20 hover:border-cyan-500/50 transition-all duration-300 hover:bg-cyan-900/30 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 to-blue-500/0 group-hover:from-cyan-500/5 group-hover:to-blue-500/5 rounded-xl transition-all"></div>
              <div className="relative text-5xl mb-4">📊</div>
              <h4 className="text-xl font-bold mb-3 text-cyan-100">Intelligence Reports</h4>
              <p className="text-slate-300 leading-relaxed">
                Comprehensive threat intelligence dashboards with actionable insights.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group relative bg-gradient-to-br from-purple-900/20 to-slate-900/20 p-8 rounded-xl border border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 hover:bg-purple-900/30 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/5 group-hover:to-pink-500/5 rounded-xl transition-all"></div>
              <div className="relative text-5xl mb-4">🛡️</div>
              <h4 className="text-xl font-bold mb-3 text-purple-100">Risk Management</h4>
              <p className="text-slate-300 leading-relaxed">
                Advanced risk scoring and prioritization to focus on critical threats.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Status Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="bg-gradient-to-br from-blue-900/20 to-slate-900/30 p-10 rounded-2xl border border-blue-500/20 backdrop-blur-sm">
          <h3 className="text-3xl font-bold mb-8 text-blue-100">Getting Started</h3>
          <div className="space-y-5">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center flex-shrink-0 font-bold text-white">1</div>
              <div className="pt-1">
                <div className="font-semibold text-lg text-blue-100">Sign In</div>
                <div className="text-slate-400">Create an account or use demo credentials (admin@aiteebar.ai / admin123)</div>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0 font-bold text-white">2</div>
              <div className="pt-1">
                <div className="font-semibold text-lg text-cyan-100">View Dashboard</div>
                <div className="text-slate-400">Access comprehensive security insights and real-time metrics</div>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center flex-shrink-0 font-bold text-white">3</div>
              <div className="pt-1">
                <div className="font-semibold text-lg text-purple-100">Monitor & Protect</div>
                <div className="text-slate-400">Track threats, analyze risks, and secure your AI infrastructure</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-blue-900/30 bg-slate-950/40 backdrop-blur-sm py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="font-bold text-blue-300 mb-4">About Aiteebar</h4>
              <p className="text-slate-400 text-sm">Advanced AI security intelligence platform protecting your infrastructure.</p>
            </div>
            <div>
              <h4 className="font-bold text-blue-300 mb-4">Features</h4>
              <ul className="text-slate-400 text-sm space-y-2">
                <li>🔍 Threat Detection</li>
                <li>📊 Intelligence Reports</li>
                <li>🛡️ Risk Management</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-blue-300 mb-4">Security</h4>
              <p className="text-slate-400 text-sm">Enterprise-grade security with AI-powered threat analysis.</p>
            </div>
          </div>
          <div className="border-t border-blue-900/30 pt-8 text-center text-slate-400">
            <p>&copy; 2024 Aiteebar AI Security. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
