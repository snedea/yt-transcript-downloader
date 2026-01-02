'use client'

import React, { useState } from 'react'
import { ContentInput } from '@/components/content/ContentInput'
import { DiscoveryMode } from '@/components/analysis/DiscoveryMode'
import { contentApi, analysisApi } from '@/services/api'
import type { DiscoveryResult, ContentSourceType } from '@/types'

interface DiscoveryProgress {
  phase: 'uploading' | 'extracting' | 'analyzing' | 'generating' | 'complete'
  phase_name: string
  progress: number
  message: string
}

export function DiscoveryView() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DiscoveryResult | null>(null)
  const [progress, setProgress] = useState<DiscoveryProgress | null>(null)
  const [contentTitle, setContentTitle] = useState<string>('')

  const handleAnalyze = async (source: string, sourceType: ContentSourceType, file?: File) => {
    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      let textContent: string
      let title: string

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
      } else {
        // URL extraction
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

      // Now run discovery analysis
      setProgress({
        phase: 'analyzing',
        phase_name: 'Analyzing with Kinoshita Pattern...',
        progress: 50,
        message: 'Extracting problems, techniques, and cross-domain applications...'
      })

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev
          if (prev.phase === 'analyzing' && prev.progress < 70) {
            return { ...prev, progress: prev.progress + 5 }
          }
          if (prev.phase === 'analyzing') {
            return {
              phase: 'generating',
              phase_name: 'Generating cross-domain insights...',
              progress: 80,
              message: 'Finding transferable techniques and applications...'
            }
          }
          return prev
        })
      }, 3000)

      // Always pass 'plain_text' since content is already extracted
      // (PDF/URL extraction happened above, now we just have the text)
      const discoveryResult = await analysisApi.analyzeDiscovery({
        source: textContent,
        sourceType: 'plain_text'
      })

      clearInterval(progressInterval)

      setProgress({
        phase: 'complete',
        phase_name: 'Complete',
        progress: 100,
        message: 'Discovery analysis complete!'
      })

      setResult(discoveryResult)
    } catch (err: any) {
      console.error('Discovery analysis error:', err)
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to perform discovery analysis'
      setError(errorMessage)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReanalyze = async () => {
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
            🔬 Discovery Mode
          </h1>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Analyze any content using the Kinoshita Pattern - extract problems, techniques,
            and cross-domain applications inspired by how EUV lithography was discovered.
          </p>
        </div>

        {/* Show input or result */}
        {!result && !isAnalyzing && (
          <ContentInput
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
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
                <h4 className="font-medium text-red-800 dark:text-red-200">Analysis Failed</h4>
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
        {isAnalyzing && progress && (
          <div className="mt-6 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-8">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
              <h4 className="font-medium text-indigo-800 dark:text-indigo-200 mb-2">
                {progress.phase_name}
              </h4>
              <div className="w-full max-w-md mb-4">
                <div className="h-2 bg-indigo-100 dark:bg-indigo-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 transition-all duration-500"
                    style={{ width: `${progress.progress}%` }}
                  />
                </div>
              </div>
              <p className="text-sm text-indigo-600 dark:text-indigo-400 max-w-md">
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
              title="Analyze new content"
            >
              <svg className="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <DiscoveryMode
              result={result}
              videoTitle={contentTitle}
              isCached={false}
              onReanalyze={handleReanalyze}
              isReanalyzing={isAnalyzing}
            />
          </div>
        )}
      </div>
    </div>
  )
}
