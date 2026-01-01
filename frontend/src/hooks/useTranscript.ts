import { useState, useCallback } from 'react'
import { transcriptApi, cacheApi } from '@/services/api'
import type { TranscriptResponse, AnalysisResult, ContentSummaryResult } from '@/types'

interface TranscriptData extends TranscriptResponse {
  cachedAnalysis?: AnalysisResult
  analysisDate?: string
  cachedSummary?: ContentSummaryResult
  summaryDate?: string
}

export const useTranscript = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<TranscriptData | null>(null)

  const fetchTranscript = useCallback(async (videoUrl: string, clean: boolean) => {
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const result = await transcriptApi.fetchSingle(videoUrl, clean)
      setData(result)
    } catch (err: any) {
      let errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch transcript'

      if (errorMessage === 'Network Error') {
        errorMessage = 'Unable to connect to server. Please ensure the backend is running properly.'
      }

      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadFromCache = useCallback(async (videoId: string) => {
    setLoading(true)
    setError(null)
    // Don't clear data immediately - prevents flickering

    try {
      const cached = await cacheApi.getTranscript(videoId)
      if (cached) {
        setData({
          transcript: cached.transcript,
          video_title: cached.video_title,
          video_id: cached.video_id,
          author: cached.author,
          upload_date: cached.upload_date,
          tokens_used: cached.tokens_used,
          transcript_data: cached.transcript_data,
          cached: true,
          cachedAnalysis: cached.analysis_result,
          analysisDate: cached.analysis_date,
          cachedSummary: cached.summary_result,
          summaryDate: cached.summary_date
        })
      } else {
        setData(null)
        setError('Transcript not found in cache')
      }
    } catch (err: any) {
      setData(null)
      setError(err.message || 'Failed to load from cache')
    } finally {
      setLoading(false)
    }
  }, [])

  const clearData = useCallback(() => {
    setData(null)
    setError(null)
  }, [])

  return { loading, error, data, fetchTranscript, loadFromCache, clearData }
}
