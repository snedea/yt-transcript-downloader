'use client'

import React from 'react'
import type { LibraryItem } from '@/services/api'
import type { ContentType } from '@/types'

interface ContentCardProps {
  item: LibraryItem
  onClick: () => void
  onDelete?: (videoId: string) => void
}

// Content type display info
const CONTENT_TYPE_INFO: Record<ContentType, { label: string; icon: string; color: string }> = {
  programming_technical: { label: 'Technical', icon: '💻', color: 'bg-blue-500' },
  tutorial_howto: { label: 'Tutorial', icon: '📝', color: 'bg-green-500' },
  news_current_events: { label: 'News', icon: '📰', color: 'bg-red-500' },
  educational: { label: 'Educational', icon: '🎓', color: 'bg-purple-500' },
  entertainment: { label: 'Entertainment', icon: '🎬', color: 'bg-pink-500' },
  discussion_opinion: { label: 'Discussion', icon: '💬', color: 'bg-yellow-500' },
  review: { label: 'Review', icon: '⭐', color: 'bg-orange-500' },
  interview: { label: 'Interview', icon: '🎤', color: 'bg-indigo-500' },
  other: { label: 'Other', icon: '📄', color: 'bg-gray-500' }
}

export function ContentCard({ item, onClick, onDelete }: ContentCardProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card click
    if (onDelete) {
      onDelete(item.video_id)
    }
  }
  // Dynamic thumbnail based on source type
  const thumbnail = item.source_type === 'youtube'
    ? `https://img.youtube.com/vi/${item.video_id}/mqdefault.jpg`
    : item.thumbnail_url || '/placeholder-pdf.jpg'

  const contentType = (item.content_type as ContentType) || 'other'
  const contentTypeInfo = CONTENT_TYPE_INFO[contentType] || CONTENT_TYPE_INFO.other

  // Source type display
  const sourceTypeLabel = {
    youtube: '▶️ Video',
    pdf: '📄 PDF',
    web_url: '🌐 Web',
    plain_text: '📝 Text'
  }[item.source_type || 'youtube']

  return (
    <div
      onClick={onClick}
      className="
        bg-white dark:bg-gray-800
        rounded-lg shadow
        hover:shadow-md
        transition-shadow
        cursor-pointer
        overflow-hidden
        border border-gray-200 dark:border-gray-700
      "
    >
      {/* Thumbnail */}
      <div className="relative aspect-video bg-gray-100 dark:bg-gray-700">
        <img
          src={thumbnail}
          alt={item.video_title}
          className="w-full h-full object-cover"
          loading="lazy"
          onError={(e) => {
            // Fallback if thumbnail fails to load
            e.currentTarget.src = '/placeholder-pdf.jpg'
          }}
        />

        {/* Source type badge - top left (for non-YouTube content) */}
        {item.source_type && item.source_type !== 'youtube' && (
          <span className="absolute top-2 left-2 bg-gray-800/80 text-white text-xs px-2 py-1 rounded font-medium">
            {sourceTypeLabel}
          </span>
        )}

        {/* Status badges - top right */}
        <div className="absolute top-2 right-2 flex gap-1">
          {item.has_summary && (
            <span className="bg-emerald-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Summary
            </span>
          )}
          {/* Show Trust badge if manipulation analysis exists */}
          {item.has_manipulation && (
            <span className="bg-indigo-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Trust
            </span>
          )}
          {/* Show Rhetoric badge if rhetorical analysis exists */}
          {item.has_rhetorical && (
            <span className="bg-purple-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Rhetoric
            </span>
          )}
          {/* Show Discovery badge if discovery analysis exists */}
          {item.has_discovery && (
            <span className="bg-amber-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Discovery
            </span>
          )}
          {/* Show Health badge if health observation exists */}
          {item.has_health && (
            <span className="bg-rose-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Health
            </span>
          )}
          {/* Show Prompts badge if prompts exist */}
          {item.has_prompts && (
            <span className="bg-violet-500 text-white text-xs px-1.5 py-0.5 rounded font-medium">
              Prompts
            </span>
          )}
        </div>

        {/* Content type badge - bottom left */}
        {item.content_type && (
          <span className={`absolute bottom-2 left-2 ${contentTypeInfo.color} text-white text-xs px-2 py-0.5 rounded flex items-center gap-1`}>
            <span>{contentTypeInfo.icon}</span>
            <span>{contentTypeInfo.label}</span>
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-medium text-gray-900 dark:text-white line-clamp-2 text-sm leading-snug flex-1">
            {item.video_title}
          </h3>
          {onDelete && (
            <button
              onClick={handleDelete}
              className="flex-shrink-0 p-1 text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-500 transition-colors"
              title="Delete this item"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>

        <div className="flex items-center justify-between gap-2 mt-1">
          {item.author && (
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {item.author}
            </p>
          )}

          {/* Show page count for PDFs, word count for other non-video sources */}
          {item.source_type === 'pdf' && item.page_count && (
            <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
              {item.page_count} {item.page_count === 1 ? 'page' : 'pages'}
            </span>
          )}
          {item.source_type && item.source_type !== 'youtube' && item.source_type !== 'pdf' && item.word_count && (
            <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
              {item.word_count.toLocaleString()} words
            </span>
          )}
        </div>

        {/* TLDR preview */}
        {item.tldr && (
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 line-clamp-2">
            {item.tldr}
          </p>
        )}

        {/* Tags */}
        {item.keywords && item.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {item.keywords.slice(0, 3).map(tag => (
              <span
                key={tag}
                className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-1.5 py-0.5 rounded"
              >
                #{tag}
              </span>
            ))}
            {item.keywords.length > 3 && (
              <span className="text-xs text-gray-400">+{item.keywords.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ContentCard
