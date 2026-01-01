'use client'

import { useState, useEffect, useMemo } from 'react'
import { cacheApi, CacheHistoryItem } from '@/services/api'

interface TranscriptHistoryProps {
  onSelect: (videoId: string) => void
  refreshTrigger?: number
}

const ITEMS_PER_PAGE = 10

export default function TranscriptHistory({ onSelect, refreshTrigger }: TranscriptHistoryProps) {
  const [history, setHistory] = useState<CacheHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await cacheApi.getHistory(100) // Fetch more for pagination
      setHistory(response.items)
    } catch (err: any) {
      setError('Failed to load history')
      console.error('Failed to fetch history:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [refreshTrigger])

  // Reset to page 1 when history changes
  useEffect(() => {
    setCurrentPage(1)
  }, [history.length])

  const handleDelete = async (e: React.MouseEvent, videoId: string) => {
    e.stopPropagation()
    try {
      await cacheApi.delete(videoId)
      setHistory(prev => prev.filter(item => item.video_id !== videoId))
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'America/Chicago',
      timeZoneName: 'short'
    })
  }

  // Pagination logic
  const totalPages = Math.ceil(history.length / ITEMS_PER_PAGE)
  const showPagination = history.length > ITEMS_PER_PAGE

  const paginatedHistory = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE
    return history.slice(start, start + ITEMS_PER_PAGE)
  }, [history, currentPage])

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  if (loading && history.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <div className="flex items-center gap-2 text-gray-500">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Loading history...
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return null // Don't show anything if no history
  }

  return (
    <div className="overflow-hidden">
      {/* Header with count and pagination */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {history.length} saved
        </span>

        {/* Pagination Controls */}
        {showPagination && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Previous page"
            >
              <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[80px] text-center">
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Next page"
            >
              <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* History List - Always visible */}
      <div>
        {paginatedHistory.map((item) => (
          <div
            key={item.video_id}
            onClick={() => onSelect(item.video_id)}
            className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
                {item.video_title}
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                {item.author && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {item.author}
                  </span>
                )}
                <span className="text-xs text-gray-400">
                  {formatDate(item.last_accessed)}
                </span>
                {item.is_cleaned && (
                  <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                    Cleaned
                  </span>
                )}
                {item.has_analysis && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">
                    Analyzed
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
