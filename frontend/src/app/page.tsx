'use client'

import { useState, useEffect, useRef } from 'react'
import SingleDownload from '@/components/SingleDownload'
import BulkDownload from '@/components/BulkDownload'
import TranscriptHistory from '@/components/TranscriptHistory'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single')
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [historyOpen, setHistoryOpen] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  const handleHistorySelect = (videoId: string) => {
    setSelectedVideoId(videoId)
    setHistoryOpen(false)
  }

  const handleTranscriptFetched = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  // Reset selection when user fetches a new transcript
  const handleNewTranscript = () => {
    setSelectedVideoId(null)
    handleTranscriptFetched()
  }

  // Close panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setHistoryOpen(false)
      }
    }

    if (historyOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [historyOpen])

  // Close on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setHistoryOpen(false)
      }
    }

    if (historyOpen) {
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [historyOpen])

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8 relative">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            YouTube Content Analyzer
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Download transcripts, analyze rhetoric, and detect manipulation in video content
          </p>

          {/* History Button - Top Right */}
          <button
            onClick={() => setHistoryOpen(true)}
            className="absolute right-0 top-0 flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg shadow-md transition-colors"
            title="View transcript history"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="hidden sm:inline">History</span>
          </button>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {/* Tabs */}
          <div className="flex justify-center mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-1 inline-flex">
              <button
                onClick={() => setActiveTab('single')}
                className={`px-6 py-2 rounded-md font-medium transition-colors ${
                  activeTab === 'single'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Single Video
              </button>
              <button
                onClick={() => setActiveTab('bulk')}
                className={`px-6 py-2 rounded-md font-medium transition-colors ${
                  activeTab === 'bulk'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Bulk Download
              </button>
            </div>
          </div>

          {/* Content */}
          {activeTab === 'single' ? (
            <SingleDownload
              selectedVideoId={selectedVideoId}
              onTranscriptFetched={handleNewTranscript}
            />
          ) : (
            <BulkDownload />
          )}
        </div>
      </div>

      {/* Slide-out History Panel */}
      {historyOpen && (
        <div className="fixed inset-0 z-50">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/30" />

          {/* Panel */}
          <div
            ref={panelRef}
            className="absolute right-0 top-0 h-full w-80 max-w-[85vw] bg-white dark:bg-gray-800 shadow-2xl transform transition-transform duration-200 ease-out"
          >
            {/* Panel Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recent Transcripts
              </h2>
              <button
                onClick={() => setHistoryOpen(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Close"
              >
                <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Panel Content */}
            <div className="overflow-y-auto h-[calc(100%-65px)]">
              <TranscriptHistory
                onSelect={handleHistorySelect}
                refreshTrigger={refreshTrigger}
              />
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
