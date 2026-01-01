'use client'

import { useState, useEffect } from 'react'
import { useTranscript } from '@/hooks/useTranscript'
import TranscriptDisplay from './TranscriptDisplay'
import ErrorMessage from './ErrorMessage'

interface SingleDownloadProps {
  selectedVideoId?: string | null
  onTranscriptFetched?: () => void
}

export default function SingleDownload({ selectedVideoId, onTranscriptFetched }: SingleDownloadProps) {
  const [videoUrl, setVideoUrl] = useState('')
  const [cleanTranscript, setCleanTranscript] = useState(false)
  const { loading, error, data, fetchTranscript, loadFromCache } = useTranscript()

  // Load from cache when selectedVideoId changes
  useEffect(() => {
    if (selectedVideoId) {
      loadFromCache(selectedVideoId)
    }
  }, [selectedVideoId, loadFromCache])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (videoUrl.trim()) {
      await fetchTranscript(videoUrl, cleanTranscript)
      onTranscriptFetched?.()
    }
  }

  const isValidUrl = (url: string) => {
    return url.includes('youtube.com') || url.includes('youtu.be')
  }

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="videoUrl"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              YouTube Video URL
            </label>
            <input
              type="text"
              id="videoUrl"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={cleanTranscript}
                onChange={(e) => setCleanTranscript(e.target.checked)}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Clean transcript with AI (GPT-4o-mini)
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !videoUrl.trim() || !isValidUrl(videoUrl)}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            {loading ? 'Fetching Transcript...' : 'Get Transcript'}
          </button>
        </form>
      </div>

      {error && <ErrorMessage message={error} />}

      {data && (
        <TranscriptDisplay
          transcript={data.transcript}
          videoTitle={data.video_title}
          videoId={data.video_id}
          author={data.author}
          uploadDate={data.upload_date}
          tokensUsed={data.tokens_used}
          transcriptData={data.transcript_data}
          cached={data.cached}
          cachedAnalysis={data.cachedAnalysis}
          analysisDate={data.analysisDate}
        />
      )}
    </div>
  )
}
