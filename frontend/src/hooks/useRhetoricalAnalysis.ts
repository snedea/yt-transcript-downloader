'use client'

import { useState, useCallback } from 'react'
import { analysisApi, cacheApi } from '@/services/api'
import type { AnalysisResult, TranscriptSegment } from '@/types'

interface UseRhetoricalAnalysisReturn {
  loading: boolean
  error: string | null
  result: AnalysisResult | null
  isCached: boolean
  analyzeTranscript: (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: {
      verifyQuotes?: boolean
      videoTitle?: string
      videoAuthor?: string
      videoId?: string  // For caching the result
    }
  ) => Promise<void>
  setFromCache: (result: AnalysisResult) => void
  reset: () => void
}

export function useRhetoricalAnalysis(): UseRhetoricalAnalysisReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [isCached, setIsCached] = useState(false)

  const analyzeTranscript = useCallback(async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: {
      verifyQuotes?: boolean
      videoTitle?: string
      videoAuthor?: string
      videoId?: string
    }
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)

    try {
      const analysisResult = await analysisApi.analyzeRhetoric(
        transcript,
        transcriptData,
        options
      )
      setResult(analysisResult)

      // Save to cache if videoId is provided
      if (options?.videoId) {
        try {
          await cacheApi.saveAnalysis(options.videoId, analysisResult)
          console.log('Analysis saved to cache for video:', options.videoId)
        } catch (cacheErr) {
          console.warn('Failed to cache analysis:', cacheErr)
          // Don't fail the whole operation if caching fails
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to analyze transcript'

      if (err.message === 'Network Error') {
        setError('Unable to connect to the server. Please check if the backend is running.')
      } else {
        setError(errorMessage)
      }
      setResult(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const setFromCache = useCallback((cachedResult: AnalysisResult) => {
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
