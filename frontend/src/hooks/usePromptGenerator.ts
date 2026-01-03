'use client'

import { useState, useCallback } from 'react'
import { promptGeneratorApi } from '@/services/api'
import type {
  PromptGeneratorResult,
  PromptCategory
} from '@/types'

interface PromptGeneratorProgress {
  phase: 'preparing' | 'generating' | 'complete'
  phase_name: string
  progress: number
  message: string
}

const PHASE_INFO: Record<string, { name: string; progress: number }> = {
  preparing: { name: 'Preparing content...', progress: 20 },
  generating: { name: 'Generating prompts...', progress: 60 },
  complete: { name: 'Complete', progress: 100 }
}

interface UsePromptGeneratorOptions {
  videoId?: string
  includeDiscovery?: boolean
  includeSummary?: boolean
  includeManipulation?: boolean
  categories?: PromptCategory[]
  videoTitle?: string
  videoAuthor?: string
}

interface UsePromptGeneratorReturn {
  loading: boolean
  error: string | null
  result: PromptGeneratorResult | null
  isCached: boolean
  progress: PromptGeneratorProgress | null
  generateFromVideoId: (videoId: string, options?: UsePromptGeneratorOptions) => Promise<void>
  generateFromTranscript: (transcript: string, options?: UsePromptGeneratorOptions) => Promise<void>
  setFromCache: (result: PromptGeneratorResult) => void
  reset: () => void
}

export function usePromptGenerator(): UsePromptGeneratorReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PromptGeneratorResult | null>(null)
  const [isCached, setIsCached] = useState(false)
  const [progress, setProgress] = useState<PromptGeneratorProgress | null>(null)

  const generateFromVideoId = useCallback(async (
    videoId: string,
    options?: UsePromptGeneratorOptions
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    // Set initial progress
    setProgress({
      phase: 'preparing',
      phase_name: PHASE_INFO.preparing.name,
      progress: PHASE_INFO.preparing.progress,
      message: 'Loading transcript and analyses...'
    })

    try {
      // Simulate progress updates (generation takes ~30-60s)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev
          if (prev.phase === 'preparing') {
            return {
              phase: 'generating',
              phase_name: PHASE_INFO.generating.name,
              progress: PHASE_INFO.generating.progress,
              message: 'Generating 7 production-ready prompts...'
            }
          }
          return prev
        })
      }, 5000)

      const promptResult = await promptGeneratorApi.generatePrompts({
        videoId,
        includeDiscovery: options?.includeDiscovery ?? true,
        includeSummary: options?.includeSummary ?? true,
        includeManipulation: options?.includeManipulation ?? false,
        categories: options?.categories,
        videoTitle: options?.videoTitle,
        videoAuthor: options?.videoAuthor
      })

      clearInterval(progressInterval)

      // Set final progress
      setProgress({
        phase: 'complete',
        phase_name: PHASE_INFO.complete.name,
        progress: 100,
        message: `Generated ${promptResult.total_prompts} prompts!`
      })

      setResult(promptResult)

      // Save to cache
      try {
        await promptGeneratorApi.savePrompts(videoId, promptResult)
        console.log('[PromptGenerator] Saved to cache for video:', videoId)
      } catch (cacheErr) {
        console.error('[PromptGenerator] Failed to cache:', cacheErr)
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to generate prompts'

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

  const generateFromTranscript = useCallback(async (
    transcript: string,
    options?: UsePromptGeneratorOptions
  ) => {
    setLoading(true)
    setError(null)
    setIsCached(false)
    setResult(null)

    // Set initial progress
    setProgress({
      phase: 'generating',
      phase_name: PHASE_INFO.generating.name,
      progress: PHASE_INFO.generating.progress,
      message: 'Generating 7 production-ready prompts...'
    })

    try {
      const promptResult = await promptGeneratorApi.generatePrompts({
        transcript,
        includeDiscovery: options?.includeDiscovery ?? false,
        includeSummary: options?.includeSummary ?? false,
        includeManipulation: options?.includeManipulation ?? false,
        categories: options?.categories,
        videoTitle: options?.videoTitle,
        videoAuthor: options?.videoAuthor
      })

      // Set final progress
      setProgress({
        phase: 'complete',
        phase_name: PHASE_INFO.complete.name,
        progress: 100,
        message: `Generated ${promptResult.total_prompts} prompts!`
      })

      setResult(promptResult)

      // Save to cache if videoId provided
      if (options?.videoId) {
        try {
          await promptGeneratorApi.savePrompts(options.videoId, promptResult)
          console.log('[PromptGenerator] Saved to cache for video:', options.videoId)
        } catch (cacheErr) {
          console.error('[PromptGenerator] Failed to cache:', cacheErr)
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to generate prompts'

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

  const setFromCache = useCallback((cachedResult: PromptGeneratorResult) => {
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
    generateFromVideoId,
    generateFromTranscript,
    setFromCache,
    reset
  }
}

/**
 * Helper to estimate prompt generation duration
 */
export function usePromptGeneratorEstimate(wordCount: number): string {
  // Generation is generally ~45s base + scaling with content
  const baseSeconds = 40
  const perThousandWords = 15
  const estimatedSeconds = baseSeconds + Math.floor(wordCount / 1000) * perThousandWords

  if (estimatedSeconds < 60) {
    return `~${estimatedSeconds} seconds`
  } else {
    const minutes = Math.ceil(estimatedSeconds / 60)
    return `~${minutes} minute${minutes > 1 ? 's' : ''}`
  }
}

/**
 * Category metadata for UI display
 */
export const PROMPT_CATEGORY_INFO: Record<PromptCategory, {
  name: string
  icon: string
  color: string
  targetTool: string
  description: string
}> = {
  app_builder: {
    name: 'App Builder',
    icon: '🏗️',
    color: 'indigo',
    targetTool: 'Context Foundry autonomous_build_and_deploy',
    description: 'Build working applications inspired by video content'
  },
  research_deep_dive: {
    name: 'Research Deep-Dive',
    icon: '🔬',
    color: 'blue',
    targetTool: 'Claude, GPT-4, or research agents',
    description: 'Structured research exploration of video topics'
  },
  devils_advocate: {
    name: "Devil's Advocate",
    icon: '😈',
    color: 'red',
    targetTool: 'Claude or GPT-4',
    description: 'Challenge assumptions and explore opposing viewpoints'
  },
  mermaid_diagrams: {
    name: 'Mermaid Diagrams',
    icon: '📊',
    color: 'green',
    targetTool: 'Claude, GPT-4, or diagram generators',
    description: 'Create visual diagrams from video content'
  },
  sora: {
    name: 'Sora Video',
    icon: '🎬',
    color: 'purple',
    targetTool: 'OpenAI Sora',
    description: 'Generate videos inspired by content'
  },
  nano_banana_pro: {
    name: 'Nano Banana Pro',
    icon: '🎨',
    color: 'yellow',
    targetTool: 'Gemini 3 / Nano Banana Pro',
    description: 'Create infographics and visual summaries'
  },
  validation_frameworks: {
    name: 'Validation Frameworks',
    icon: '✅',
    color: 'teal',
    targetTool: 'Claude, GPT-4, or testing tools',
    description: 'Create testing and validation frameworks'
  }
}
