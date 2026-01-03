'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { LibraryView } from '@/components/library/LibraryView'
import { ContentDetailHub } from '@/components/content/ContentDetailHub'

type ViewType = 'library' | 'detail'

const SIDEBAR_COLLAPSED_KEY = 'knowmler-sidebar-collapsed'

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>('library')
  const [selectedContentId, setSelectedContentId] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    // Initialize from localStorage (only on client)
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(SIDEBAR_COLLAPSED_KEY)
      return saved === 'true'
    }
    return false
  })

  // Persist sidebar state to localStorage
  useEffect(() => {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(sidebarCollapsed))
  }, [sidebarCollapsed])

  const handleContentSelect = (contentId: string) => {
    setSelectedContentId(contentId)
    setCurrentView('detail')
  }

  const handleBackToLibrary = () => {
    setSelectedContentId(null)
    setCurrentView('library')
  }

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={(view) => {
          if (view === 'library') {
            handleBackToLibrary()
          }
        }}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {currentView === 'library' ? (
          <LibraryView onVideoSelect={handleContentSelect} />
        ) : currentView === 'detail' && selectedContentId ? (
          <ContentDetailHub contentId={selectedContentId} onBack={handleBackToLibrary} />
        ) : null}
      </main>
    </div>
  )
}
