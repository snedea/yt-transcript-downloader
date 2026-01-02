'use client'

import React from 'react'

type ViewType = 'library' | 'new' | 'detail' | 'discover' | 'health'

interface SidebarProps {
  currentView: ViewType
  onViewChange: (view: 'library' | 'new' | 'discover' | 'health') => void
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export function Sidebar({
  currentView,
  onViewChange,
  collapsed = false,
  onToggleCollapse
}: SidebarProps) {

  const navItems = [
    { id: 'library' as const, label: 'Library', icon: LibraryIcon },
    { id: 'new' as const, label: 'New Video', icon: PlusIcon },
    { id: 'discover' as const, label: 'Discovery', icon: DiscoverIcon },
    { id: 'health' as const, label: 'Health', icon: HealthIcon },
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
          <button
            onClick={() => onViewChange('library')}
            className="text-lg font-bold text-gray-900 dark:text-white truncate hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer select-none"
          >
            YT Analyzer
          </button>
        )}
        {collapsed && (
          <button
            onClick={() => onViewChange('library')}
            className="text-lg font-bold text-gray-900 dark:text-white mx-auto hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer select-none"
          >
            YT
          </button>
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

      {/* User Account Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg
              text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700
              transition-colors text-sm"
            onClick={() => {
              // TODO: Implement login flow
              console.log('Login clicked')
            }}
          >
            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </div>
            <div className="flex-1 text-left">
              <div className="font-medium text-gray-700 dark:text-gray-300">Guest</div>
              <div className="text-xs text-gray-500 dark:text-gray-500">Sign in</div>
            </div>
          </button>
        </div>
      )}
      {collapsed && (
        <div className="p-2 border-t border-gray-200 dark:border-gray-700">
          <button
            className="w-full flex items-center justify-center p-2 rounded-lg
              text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700
              transition-colors"
            onClick={() => {
              // TODO: Implement login flow
              console.log('Login clicked')
            }}
            title="Sign in"
          >
            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </div>
          </button>
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

function DiscoverIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  )
}

function UserIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  )
}

function HealthIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  )
}

export default Sidebar
