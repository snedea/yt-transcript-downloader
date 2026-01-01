'use client'

import { useState, useCallback } from 'react'
import { analysisApi, cacheApi } from '@/services/api'
import type { ContentSummaryResult, TranscriptSegment } from '@/types'

interface UseContentSummaryOptions {
  videoTitle?: string
  videoAuthor?: string
  videoId?: string
  videoUrl?: string
}

interface UseContentSummaryReturn {
  loading: boolean
  error: string | null
  result: ContentSummaryResult | null
  isCached: boolean
  analyzeTranscript: (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: UseContentSummaryOptions
  ) => Promise<void>
  setFromCache: (result: ContentSummaryResult) => void
  reset: () => void
}

/**
 * React hook for content summary analysis.
 *
 * Provides a fast (~10s) analysis that extracts:
 * - Content type detection
 * - TLDR summary
 * - Key concepts with explanations
 * - Technical details (for programming content)
 * - Action items and takeaways
 * - Keywords/tags for Obsidian
 * - Key moments with timestamps
 */
export function useContentSummary(): UseContentSummaryReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ContentSummaryResult | null>(null)
  const [isCached, setIsCached] = useState(false)

  const analyzeTranscript = useCallback(async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: UseContentSummaryOptions
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    try {
      const summaryResult = await analysisApi.analyzeSummary(
        transcript,
        transcriptData,
        options
      )
      setResult(summaryResult)

      // Save to cache if videoId is provided
      if (options?.videoId) {
        try {
          await cacheApi.saveSummary(options.videoId, summaryResult)
        } catch (cacheErr) {
          console.warn('Failed to cache summary:', cacheErr)
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to analyze content'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  const setFromCache = useCallback((cachedResult: ContentSummaryResult) => {
    setResult(cachedResult)
    setIsCached(true)
    setError(null)
    setLoading(false)
  }, [])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
    setResult(null)
    setIsCached(false)
  }, [])

  return {
    loading,
    error,
    result,
    isCached,
    analyzeTranscript,
    setFromCache,
    reset
  }
}
