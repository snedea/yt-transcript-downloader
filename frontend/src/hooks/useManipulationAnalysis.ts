'use client'

import { useState, useCallback } from 'react'
import { analysisApi, cacheApi } from '@/services/api'
import type {
  ManipulationAnalysisResult,
  TranscriptSegment,
  AnalysisMode,
  AnalysisProgress
} from '@/types'

// Phase information for progress display
const PHASE_INFO: Record<string, { name: string; progress: number }> = {
  initializing: { name: 'Initializing...', progress: 0 },
  claim_extraction: { name: 'Extracting claims...', progress: 20 },
  manipulation_scan: { name: 'Scanning for manipulation techniques...', progress: 40 },
  dimension_scoring: { name: 'Scoring dimensions...', progress: 60 },
  claim_verification: { name: 'Verifying claims...', progress: 80 },
  synthesis: { name: 'Synthesizing results...', progress: 90 },
  complete: { name: 'Complete', progress: 100 }
}

interface UseManipulationAnalysisOptions {
  mode?: AnalysisMode
  verifyClaims?: boolean
  includeSegments?: boolean
  videoTitle?: string
  videoAuthor?: string
  videoId?: string  // For caching the result
}

interface UseManipulationAnalysisReturn {
  loading: boolean
  error: string | null
  result: ManipulationAnalysisResult | null
  isCached: boolean
  progress: AnalysisProgress | null
  mode: AnalysisMode
  setMode: (mode: AnalysisMode) => void
  analyzeTranscript: (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: UseManipulationAnalysisOptions
  ) => Promise<void>
  setFromCache: (result: ManipulationAnalysisResult) => void
  reset: () => void
}

export function useManipulationAnalysis(): UseManipulationAnalysisReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ManipulationAnalysisResult | null>(null)
  const [isCached, setIsCached] = useState(false)
  const [mode, setMode] = useState<AnalysisMode>('quick')
  const [progress, setProgress] = useState<AnalysisProgress | null>(null)

  const analyzeTranscript = useCallback(async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: UseManipulationAnalysisOptions
  ) => {
    const analysisMode = options?.mode ?? mode
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    // Set initial progress
    if (analysisMode === 'deep') {
      setProgress({
        phase: 'claim_extraction',
        phase_name: PHASE_INFO.initializing.name,
        progress: PHASE_INFO.initializing.progress,
        message: 'Starting deep analysis...'
      })
    } else {
      setProgress({
        phase: 'synthesis',
        phase_name: 'Analyzing...',
        progress: 50,
        message: 'Running quick analysis...'
      })
    }

    try {
      // Simulate progress updates for deep mode
      // In a real implementation, this could use SSE or WebSocket for real-time updates
      let progressInterval: NodeJS.Timeout | null = null

      if (analysisMode === 'deep') {
        const phases = ['claim_extraction', 'manipulation_scan', 'dimension_scoring', 'claim_verification', 'synthesis'] as const
        let currentPhaseIndex = 0

        progressInterval = setInterval(() => {
          if (currentPhaseIndex < phases.length) {
            const phase = phases[currentPhaseIndex]
            const phaseInfo = PHASE_INFO[phase]
            setProgress({
              phase,
              phase_name: phaseInfo.name,
              progress: phaseInfo.progress,
              message: `Phase ${currentPhaseIndex + 1} of ${phases.length}`
            })
            currentPhaseIndex++
          }
        }, 10000) // Update every 10 seconds for deep mode
      }

      const analysisResult = await analysisApi.analyzeManipulation(
        transcript,
        transcriptData,
        {
          mode: analysisMode,
          verifyClaims: options?.verifyClaims ?? (analysisMode === 'deep'),
          includeSegments: options?.includeSegments ?? true,
          videoTitle: options?.videoTitle,
          videoAuthor: options?.videoAuthor
        }
      )

      // Clear progress interval
      if (progressInterval) {
        clearInterval(progressInterval)
      }

      // Set final progress
      setProgress({
        phase: 'synthesis',
        phase_name: PHASE_INFO.complete.name,
        progress: 100,
        message: 'Analysis complete!'
      })

      setResult(analysisResult)

      // Save to cache if videoId is provided
      // Uses separate manipulation_result column to coexist with rhetorical analysis
      console.log('[ManipulationAnalysis] Checking save conditions:', {
        hasVideoId: !!options?.videoId,
        videoId: options?.videoId,
        hasResult: !!analysisResult,
        resultKeys: analysisResult ? Object.keys(analysisResult) : []
      })

      if (options?.videoId) {
        console.log('[ManipulationAnalysis] Attempting to save to cache...')
        try {
          await cacheApi.saveManipulation(options.videoId, analysisResult)
          console.log('[ManipulationAnalysis] ✅ Successfully saved to cache for video:', options.videoId)
        } catch (cacheErr) {
          console.error('[ManipulationAnalysis] ❌ Failed to cache manipulation analysis:', cacheErr)
        }
      } else {
        console.warn('[ManipulationAnalysis] ⚠️ No videoId provided, skipping cache save')
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
      setProgress(null)
    } finally {
      setLoading(false)
    }
  }, [mode])

  const setFromCache = useCallback((cachedResult: ManipulationAnalysisResult) => {
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
    mode,
    setMode,
    analyzeTranscript,
    setFromCache,
    reset
  }
}

/**
 * Helper hook to get estimated duration for an analysis mode
 */
export function useAnalysisEstimate(mode: AnalysisMode, wordCount: number): string {
  if (mode === 'quick') {
    return '~15 seconds'
  }

  // Deep mode scales with content length
  const baseSeconds = 45
  const perThousandWords = 15
  const estimatedSeconds = baseSeconds + Math.floor(wordCount / 1000) * perThousandWords

  if (estimatedSeconds < 60) {
    return `~${estimatedSeconds} seconds`
  } else {
    const minutes = Math.ceil(estimatedSeconds / 60)
    return `~${minutes} minute${minutes > 1 ? 's' : ''}`
  }
}
