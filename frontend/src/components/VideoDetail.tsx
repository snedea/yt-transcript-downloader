'use client'

import { useEffect } from 'react'
import { useTranscript } from '@/hooks/useTranscript'
import TranscriptDisplay from './TranscriptDisplay'
import ErrorMessage from './ErrorMessage'

interface VideoDetailProps {
  videoId: string
  onBack: () => void
}

export default function VideoDetail({ videoId, onBack }: VideoDetailProps) {
  const { loading, error, data, loadFromCache } = useTranscript()

  useEffect(() => {
    loadFromCache(videoId)
  }, [videoId, loadFromCache])

  return (
    <div className="h-full overflow-auto">
      <div className="container mx-auto px-4 py-6">
        {/* Back button */}
        <button
          onClick={onBack}
          className="mb-4 inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Library
        </button>

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        )}

        {/* Error state */}
        {error && <ErrorMessage message={error} />}

        {/* Video details */}
        {data && (
          <div className="max-w-4xl mx-auto">
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
              cachedManipulation={data.cachedManipulation}
              manipulationDate={data.manipulationDate}
              cachedSummary={data.cachedSummary}
              summaryDate={data.summaryDate}
            />
          </div>
        )}
      </div>
    </div>
  )
}
