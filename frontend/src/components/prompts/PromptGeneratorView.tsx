'use client'

import React, { useState } from 'react'
import { ContentInput } from '@/components/content/ContentInput'
import { PromptGenerator, PromptGeneratorLoading, PromptGeneratorError } from '@/components/analysis/PromptGenerator'
import { contentApi, promptGeneratorApi, transcriptApi } from '@/services/api'
import type { PromptGeneratorResult, ContentSourceType } from '@/types'

// Helper to extract YouTube video ID from URL
function extractYouTubeVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)/,
    /^([a-zA-Z0-9_-]{11})$/ // Direct video ID
  ]
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  return null
}

interface PromptProgress {
  phase: 'uploading' | 'extracting' | 'generating' | 'complete'
  phase_name: string
  progress: number
  message: string
}

export function PromptGeneratorView() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PromptGeneratorResult | null>(null)
  const [progress, setProgress] = useState<PromptProgress | null>(null)
  const [contentTitle, setContentTitle] = useState<string>('')

  const handleGenerate = async (source: string, sourceType: ContentSourceType, file?: File) => {
    setIsGenerating(true)
    setError(null)
    setResult(null)

    try {
      let textContent: string
      let title: string
      let videoId: string | null = null
      let author: string | undefined

      if (file) {
        // Handle file upload
        setProgress({
          phase: 'uploading',
          phase_name: 'Uploading file...',
          progress: 10,
          message: `Uploading ${file.name}...`
        })

        const uploadResponse = await contentApi.upload(file)
        if (!uploadResponse.content) {
          throw new Error(uploadResponse.error || 'Failed to extract content from file')
        }
        textContent = uploadResponse.content.text
        title = uploadResponse.content.title || file.name
      } else if (sourceType === 'plain_text') {
        // Direct text input
        textContent = source
        title = 'Text Input'
      } else if (sourceType === 'youtube') {
        // YouTube URL - use transcript API to save to library
        videoId = extractYouTubeVideoId(source)
        if (!videoId) {
          throw new Error('Invalid YouTube URL')
        }

        setProgress({
          phase: 'extracting',
          phase_name: 'Fetching transcript...',
          progress: 20,
          message: 'Downloading YouTube transcript and saving to library...'
        })

        const transcriptResponse = await transcriptApi.fetchSingle(source, false)
        textContent = transcriptResponse.transcript
        title = transcriptResponse.video_title
        author = transcriptResponse.author
      } else {
        // Other URL extraction (non-YouTube)
        setProgress({
          phase: 'extracting',
          phase_name: 'Extracting content...',
          progress: 20,
          message: 'Fetching and extracting content from URL...'
        })

        const extractResponse = await contentApi.extract(source, { sourceType })
        textContent = extractResponse.text
        title = extractResponse.title
      }

      setContentTitle(title)

      // Now run prompt generation
      setProgress({
        phase: 'generating',
        phase_name: 'Generating 7 Production-Ready Prompts...',
        progress: 50,
        message: 'Creating prompts for App Builder, Research, Devil\'s Advocate, and more...'
      })

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev
          if (prev.phase === 'generating' && prev.progress < 90) {
            return { ...prev, progress: prev.progress + 5 }
          }
          return prev
        })
      }, 3000)

      const promptResult = await promptGeneratorApi.generatePrompts({
        transcript: textContent,
        videoTitle: title,
        videoAuthor: author,
        videoId: videoId || undefined,
        includeDiscovery: false,
        includeSummary: false
      })

      clearInterval(progressInterval)

      // Save prompts to cache if it's a YouTube video
      if (videoId) {
        try {
          await promptGeneratorApi.savePrompts(videoId, promptResult)
          console.log('[PromptGeneratorView] Saved prompts to cache for video:', videoId)
        } catch (cacheErr) {
          console.error('[PromptGeneratorView] Failed to cache prompts:', cacheErr)
        }
      }

      setProgress({
        phase: 'complete',
        phase_name: 'Complete',
        progress: 100,
        message: `Generated ${promptResult.total_prompts} prompts!`
      })

      setResult(promptResult)
    } catch (err: any) {
      console.error('Prompt generation error:', err)
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to generate prompts'
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRegenerate = async () => {
    // For now, just clear and let user re-submit
    setResult(null)
    setProgress(null)
  }

  return (
    <div className="h-full overflow-auto">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Prompt Generator
          </h1>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Generate 7 production-ready prompts for AI tools using Nate B Jones&apos;
            prompting techniques. Each prompt is 500-2000 words with explicit intent,
            disambiguation questions, and failure handling.
          </p>
        </div>

        {/* Category Preview */}
        {!result && !isGenerating && (
          <div className="mb-8 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 max-w-3xl mx-auto">
            {[
              { icon: '🏗️', name: 'App Builder', color: 'indigo' },
              { icon: '🔬', name: 'Research', color: 'blue' },
              { icon: '😈', name: "Devil's Advocate", color: 'red' },
              { icon: '📊', name: 'Mermaid', color: 'green' },
              { icon: '🎬', name: 'Sora', color: 'purple' },
              { icon: '🎨', name: 'Nano Banana', color: 'yellow' },
              { icon: '✅', name: 'Validation', color: 'teal' }
            ].map((cat) => (
              <div
                key={cat.name}
                className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
              >
                <span className="text-2xl">{cat.icon}</span>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{cat.name}</p>
              </div>
            ))}
          </div>
        )}

        {/* Show input or result */}
        {!result && !isGenerating && (
          <ContentInput
            onAnalyze={handleGenerate}
            isAnalyzing={isGenerating}
          />
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="flex-1">
                <h4 className="font-medium text-red-800 dark:text-red-200">Generation Failed</h4>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isGenerating && progress && (
          <div className="mt-6 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-lg p-8">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin mb-4" />
              <h4 className="font-medium text-violet-800 dark:text-violet-200 mb-2">
                {progress.phase_name}
              </h4>
              <div className="w-full max-w-md mb-4">
                <div className="h-2 bg-violet-100 dark:bg-violet-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-violet-500 transition-all duration-500"
                    style={{ width: `${progress.progress}%` }}
                  />
                </div>
              </div>
              <p className="text-sm text-violet-600 dark:text-violet-400 max-w-md">
                {progress.message}
              </p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 relative">
            <button
              onClick={() => {
                setResult(null)
                setProgress(null)
              }}
              className="absolute -top-2 -right-2 z-10 bg-white dark:bg-gray-800 rounded-full p-1 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Generate new prompts"
            >
              <svg className="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <PromptGenerator
              result={result}
              videoTitle={contentTitle}
              isCached={false}
              onRegenerate={handleRegenerate}
              isRegenerating={isGenerating}
            />
          </div>
        )}
      </div>
    </div>
  )
}
