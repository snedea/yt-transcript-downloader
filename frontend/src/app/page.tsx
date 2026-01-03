'use client'

import { useState, useEffect } from 'react'
import SingleDownload from '@/components/SingleDownload'
import BulkDownload from '@/components/BulkDownload'
import VideoDetail from '@/components/VideoDetail'
import { Sidebar } from '@/components/layout/Sidebar'
import { LibraryView } from '@/components/library/LibraryView'
import { DiscoveryView } from '@/components/discovery/DiscoveryView'
import { HealthView } from '@/components/health/HealthView'
import { PromptGeneratorView } from '@/components/prompts/PromptGeneratorView'

type ViewType = 'library' | 'new' | 'detail' | 'discover' | 'health' | 'prompts'
type NewVideoTab = 'single' | 'bulk'

const SIDEBAR_COLLAPSED_KEY = 'yt-analyzer-sidebar-collapsed'

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>('library')
  const [newVideoTab, setNewVideoTab] = useState<NewVideoTab>('single')
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null)
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

  const handleVideoSelect = (videoId: string) => {
    setSelectedVideoId(videoId)
    setCurrentView('detail') // Show video detail view
  }

  const handleBackToLibrary = () => {
    setSelectedVideoId(null)
    setCurrentView('library')
  }

  const handleTranscriptFetched = () => {
    // Reset selection after fetching new transcript
    setSelectedVideoId(null)
  }

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {currentView === 'library' ? (
          <LibraryView onVideoSelect={handleVideoSelect} />
        ) : currentView === 'detail' && selectedVideoId ? (
          <VideoDetail videoId={selectedVideoId} onBack={handleBackToLibrary} />
        ) : currentView === 'discover' ? (
          <DiscoveryView />
        ) : currentView === 'health' ? (
          <HealthView />
        ) : currentView === 'prompts' ? (
          <PromptGeneratorView />
        ) : (
          <div className="h-full overflow-auto">
            <div className="container mx-auto px-4 py-8">
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  Add New Video
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Download transcripts, analyze rhetoric, and detect manipulation
                </p>
              </div>

              {/* Tabs */}
              <div className="max-w-4xl mx-auto">
                <div className="flex justify-center mb-6">
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-1 inline-flex">
                    <button
                      onClick={() => setNewVideoTab('single')}
                      className={`px-6 py-2 rounded-md font-medium transition-colors ${
                        newVideoTab === 'single'
                          ? 'bg-blue-500 text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      Single Video
                    </button>
                    <button
                      onClick={() => setNewVideoTab('bulk')}
                      className={`px-6 py-2 rounded-md font-medium transition-colors ${
                        newVideoTab === 'bulk'
                          ? 'bg-blue-500 text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      Bulk Download
                    </button>
                  </div>
                </div>

                {/* Content */}
                {newVideoTab === 'single' ? (
                  <SingleDownload
                    selectedVideoId={null}
                    onTranscriptFetched={handleTranscriptFetched}
                  />
                ) : (
                  <BulkDownload />
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
