'use client'

import React, { useState } from 'react'
import { healthApi } from '@/services/api'
import { HealthObservations } from '@/components/analysis/HealthObservations'
import type { HealthObservationResult } from '@/types'

interface HealthProgress {
  phase: 'downloading' | 'extracting' | 'detecting' | 'analyzing' | 'complete'
  phase_name: string
  progress: number
  message: string
}

export function HealthView() {
  const [videoUrl, setVideoUrl] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<HealthObservationResult | null>(null)
  const [progress, setProgress] = useState<HealthProgress | null>(null)

  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^([a-zA-Z0-9_-]{11})$/
    ]
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) return match[1]
    }
    return null
  }

  const handleAnalyze = async () => {
    const videoId = extractVideoId(videoUrl.trim())
    if (!videoId) {
      setError('Please enter a valid YouTube URL or video ID')
      return
    }

    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      // Start progress simulation
      setProgress({
        phase: 'downloading',
        phase_name: 'Downloading video...',
        progress: 10,
        message: 'Downloading video for frame extraction...'
      })

      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev || prev.phase === 'complete') return prev

          if (prev.phase === 'downloading' && prev.progress < 25) {
            return { ...prev, progress: prev.progress + 3 }
          }
          if (prev.phase === 'downloading') {
            return {
              phase: 'extracting',
              phase_name: 'Extracting frames...',
              progress: 30,
              message: 'Extracting frames at regular intervals...'
            }
          }
          if (prev.phase === 'extracting' && prev.progress < 45) {
            return { ...prev, progress: prev.progress + 3 }
          }
          if (prev.phase === 'extracting') {
            return {
              phase: 'detecting',
              phase_name: 'Detecting humans...',
              progress: 50,
              message: 'Filtering frames for human presence...'
            }
          }
          if (prev.phase === 'detecting' && prev.progress < 65) {
            return { ...prev, progress: prev.progress + 3 }
          }
          if (prev.phase === 'detecting') {
            return {
              phase: 'analyzing',
              phase_name: 'Analyzing with Claude Vision...',
              progress: 70,
              message: 'Analyzing frames for observable health features...'
            }
          }
          if (prev.phase === 'analyzing' && prev.progress < 95) {
            return { ...prev, progress: prev.progress + 2 }
          }
          return prev
        })
      }, 2000)

      const healthResult = await healthApi.analyzeHealth(videoUrl.trim(), {
        videoId,
        intervalSeconds: 30,
        maxFrames: 20,
        skipIfCached: true
      })

      clearInterval(progressInterval)

      setProgress({
        phase: 'complete',
        phase_name: 'Complete',
        progress: 100,
        message: 'Health observation analysis complete!'
      })

      setResult(healthResult)
    } catch (err: any) {
      console.error('Health analysis error:', err)
      const errorMessage = err.response?.data?.detail
        || err.message
        || 'Failed to perform health observation analysis'
      setError(errorMessage)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setProgress(null)
    setVideoUrl('')
    setError(null)
  }

  return (
    <div className="h-full overflow-auto">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Health Observations
          </h1>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Analyze YouTube videos for observable health-related features using AI vision.
            This is an <strong>educational tool only</strong> - not medical advice.
          </p>
        </div>

        {/* Disclaimer Banner */}
        <div className="mb-6 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium text-amber-800 dark:text-amber-200">Educational Tool Only</h4>
              <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                This tool identifies visual observations that MAY warrant professional evaluation.
                It does NOT diagnose conditions and should NEVER replace healthcare professionals.
              </p>
            </div>
          </div>
        </div>

        {/* Input Form */}
        {!result && !isAnalyzing && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              YouTube Video URL
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=... or video ID"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                  bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                  focus:ring-2 focus:ring-rose-500 focus:border-transparent
                  placeholder-gray-400 dark:placeholder-gray-500"
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              />
              <button
                onClick={handleAnalyze}
                disabled={!videoUrl.trim()}
                className="px-6 py-3 bg-rose-500 hover:bg-rose-600 disabled:bg-gray-300
                  dark:disabled:bg-gray-600 text-white font-medium rounded-lg
                  transition-colors disabled:cursor-not-allowed"
              >
                Analyze
              </button>
            </div>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              The video will be downloaded temporarily, frames extracted, and analyzed for observable features.
              No images are stored - only timestamps are kept.
            </p>
          </div>
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
          <div className="mt-6 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-lg p-8">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 border-4 border-rose-200 border-t-rose-600 rounded-full animate-spin mb-4" />
              <h4 className="font-medium text-rose-800 dark:text-rose-200 mb-2">
                {progress.phase_name}
              </h4>
              <div className="w-full max-w-md mb-4">
                <div className="h-2 bg-rose-100 dark:bg-rose-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-rose-500 transition-all duration-500"
                    style={{ width: `${progress.progress}%` }}
                  />
                </div>
              </div>
              <p className="text-sm text-rose-600 dark:text-rose-400 max-w-md">
                {progress.message}
              </p>
              <p className="text-xs text-rose-500 dark:text-rose-500 mt-4">
                This may take 1-3 minutes depending on video length
              </p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 relative">
            <button
              onClick={handleReset}
              className="absolute -top-2 -right-2 z-10 bg-white dark:bg-gray-800 rounded-full p-1 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Analyze new video"
            >
              <svg className="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <HealthObservations
              result={result}
              videoTitle={result.video_title}
              videoUrl={result.video_url}
              isCached={false}
              onReanalyze={handleReset}
              isReanalyzing={isAnalyzing}
            />
          </div>
        )}
      </div>
    </div>
  )
}
