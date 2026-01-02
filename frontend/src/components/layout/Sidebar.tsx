'use client'

import React, { useState, useEffect } from 'react'
import { cacheApi, LibraryStats } from '@/services/api'

type ViewType = 'library' | 'new' | 'detail'

interface SidebarProps {
  currentView: ViewType
  onViewChange: (view: 'library' | 'new') => void  // Only allow switching to library or new
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export function Sidebar({
  currentView,
  onViewChange,
  collapsed = false,
  onToggleCollapse
}: SidebarProps) {
  const [stats, setStats] = useState<LibraryStats>({ total: 0, with_summary: 0, with_analysis: 0 })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await cacheApi.getLibraryStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }
    fetchStats()
  }, [])

  const navItems = [
    { id: 'library' as const, label: 'Library', icon: LibraryIcon },
    { id: 'new' as const, label: 'New Video', icon: PlusIcon },
  ]

  return (
    <aside
      className={`
        ${collapsed ? 'w-16' : 'w-64'}
        bg-white dark:bg-gray-800
        border-r border-gray-200 dark:border-gray-700
        flex flex-col
        transition-all duration-200
        h-full
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        {!collapsed && (
          <h1 className="text-lg font-bold text-gray-900 dark:text-white truncate">
            YT Analyzer
          </h1>
        )}
        {collapsed && (
          <span className="text-lg font-bold text-gray-900 dark:text-white mx-auto">
            YT
          </span>
        )}
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {collapsed ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              )}
            </svg>
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={`
              w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
              transition-colors text-left
              ${(currentView === item.id || (item.id === 'library' && currentView === 'detail'))
                ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }
            `}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Stats Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <div className="flex justify-between">
              <span>Videos</span>
              <span className="font-medium text-gray-700 dark:text-gray-300">{stats.total}</span>
            </div>
            <div className="flex justify-between">
              <span>Summarized</span>
              <span className="font-medium text-emerald-600 dark:text-emerald-400">{stats.with_summary}</span>
            </div>
            <div className="flex justify-between">
              <span>Analyzed</span>
              <span className="font-medium text-indigo-600 dark:text-indigo-400">{stats.with_analysis}</span>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}

// Icons
function LibraryIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  )
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  )
}

export default Sidebar
