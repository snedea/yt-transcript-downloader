import { useState } from 'react'
import { playlistApi, transcriptApi } from '@/services/api'
import type { Video, BulkResult } from '@/types'

export const useBulkDownload = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [videos, setVideos] = useState<Video[]>([])
  const [transcripts, setTranscripts] = useState<BulkResult | null>(null)
  const [progress, setProgress] = useState({ current: 0, total: 0 })

  const fetchPlaylistVideos = async (playlistUrl: string) => {
    setLoading(true)
    setError(null)
    setVideos([])

    try {
      const result = await playlistApi.getVideos(playlistUrl)
      setVideos(result.videos)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch playlist videos'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const fetchBulkTranscripts = async (videoIds: string[], clean: boolean) => {
    setLoading(true)
    setError(null)
    setTranscripts(null)
    setProgress({ current: 0, total: videoIds.length })

    try {
      const result = await transcriptApi.fetchBulk(videoIds, clean)
      setTranscripts(result)
      setProgress({ current: videoIds.length, total: videoIds.length })
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch transcripts'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setVideos([])
    setTranscripts(null)
    setError(null)
    setProgress({ current: 0, total: 0 })
  }

  return {
    loading,
    error,
    videos,
    transcripts,
    progress,
    fetchPlaylistVideos,
    fetchBulkTranscripts,
    reset
  }
}
