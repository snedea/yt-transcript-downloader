'use client'

import { useState } from 'react'
import type { Video } from '@/types'

interface VideoSelectorProps {
  videos: Video[]
  onSelect: (selectedIds: string[]) => void
}

export default function VideoSelector({ videos, onSelect }: VideoSelectorProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const toggleVideo = (videoId: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(videoId)) {
      newSelected.delete(videoId)
    } else {
      newSelected.add(videoId)
    }
    setSelectedIds(newSelected)
    onSelect(Array.from(newSelected))
  }

  const selectAll = () => {
    const allIds = new Set(videos.map(v => v.id))
    setSelectedIds(allIds)
    onSelect(Array.from(allIds))
  }

  const deselectAll = () => {
    setSelectedIds(new Set())
    onSelect([])
  }

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Select Videos ({selectedIds.size} selected)
        </h3>
        <div className="flex gap-2">
          <button
            onClick={selectAll}
            className="text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-1 px-3 rounded"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            className="text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-1 px-3 rounded"
          >
            Deselect All
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
        {videos.map((video) => (
          <div
            key={video.id}
            onClick={() => toggleVideo(video.id)}
            className={`cursor-pointer border-2 rounded-lg overflow-hidden transition-all ${
              selectedIds.has(video.id)
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="relative">
              {video.thumbnail && (
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-full h-32 object-cover"
                />
              )}
              <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                {formatDuration(video.duration)}
              </div>
              <div className="absolute top-2 left-2">
                <input
                  type="checkbox"
                  checked={selectedIds.has(video.id)}
                  onChange={() => {}}
                  className="w-5 h-5"
                />
              </div>
            </div>
            <div className="p-3">
              <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                {video.title}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
