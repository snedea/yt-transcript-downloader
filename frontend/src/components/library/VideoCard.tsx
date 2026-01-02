'use client'

import React from 'react'
import type { LibraryItem } from '@/services/api'
import type { ContentType } from '@/types'

interface VideoCardProps {
  item: LibraryItem
  onClick: () => void
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

export function VideoCard({ item, onClick }: VideoCardProps) {
  const thumbnail = `https://img.youtube.com/vi/${item.video_id}/mqdefault.jpg`
  const contentType = (item.content_type as ContentType) || 'other'
  const contentTypeInfo = CONTENT_TYPE_INFO[contentType] || CONTENT_TYPE_INFO.other

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
        />

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
        <h3 className="font-medium text-gray-900 dark:text-white line-clamp-2 text-sm leading-snug">
          {item.video_title}
        </h3>

        {item.author && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
            {item.author}
          </p>
        )}

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

export default VideoCard
