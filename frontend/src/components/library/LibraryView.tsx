'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { cacheApi, LibraryItem, TagCount, SearchFilters } from '@/services/api'
import { SearchBar } from './SearchBar'
import { VideoCard } from './VideoCard'
import { UnifiedContentModal } from '@/components/content/UnifiedContentModal'
import type { ContentType } from '@/types'

interface LibraryViewProps {
  onVideoSelect: (videoId: string) => void
}

// Content type info for filter chips
const CONTENT_TYPES: { id: ContentType; label: string; icon: string }[] = [
  { id: 'programming_technical', label: 'Technical', icon: '💻' },
  { id: 'tutorial_howto', label: 'Tutorial', icon: '📝' },
  { id: 'educational', label: 'Educational', icon: '🎓' },
  { id: 'news_current_events', label: 'News', icon: '📰' },
  { id: 'entertainment', label: 'Entertainment', icon: '🎬' },
  { id: 'discussion_opinion', label: 'Discussion', icon: '💬' },
  { id: 'review', label: 'Review', icon: '⭐' },
  { id: 'interview', label: 'Interview', icon: '🎤' },
]

export function LibraryView({ onVideoSelect }: LibraryViewProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<LibraryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showContentModal, setShowContentModal] = useState(false)

  // Filters
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [hasSummary, setHasSummary] = useState<boolean | null>(null)
  const [hasAnalysis, setHasAnalysis] = useState<boolean | null>(null)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [orderBy, setOrderBy] = useState<'last_accessed' | 'created_at' | 'title'>('last_accessed')

  // Tag suggestions
  const [availableTags, setAvailableTags] = useState<TagCount[]>([])
  const [contentTypeCounts, setContentTypeCounts] = useState<Record<string, number>>({})

  // Debounce search
  const [debouncedQuery, setDebouncedQuery] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Fetch tags and content types on mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [tagsRes, typesRes] = await Promise.all([
          cacheApi.getTags(50),
          cacheApi.getContentTypes()
        ])
        setAvailableTags(tagsRes.tags)
        setContentTypeCounts(typesRes.content_types)
      } catch (err) {
        console.error('Failed to fetch metadata:', err)
      }
    }
    fetchMetadata()
  }, [])

  // Fetch results when filters change
  const fetchResults = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const filters: SearchFilters = {
        q: debouncedQuery || undefined,
        content_type: selectedTypes.length > 0 ? selectedTypes : undefined,
        has_summary: hasSummary ?? undefined,
        has_analysis: hasAnalysis ?? undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        order_by: orderBy,
        limit: 100
      }

      const response = await cacheApi.advancedSearch(filters)
      setResults(response.results)
    } catch (err: any) {
      setError(err.message || 'Failed to search')
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [debouncedQuery, selectedTypes, hasSummary, hasAnalysis, selectedTags, orderBy])

  useEffect(() => {
    fetchResults()
  }, [fetchResults])

  const toggleType = (type: string) => {
    setSelectedTypes(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    )
  }

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
  }

  const toggleBoolFilter = (current: boolean | null): boolean | null => {
    if (current === null) return true
    if (current === true) return false
    return null
  }

  const clearAllFilters = () => {
    setSearchQuery('')
    setSelectedTypes([])
    setHasSummary(null)
    setHasAnalysis(null)
    setSelectedTags([])
  }

  const hasActiveFilters = searchQuery || selectedTypes.length > 0 || hasSummary !== null || hasAnalysis !== null || selectedTags.length > 0

  const handleContentAdded = (contentId: string) => {
    // Refresh results after adding content
    fetchResults()
    // Navigate to the newly added content
    onVideoSelect(contentId)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
            />
          </div>
          <button
            onClick={() => setShowContentModal(true)}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            title="Add content"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span className="hidden sm:inline">Add</span>
          </button>
          <select
            value={orderBy}
            onChange={(e) => setOrderBy(e.target.value as typeof orderBy)}
            className="appearance-none px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-no-repeat bg-right"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
              backgroundPosition: 'right 0.5rem center',
              backgroundSize: '1.5em 1.5em'
            }}
          >
            <option value="last_accessed">Recent</option>
            <option value="created_at">Date Added</option>
            <option value="title">Title</option>
          </select>
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-2">
          {/* Content Type Filters */}
          {CONTENT_TYPES.filter(t => (contentTypeCounts[t.id] || 0) > 0).map(type => (
            <button
              key={type.id}
              onClick={() => toggleType(type.id)}
              className={`
                inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium
                transition-colors
                ${selectedTypes.includes(type.id)
                  ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-500'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }
              `}
            >
              <span>{type.icon}</span>
              <span>{type.label}</span>
              {contentTypeCounts[type.id] && (
                <span className="text-xs opacity-70">({contentTypeCounts[type.id]})</span>
              )}
            </button>
          ))}

          {/* Status Filters */}
          <button
            onClick={() => setHasSummary(toggleBoolFilter(hasSummary))}
            className={`
              inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium
              transition-colors
              ${hasSummary === true
                ? 'bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 ring-1 ring-emerald-500'
                : hasSummary === false
                ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 ring-1 ring-red-500'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
              }
            `}
          >
            {hasSummary === true ? '✓' : hasSummary === false ? '✗' : ''} Has Summary
          </button>

          <button
            onClick={() => setHasAnalysis(toggleBoolFilter(hasAnalysis))}
            className={`
              inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium
              transition-colors
              ${hasAnalysis === true
                ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-500'
                : hasAnalysis === false
                ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 ring-1 ring-red-500'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
              }
            `}
          >
            {hasAnalysis === true ? '✓' : hasAnalysis === false ? '✗' : ''} Analyzed
          </button>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Clear all
            </button>
          )}
        </div>

        {/* Tag Filters */}
        {availableTags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {availableTags.slice(0, 15).map(({ tag, count }) => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`
                  inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs
                  transition-colors
                  ${selectedTags.includes(tag)
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 ring-1 ring-blue-500'
                    : 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }
                `}
              >
                #{tag}
                <span className="opacity-50">({count})</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      <div className="flex-1 overflow-auto p-4 bg-gray-50 dark:bg-gray-900">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">
            <p>{error}</p>
            <button
              onClick={fetchResults}
              className="mt-2 text-indigo-600 hover:underline"
            >
              Try again
            </button>
          </div>
        ) : results.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p className="text-lg font-medium">No videos found</p>
            <p className="text-sm mt-1">
              {hasActiveFilters
                ? 'Try adjusting your filters or search query'
                : 'Add a new video to get started'
              }
            </p>
          </div>
        ) : (
          <>
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">
              {results.length} video{results.length !== 1 ? 's' : ''}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {results.map(item => (
                <VideoCard
                  key={item.video_id}
                  item={item}
                  onClick={() => onVideoSelect(item.video_id)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Unified Content Modal */}
      <UnifiedContentModal
        isOpen={showContentModal}
        onClose={() => setShowContentModal(false)}
        onContentAdded={handleContentAdded}
      />
    </div>
  )
}

export default LibraryView
