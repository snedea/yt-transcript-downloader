'use client'

import { useState } from 'react'
import SingleDownload from '@/components/SingleDownload'
import BulkDownload from '@/components/BulkDownload'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single')

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            YouTube Transcript Downloader
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Download and clean YouTube video transcripts with AI-powered formatting
          </p>
        </div>

        <div className="flex justify-center mb-8">
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

        <div className="max-w-4xl mx-auto">
          {activeTab === 'single' ? <SingleDownload /> : <BulkDownload />}
        </div>
      </div>
    </main>
  )
}
