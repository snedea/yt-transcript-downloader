'use client'

import { useState } from 'react'
import SingleDownload from '@/components/SingleDownload'
import BulkDownload from '@/components/BulkDownload'
import TranscriptHistory from '@/components/TranscriptHistory'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single')
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleHistorySelect = (videoId: string) => {
    setSelectedVideoId(videoId)
  }

  const handleTranscriptFetched = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  // Reset selection when user fetches a new transcript
  const handleNewTranscript = () => {
    setSelectedVideoId(null)
    handleTranscriptFetched()
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            YouTube Transcript Downloader
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Download and clean YouTube video transcripts with AI-powered formatting
          </p>
        </div>

        {/* Main Layout: Sidebar + Content */}
        <div className="flex gap-6">
          {/* Left Sidebar - Recent Transcripts */}
          <aside className="w-72 flex-shrink-0 hidden lg:block">
            <div className="sticky top-4">
              <TranscriptHistory
                onSelect={handleHistorySelect}
                refreshTrigger={refreshTrigger}
              />
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
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
            <div className="max-w-4xl mx-auto">
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

          {/* Mobile: Show history below on small screens */}
          <div className="lg:hidden fixed bottom-4 right-4">
            <MobileHistoryButton onSelect={handleHistorySelect} refreshTrigger={refreshTrigger} />
          </div>
        </div>
      </div>
    </main>
  )
}

// Mobile floating button for history
function MobileHistoryButton({ onSelect, refreshTrigger }: { onSelect: (id: string) => void, refreshTrigger: number }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg"
        title="Recent Transcripts"
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-t-xl w-full max-w-lg max-h-[70vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-medium text-gray-900 dark:text-white">Recent Transcripts</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto max-h-[60vh]">
              <TranscriptHistory
                onSelect={(id) => { onSelect(id); setIsOpen(false); }}
                refreshTrigger={refreshTrigger}
              />
            </div>
          </div>
        </div>
      )}
    </>
  )
}
