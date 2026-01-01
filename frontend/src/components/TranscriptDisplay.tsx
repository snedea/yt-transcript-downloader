'use client'

import React, { useState, useEffect } from 'react'
import { downloadTextFile, copyToClipboard, generateFilename, formatTranscriptWithTimestamps } from '@/utils/download'
import { useRhetoricalAnalysis } from '@/hooks/useRhetoricalAnalysis'
import { useManipulationAnalysis } from '@/hooks/useManipulationAnalysis'
import { RhetoricalAnalysis } from '@/components/analysis/RhetoricalAnalysis'
import { ManipulationAnalysis } from '@/components/analysis/ManipulationAnalysis'
import { AnalysisModeSelector, AnalysisProgressBar, CompactModeSelector } from '@/components/analysis/AnalysisModeSelector'
import type { TranscriptSegment, AnalysisMode } from '@/types'

type AnalysisType = 'rhetorical' | 'manipulation'

interface TranscriptDisplayProps {
  transcript: string
  videoTitle: string
  videoId: string
  author?: string
  uploadDate?: string
  tokensUsed?: number
  transcriptData?: TranscriptSegment[]
  cached?: boolean
  cachedAnalysis?: import('@/types').AnalysisResult
  analysisDate?: string
}

export default function TranscriptDisplay({
  transcript,
  videoTitle,
  videoId,
  author,
  uploadDate,
  tokensUsed,
  transcriptData,
  cached,
  cachedAnalysis,
  analysisDate
}: TranscriptDisplayProps) {
  const [copied, setCopied] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(cachedAnalysis ? true : false)
  const [verifyQuotes, setVerifyQuotes] = useState(true)
  const [analysisType, setAnalysisType] = useState<AnalysisType>('manipulation')
  const [showModeSelector, setShowModeSelector] = useState(true)  // Show mode selector by default for manipulation

  // Rhetorical analysis hook (v1.0)
  const {
    loading: rhetoricalLoading,
    error: rhetoricalError,
    result: rhetoricalResult,
    isCached: isRhetoricalCached,
    analyzeTranscript: analyzeRhetorical,
    setFromCache: setRhetoricalFromCache,
    reset: resetRhetorical
  } = useRhetoricalAnalysis()

  // Manipulation analysis hook (v2.0)
  const {
    loading: manipulationLoading,
    error: manipulationError,
    result: manipulationResult,
    isCached: isManipulationCached,
    progress: manipulationProgress,
    mode: analysisMode,
    setMode: setAnalysisMode,
    analyzeTranscript: analyzeManipulation,
    setFromCache: setManipulationFromCache,
    reset: resetManipulation
  } = useManipulationAnalysis()

  // Combined state
  const analyzing = analysisType === 'rhetorical' ? rhetoricalLoading : manipulationLoading
  const analysisError = analysisType === 'rhetorical' ? rhetoricalError : manipulationError
  const analysisResult = analysisType === 'rhetorical' ? rhetoricalResult : manipulationResult
  const isAnalysisCached = analysisType === 'rhetorical' ? isRhetoricalCached : isManipulationCached

  // Load cached analysis on mount if available
  useEffect(() => {
    if (cachedAnalysis && !rhetoricalResult && !manipulationResult) {
      // Check if it's a v2.0 analysis (has dimension_scores)
      if ('dimension_scores' in cachedAnalysis) {
        setAnalysisType('manipulation')
        setManipulationFromCache(cachedAnalysis as any)
      } else {
        setAnalysisType('rhetorical')
        setRhetoricalFromCache(cachedAnalysis)
      }
    }
  }, [cachedAnalysis, rhetoricalResult, manipulationResult, setRhetoricalFromCache, setManipulationFromCache])

  const handleCopy = async () => {
    const success = await copyToClipboard(transcript)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    const filename = generateFilename(videoTitle || videoId, author, uploadDate)
    downloadTextFile(transcript, filename)
  }

  const handleDownloadWithTimestamps = () => {
    if (!transcriptData) return
    const content = formatTranscriptWithTimestamps(transcriptData)
    const filename = generateFilename(videoTitle || videoId, author, uploadDate)
    // Append _timestamps to filename before extension
    const timestampFilename = filename.replace('.txt', '_timestamps.txt')
    downloadTextFile(content, timestampFilename)
  }

  const handleAnalyze = async () => {
    setShowAnalysis(true)
    setShowModeSelector(false)

    if (analysisType === 'rhetorical') {
      await analyzeRhetorical(transcript, transcriptData, {
        verifyQuotes,
        videoTitle,
        videoAuthor: author,
        videoId
      })
    } else {
      await analyzeManipulation(transcript, transcriptData, {
        mode: analysisMode,
        verifyClaims: analysisMode === 'deep',
        videoTitle,
        videoAuthor: author,
        videoId
      })
    }
  }

  const handleCloseAnalysis = () => {
    setShowAnalysis(false)
    resetRhetorical()
    resetManipulation()
  }

  const wordCount = transcript.split(/\s+/).length

  return (
    <div className="space-y-6">
      {/* Transcript Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {videoTitle}
            </h3>
            {cached && (
              <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-0.5 rounded-full">
                Cached
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Video ID: {videoId}
          </p>
          {author && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Author: {author}
            </p>
          )}
          {tokensUsed && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Tokens used: {tokensUsed}
            </p>
          )}
        </div>

        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 mb-4 max-h-32 overflow-y-auto">
          <pre className="whitespace-pre-wrap text-xs text-gray-600 dark:text-gray-400 line-clamp-6">
            {transcript}
          </pre>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center italic">
            Scroll to preview more, or download/analyze below
          </p>
        </div>

        <div className="flex flex-col gap-3">
          {/* Primary Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleCopy}
              className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {copied ? 'Copied!' : 'Copy to Clipboard'}
            </button>
            <button
              onClick={handleDownload}
              className="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Download as TXT
            </button>
            {transcriptData && (
              <button
                onClick={handleDownloadWithTimestamps}
                className="flex-1 bg-purple-500 hover:bg-purple-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Download w/ Timestamps
              </button>
            )}
          </div>

          {/* Analysis Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            {/* Analysis Type Toggle */}
            <div className="flex items-center gap-4 mb-4">
              <div className="flex rounded-lg bg-gray-100 dark:bg-gray-700 p-1">
                <button
                  onClick={() => { setAnalysisType('manipulation'); setShowModeSelector(true) }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                    analysisType === 'manipulation'
                      ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  🔬 Trust Analysis
                </button>
                <button
                  onClick={() => { setAnalysisType('rhetorical'); setShowModeSelector(false) }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                    analysisType === 'rhetorical'
                      ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  🎭 Rhetorical Analysis
                </button>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-500">
                {analysisType === 'manipulation' ? 'v2.0 - 5 dimensions' : 'v1.0 - 4 pillars'}
              </span>
            </div>

            {/* Mode Selector for Manipulation Analysis */}
            {analysisType === 'manipulation' && showModeSelector && (
              <div className="mb-4">
                <AnalysisModeSelector
                  mode={analysisMode}
                  onChange={setAnalysisMode}
                  disabled={analyzing}
                  wordCount={wordCount}
                />
              </div>
            )}

            {/* Analysis Options for Rhetorical */}
            {analysisType === 'rhetorical' && (
              <div className="mb-4">
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <input
                    type="checkbox"
                    checked={verifyQuotes}
                    onChange={(e) => setVerifyQuotes(e.target.checked)}
                    disabled={analyzing}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  Verify quotes via web search
                </label>
              </div>
            )}

            {/* Analyze Button */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="flex-1 sm:flex-none bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium py-2.5 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {analyzing ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    {analysisType === 'manipulation'
                      ? `Running ${analysisMode === 'deep' ? 'Deep' : 'Quick'} Analysis...`
                      : 'Analyzing Rhetoric...'
                    }
                  </>
                ) : (
                  <>
                    <span>{analysisType === 'manipulation' ? '🔬' : '🎭'}</span>
                    {analysisType === 'manipulation'
                      ? `${analysisMode === 'deep' ? 'Deep' : 'Quick'} Analysis`
                      : 'Analyze Rhetoric'
                    }
                  </>
                )}
              </button>

              {/* Quick mode selector inline for manipulation */}
              {analysisType === 'manipulation' && !showModeSelector && (
                <CompactModeSelector
                  mode={analysisMode}
                  onChange={setAnalysisMode}
                  disabled={analyzing}
                />
              )}
            </div>

            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              {analysisType === 'manipulation'
                ? `Detect manipulation tactics and score content trustworthiness across 5 dimensions. Higher scores = more trustworthy. ${analysisMode === 'deep' ? 'Deep mode verifies factual claims.' : ''}`
                : 'Analyze the transcript for rhetorical techniques using AI. Identifies persuasion strategies, scores the four pillars (Logos, Pathos, Ethos, Kairos), and detects quotes/attributions.'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Error */}
      {analysisError && showAnalysis && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <h4 className="font-medium text-red-800 dark:text-red-200">Analysis Failed</h4>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">{analysisError}</p>
            </div>
            <button
              onClick={handleCloseAnalysis}
              className="text-red-500 hover:text-red-700"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Analysis Loading State */}
      {analyzing && showAnalysis && (
        <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
            <h4 className="font-medium text-indigo-800 dark:text-indigo-200 mb-2">
              {analysisType === 'manipulation'
                ? `Running ${analysisMode === 'deep' ? 'Deep' : 'Quick'} Analysis...`
                : 'Analyzing Rhetorical Techniques...'
              }
            </h4>

            {/* Progress bar for manipulation analysis */}
            {analysisType === 'manipulation' && manipulationProgress && (
              <div className="w-full max-w-md mb-4">
                <AnalysisProgressBar progress={manipulationProgress} />
              </div>
            )}

            <p className="text-sm text-indigo-600 dark:text-indigo-400 max-w-md">
              {analysisType === 'manipulation'
                ? analysisMode === 'deep'
                  ? 'Running multi-pass analysis: extracting claims, scanning for manipulation techniques, scoring dimensions, and verifying claims. This takes about 60 seconds.'
                  : 'Analyzing content across 5 dimensions: Epistemic Integrity, Argument Quality, Manipulation Risk, Rhetorical Craft, and Fairness. This takes about 15 seconds.'
                : `Our AI is examining the transcript for persuasion techniques, scoring the four pillars of rhetoric, and ${verifyQuotes ? 'verifying quotes via web search' : 'identifying potential quotes'}. This may take 30-60 seconds.`
              }
            </p>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {showAnalysis && (rhetoricalResult || manipulationResult) && (
        <div className="relative">
          <button
            onClick={handleCloseAnalysis}
            className="absolute -top-2 -right-2 z-10 bg-white dark:bg-gray-800 rounded-full p-1 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Close analysis"
          >
            <svg className="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>

          {/* Render appropriate analysis component */}
          {manipulationResult ? (
            <ManipulationAnalysis
              result={manipulationResult}
              videoTitle={videoTitle}
              videoAuthor={author}
              isCached={isManipulationCached}
              analysisDate={analysisDate}
            />
          ) : rhetoricalResult ? (
            <RhetoricalAnalysis
              result={rhetoricalResult}
              videoTitle={videoTitle}
              videoAuthor={author}
              isCached={isRhetoricalCached}
              analysisDate={analysisDate}
            />
          ) : null}
        </div>
      )}
    </div>
  )
}
