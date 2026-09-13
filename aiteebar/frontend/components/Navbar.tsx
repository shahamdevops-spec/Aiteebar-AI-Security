'use client'

import React, { useState } from 'react'
import Link from 'next/link'

interface NavbarProps {
  user?: {
    email: string
    name: string
    role: string
  }
  onLogout?: () => void
}

export function Navbar({ user, onLogout }: NavbarProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  return (
    <nav className="bg-slate-900 border-b border-slate-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="text-2xl font-bold text-blue-400">🔒</div>
            <span className="text-xl font-bold text-slate-100">Aiteebar</span>
          </Link>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="hidden sm:flex flex-col items-start">
                    <div className="text-sm font-medium text-slate-100">{user.name}</div>
                    <div className="text-xs text-slate-400">{user.role}</div>
                  </div>
                </button>

                {/* Profile dropdown */}
                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-lg">
                    <div className="px-4 py-3 border-b border-slate-700">
                      <div className="font-semibold text-slate-100">{user.name}</div>
                      <div className="text-sm text-slate-400">{user.email}</div>
                    </div>
                    <Link
                      href="/settings"
                      className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={onLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-slate-700 border-t border-slate-700"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
