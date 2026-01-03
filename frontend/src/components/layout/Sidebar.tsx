'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { AccountSettings } from '@/components/AccountSettings'

type ViewType = 'library' | 'new' | 'detail' | 'discover' | 'health' | 'prompts'

interface SidebarProps {
  currentView: ViewType
  onViewChange: (view: 'library' | 'new' | 'discover' | 'health' | 'prompts') => void
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export function Sidebar({
  currentView,
  onViewChange,
  collapsed = false,
  onToggleCollapse
}: SidebarProps) {
  const { user, logout, isAuthenticated } = useAuth()
  const router = useRouter()
  const [isAccountSettingsOpen, setIsAccountSettingsOpen] = useState(false)

  // Removed old navigation items - now just use Faceteer header as home button
  // All content access happens through Library + ContentDetailHub

  const handleLoginClick = () => {
    router.push('/login')
  }

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
            💎 Faceteer
          </button>
        )}
        {collapsed && (
          <button
            onClick={() => onViewChange('library')}
            className="text-lg font-bold text-gray-900 dark:text-white mx-auto hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer select-none"
          >
            💎
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

      {/* Spacer - Navigation removed, content access via Library */}
      <div className="flex-1"></div>

      {/* User Account Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          {isAuthenticated ? (
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setIsAccountSettingsOpen(true)}
                className="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer w-full"
              >
                <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300 font-bold">
                  {user?.full_name ? user.full_name[0].toUpperCase() : user?.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {user?.full_name || 'User'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email}
                  </div>
                </div>
              </button>
              <button
                onClick={logout}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg
                    text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700
                    transition-colors text-sm"
              onClick={handleLoginClick}
            >
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </div>
              <div className="flex-1 text-left">
                <div className="font-medium text-gray-700 dark:text-gray-300">Guest</div>
                <div className="text-xs text-gray-500 dark:text-gray-500">Sign in</div>
              </div>
            </button>
          )}
        </div>
      )}
      {collapsed && (
        <div className="p-2 border-t border-gray-200 dark:border-gray-700">
          {isAuthenticated ? (
            <button
              className="w-full flex items-center justify-center p-2 rounded-lg
                  text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20
                  transition-colors"
              onClick={logout}
              title={`Sign out (${user?.email})`}
            >
              <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-300 text-sm font-bold">
                {user?.full_name ? user.full_name[0].toUpperCase() : user?.email[0].toUpperCase()}
              </div>
            </button>
          ) : (
            <button
              className="w-full flex items-center justify-center p-2 rounded-lg
                    text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700
                    transition-colors"
              onClick={handleLoginClick}
              title="Sign in"
            >
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </div>
            </button>
          )}
        </div>
      )}

      {/* Account Settings Modal */}
      <AccountSettings
        isOpen={isAccountSettingsOpen}
        onClose={() => setIsAccountSettingsOpen(false)}
      />
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

function PromptsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  )
}

export default Sidebar
