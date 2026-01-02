'use client'

import { useState, useCallback } from 'react'
import { analysisApi, discoveryCacheApi } from '@/services/api'
import type {
  DiscoveryResult,
  ContentSourceType
} from '@/types'

interface DiscoveryProgress {
  phase: 'extracting' | 'analyzing' | 'generating' | 'complete'
  phase_name: string
  progress: number
  message: string
}

const PHASE_INFO: Record<string, { name: string; progress: number }> = {
  extracting: { name: 'Extracting content...', progress: 20 },
  analyzing: { name: 'Analyzing with Kinoshita Pattern...', progress: 50 },
  generating: { name: 'Generating cross-domain applications...', progress: 80 },
  complete: { name: 'Complete', progress: 100 }
}

interface UseDiscoveryOptions {
  focusDomains?: string[]
  maxApplications?: number
  videoId?: string  // For caching the result
}

interface UseDiscoveryReturn {
  loading: boolean
  error: string | null
  result: DiscoveryResult | null
  isCached: boolean
  progress: DiscoveryProgress | null
  analyzeFromVideoId: (videoId: string, options?: UseDiscoveryOptions) => Promise<void>
  analyzeFromSource: (source: string, sourceType?: ContentSourceType, options?: UseDiscoveryOptions) => Promise<void>
  setFromCache: (result: DiscoveryResult) => void
  reset: () => void
}

export function useDiscovery(): UseDiscoveryReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DiscoveryResult | null>(null)
  const [isCached, setIsCached] = useState(false)
  const [progress, setProgress] = useState<DiscoveryProgress | null>(null)

  const analyzeFromVideoId = useCallback(async (
    videoId: string,
    options?: UseDiscoveryOptions
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    // Set initial progress
    setProgress({
      phase: 'analyzing',
      phase_name: PHASE_INFO.analyzing.name,
      progress: PHASE_INFO.analyzing.progress,
      message: 'Analyzing cached transcript...'
    })

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev
          if (prev.phase === 'analyzing') {
            return {
              phase: 'generating',
              phase_name: PHASE_INFO.generating.name,
              progress: PHASE_INFO.generating.progress,
              message: 'Generating cross-domain insights...'
            }
          }
          return prev
        })
      }, 10000)

      const discoveryResult = await analysisApi.analyzeDiscovery({
        videoId,
        focusDomains: options?.focusDomains,
        maxApplications: options?.maxApplications
      })

      clearInterval(progressInterval)

      // Set final progress
      setProgress({
        phase: 'complete',
        phase_name: PHASE_INFO.complete.name,
        progress: 100,
        message: 'Discovery analysis complete!'
      })

      setResult(discoveryResult)

      // Save to cache
      try {
        await discoveryCacheApi.saveDiscovery(videoId, discoveryResult)
        console.log('[Discovery] Saved to cache for video:', videoId)
      } catch (cacheErr) {
        console.error('[Discovery] Failed to cache:', cacheErr)
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to perform discovery analysis'

      if (err.message === 'Network Error') {
        setError('Unable to connect to the server. Please check if the backend is running.')
      } else {
        setError(errorMessage)
      }
      setResult(null)
      setProgress(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const analyzeFromSource = useCallback(async (
    source: string,
    sourceType?: ContentSourceType,
    options?: UseDiscoveryOptions
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    // Set initial progress
    setProgress({
      phase: 'extracting',
      phase_name: PHASE_INFO.extracting.name,
      progress: PHASE_INFO.extracting.progress,
      message: 'Extracting content from source...'
    })

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev
          if (prev.phase === 'extracting') {
            return {
              phase: 'analyzing',
              phase_name: PHASE_INFO.analyzing.name,
              progress: PHASE_INFO.analyzing.progress,
              message: 'Analyzing with Kinoshita Pattern...'
            }
          }
          if (prev.phase === 'analyzing') {
            return {
              phase: 'generating',
              phase_name: PHASE_INFO.generating.name,
              progress: PHASE_INFO.generating.progress,
              message: 'Generating cross-domain insights...'
            }
          }
          return prev
        })
      }, 8000)

      const discoveryResult = await analysisApi.analyzeDiscovery({
        source,
        sourceType,
        focusDomains: options?.focusDomains,
        maxApplications: options?.maxApplications
      })

      clearInterval(progressInterval)

      // Set final progress
      setProgress({
        phase: 'complete',
        phase_name: PHASE_INFO.complete.name,
        progress: 100,
        message: 'Discovery analysis complete!'
      })

      setResult(discoveryResult)

      // Save to cache if videoId provided (for YouTube sources)
      if (options?.videoId) {
        try {
          await discoveryCacheApi.saveDiscovery(options.videoId, discoveryResult)
          console.log('[Discovery] Saved to cache for video:', options.videoId)
        } catch (cacheErr) {
          console.error('[Discovery] Failed to cache:', cacheErr)
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to perform discovery analysis'

      if (err.message === 'Network Error') {
        setError('Unable to connect to the server. Please check if the backend is running.')
      } else {
        setError(errorMessage)
      }
      setResult(null)
      setProgress(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const setFromCache = useCallback((cachedResult: DiscoveryResult) => {
    setResult(cachedResult)
    setIsCached(true)
    setError(null)
    setLoading(false)
    setProgress(null)
  }, [])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
    setResult(null)
    setIsCached(false)
    setProgress(null)
  }, [])

  return {
    loading,
    error,
    result,
    isCached,
    progress,
    analyzeFromVideoId,
    analyzeFromSource,
    setFromCache,
    reset
  }
}

/**
 * Helper to estimate discovery analysis duration
 */
export function useDiscoveryEstimate(wordCount: number): string {
  // Discovery is generally ~30s base + scaling with content
  const baseSeconds = 25
  const perThousandWords = 10
  const estimatedSeconds = baseSeconds + Math.floor(wordCount / 1000) * perThousandWords

  if (estimatedSeconds < 60) {
    return `~${estimatedSeconds} seconds`
  } else {
    const minutes = Math.ceil(estimatedSeconds / 60)
    return `~${minutes} minute${minutes > 1 ? 's' : ''}`
  }
}
