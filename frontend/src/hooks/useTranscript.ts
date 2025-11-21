import { useState } from 'react'
import { transcriptApi } from '@/services/api'
import type { TranscriptResponse } from '@/types'

export const useTranscript = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<TranscriptResponse | null>(null)

  const fetchTranscript = async (videoUrl: string, clean: boolean) => {
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const result = await transcriptApi.fetchSingle(videoUrl, clean)
      setData(result)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch transcript'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, data, fetchTranscript }
}
