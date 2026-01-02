'use client'

import React, { useState, useEffect } from 'react'
import { downloadTextFile, copyToClipboard, generateFilename, formatTranscriptWithTimestamps } from '@/utils/download'
import { useRhetoricalAnalysis } from '@/hooks/useRhetoricalAnalysis'
import { useManipulationAnalysis } from '@/hooks/useManipulationAnalysis'
import { useContentSummary } from '@/hooks/useContentSummary'
import { RhetoricalAnalysis } from '@/components/analysis/RhetoricalAnalysis'
import { ManipulationAnalysis } from '@/components/analysis/ManipulationAnalysis'
import { ContentSummary } from '@/components/analysis/ContentSummary'
import { AnalysisModeSelector, AnalysisProgressBar, CompactModeSelector } from '@/components/analysis/AnalysisModeSelector'
import type { TranscriptSegment, AnalysisMode } from '@/types'

type AnalysisType = 'rhetorical' | 'manipulation' | 'summary'

interface TranscriptDisplayProps {
  transcript: string
  videoTitle: string
  videoId: string
  author?: string
  uploadDate?: string
  tokensUsed?: number
  transcriptData?: TranscriptSegment[]
  cached?: boolean
  // Rhetorical analysis (v1.0)
  cachedAnalysis?: import('@/types').AnalysisResult
  analysisDate?: string
  // Manipulation/Trust analysis (v2.0)
  cachedManipulation?: import('@/types').ManipulationAnalysisResult
  manipulationDate?: string
  // Content summary
  cachedSummary?: import('@/types').ContentSummaryResult
  summaryDate?: string
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
  analysisDate,
  cachedManipulation,
  manipulationDate,
  cachedSummary,
  summaryDate
}: TranscriptDisplayProps) {
  const [copied, setCopied] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(cachedAnalysis || cachedManipulation || cachedSummary ? true : false)
  const [verifyQuotes, setVerifyQuotes] = useState(true)
  const [analysisType, setAnalysisType] = useState<AnalysisType>('summary')
  const [showModeSelector, setShowModeSelector] = useState(false)  // Show mode selector for manipulation only

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

  // Content summary hook (v3.0)
  const {
    loading: summaryLoading,
    error: summaryError,
    result: summaryResult,
    isCached: isSummaryCached,
    analyzeTranscript: analyzeSummary,
    setFromCache: setSummaryFromCache,
    reset: resetSummary
  } = useContentSummary()

  // Combined state
  const analyzing = analysisType === 'rhetorical'
    ? rhetoricalLoading
    : analysisType === 'manipulation'
    ? manipulationLoading
    : summaryLoading
  const analysisError = analysisType === 'rhetorical'
    ? rhetoricalError
    : analysisType === 'manipulation'
    ? manipulationError
    : summaryError

  // Reset analysis state when video changes
  useEffect(() => {
    resetRhetorical()
    resetManipulation()
    resetSummary()
    setShowAnalysis(false)
  }, [videoId, resetRhetorical, resetManipulation, resetSummary])

  // Load ALL cached analyses after reset (so user can switch between them)
  useEffect(() => {
    let hasAnyCached = false
    let defaultType: AnalysisType = 'summary'

    // Load cached summary if available
    if (cachedSummary) {
      setSummaryFromCache(cachedSummary)
      hasAnyCached = true
      defaultType = 'summary'
    }

    // Load cached manipulation/trust analysis (v2.0) from separate column
    if (cachedManipulation) {
      setManipulationFromCache(cachedManipulation)
      if (!cachedSummary) defaultType = 'manipulation'
      hasAnyCached = true
    }

    // Load cached rhetorical analysis (v1.0) from analysis_result column
    if (cachedAnalysis && cachedAnalysis.pillar_scores) {
      setRhetoricalFromCache(cachedAnalysis)
      if (!cachedSummary && !cachedManipulation) defaultType = 'rhetorical'
      hasAnyCached = true
    }

    if (hasAnyCached) {
      setAnalysisType(defaultType)
      setShowAnalysis(true)
    }
  }, [videoId, cachedAnalysis, cachedManipulation, cachedSummary, setRhetoricalFromCache, setManipulationFromCache, setSummaryFromCache])

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
    } else if (analysisType === 'manipulation') {
      await analyzeManipulation(transcript, transcriptData, {
        mode: analysisMode,
        verifyClaims: analysisMode === 'deep',
        videoTitle,
        videoAuthor: author,
        videoId
      })
    } else {
      // Content Summary
      const videoUrl = videoId ? `https://youtube.com/watch?v=${videoId}` : undefined
      await analyzeSummary(transcript, transcriptData, {
        videoTitle,
        videoAuthor: author,
        videoId,
        videoUrl
      })
    }
  }

  const handleCloseAnalysis = () => {
    setShowAnalysis(false)
    resetRhetorical()
    resetManipulation()
    resetSummary()
  }

  // Re-analyze summary with fresh API call (bypasses cache)
  const handleReanalyzeSummary = async () => {
    const videoUrl = videoId ? `https://youtube.com/watch?v=${videoId}` : undefined
    await analyzeSummary(transcript, transcriptData, {
      videoTitle,
      videoAuthor: author,
      videoId,
      videoUrl
    })
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
          {tokensUsed !== undefined && tokensUsed > 0 && (
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
                  onClick={() => {
                    setAnalysisType('summary')
                    setShowModeSelector(false)
                    if (summaryResult) setShowAnalysis(true)
                  }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all relative ${
                    analysisType === 'summary'
                      ? 'bg-white dark:bg-gray-600 text-emerald-600 dark:text-emerald-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  📋 Summary
                  {summaryResult && <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full" />}
                </button>
                <button
                  onClick={() => {
                    setAnalysisType('manipulation')
                    setShowModeSelector(!manipulationResult)
                    if (manipulationResult) setShowAnalysis(true)
                  }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all relative ${
                    analysisType === 'manipulation'
                      ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  🔬 Trust Analysis
                  {manipulationResult && <span className="absolute -top-1 -right-1 w-2 h-2 bg-indigo-500 rounded-full" />}
                </button>
                <button
                  onClick={() => {
                    setAnalysisType('rhetorical')
                    setShowModeSelector(false)
                    if (rhetoricalResult) setShowAnalysis(true)
                  }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all relative ${
                    analysisType === 'rhetorical'
                      ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  🎭 Rhetoric
                  {rhetoricalResult && <span className="absolute -top-1 -right-1 w-2 h-2 bg-purple-500 rounded-full" />}
                </button>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-500">
                {analysisType === 'summary' ? 'Key concepts & export' : analysisType === 'manipulation' ? 'v2.0 - 5 dimensions' : 'v1.0 - 4 pillars'}
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
                className={`flex-1 sm:flex-none font-medium py-2.5 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${
                  analysisType === 'summary'
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white'
                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white'
                }`}
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
                    {analysisType === 'summary'
                      ? 'Extracting Key Concepts...'
                      : analysisType === 'manipulation'
                      ? `Running ${analysisMode === 'deep' ? 'Deep' : 'Quick'} Analysis...`
                      : 'Analyzing Rhetoric...'
                    }
                  </>
                ) : (
                  <>
                    <span>{analysisType === 'summary' ? '📋' : analysisType === 'manipulation' ? '🔬' : '🎭'}</span>
                    {analysisType === 'summary'
                      ? 'Get Summary'
                      : analysisType === 'manipulation'
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
              {analysisType === 'summary'
                ? 'Extract key concepts, TLDR, technical details, and action items. Export to Markdown, TXT, or JSON for Obsidian notes.'
                : analysisType === 'manipulation'
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
        <div className={`rounded-lg p-8 border ${
          analysisType === 'summary'
            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'
            : 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800'
        }`}>
          <div className="flex flex-col items-center justify-center text-center">
            <div className={`w-16 h-16 border-4 rounded-full animate-spin mb-4 ${
              analysisType === 'summary'
                ? 'border-emerald-200 border-t-emerald-600'
                : 'border-indigo-200 border-t-indigo-600'
            }`} />
            <h4 className={`font-medium mb-2 ${
              analysisType === 'summary'
                ? 'text-emerald-800 dark:text-emerald-200'
                : 'text-indigo-800 dark:text-indigo-200'
            }`}>
              {analysisType === 'summary'
                ? 'Extracting Key Concepts...'
                : analysisType === 'manipulation'
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

            <p className={`text-sm max-w-md ${
              analysisType === 'summary'
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-indigo-600 dark:text-indigo-400'
            }`}>
              {analysisType === 'summary'
                ? 'Detecting content type, extracting key concepts, identifying technical details, and generating action items. This takes about 10 seconds.'
                : analysisType === 'manipulation'
                ? analysisMode === 'deep'
                  ? 'Running multi-pass analysis: extracting claims, scanning for manipulation techniques, scoring dimensions, and verifying claims. This takes about 60 seconds.'
                  : 'Analyzing content across 5 dimensions: Epistemic Integrity, Argument Quality, Manipulation Risk, Rhetorical Craft, and Fairness. This takes about 15 seconds.'
                : `Our AI is examining the transcript for persuasion techniques, scoring the four pillars of rhetoric, and ${verifyQuotes ? 'verifying quotes via web search' : 'identifying potential quotes'}. This may take 30-60 seconds.`
              }
            </p>
          </div>
        </div>
      )}

      {/* Analysis Results - render based on selected analysisType */}
      {showAnalysis && (
        (analysisType === 'summary' && summaryResult) ||
        (analysisType === 'manipulation' && manipulationResult) ||
        (analysisType === 'rhetorical' && rhetoricalResult)
      ) && (
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

          {/* Render analysis component matching the selected type */}
          {analysisType === 'summary' && summaryResult && (
            <ContentSummary
              result={summaryResult}
              videoTitle={videoTitle}
              videoAuthor={author}
              videoId={videoId}
              videoUrl={videoId ? `https://youtube.com/watch?v=${videoId}` : undefined}
              isCached={isSummaryCached}
              onReanalyze={handleReanalyzeSummary}
              isReanalyzing={summaryLoading}
            />
          )}
          {analysisType === 'manipulation' && manipulationResult && (
            <ManipulationAnalysis
              result={manipulationResult}
              videoTitle={videoTitle}
              videoAuthor={author}
              isCached={isManipulationCached}
              analysisDate={analysisDate}
            />
          )}
          {analysisType === 'rhetorical' && rhetoricalResult && (
            <RhetoricalAnalysis
              result={rhetoricalResult}
              videoTitle={videoTitle}
              videoAuthor={author}
              isCached={isRhetoricalCached}
              analysisDate={analysisDate}
            />
          )}
        </div>
      )}
    </div>
  )
}
