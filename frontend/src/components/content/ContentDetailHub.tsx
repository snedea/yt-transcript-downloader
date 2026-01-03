'use client'

import { useState, useEffect } from 'react'
import { cacheApi } from '@/services/api'
import { downloadTextFile, copyToClipboard } from '@/utils/download'

interface ContentDetailHubProps {
  contentId: string
  onBack: () => void
}

type AnalysisType = 'summary' | 'rhetorical' | 'manipulation' | 'discovery' | 'prompts' | 'health'

interface AnalysisOption {
  id: AnalysisType
  title: string
  description: string
  icon: string
  availableFor: string[] // Which source types support this
}

const ANALYSIS_OPTIONS: AnalysisOption[] = [
  {
    id: 'summary',
    title: 'Summary',
    description: 'Quick overview with key points and takeaways',
    icon: '📝',
    availableFor: ['youtube', 'pdf', 'web_url', 'plain_text']
  },
  {
    id: 'rhetorical',
    title: 'Rhetorical Analysis',
    description: '5-dimension trust evaluation (epistemic, argument, manipulation, craft, balance)',
    icon: '🎯',
    availableFor: ['youtube', 'pdf', 'web_url', 'plain_text']
  },
  {
    id: 'manipulation',
    title: 'Manipulation Detection',
    description: 'Identify 34+ persuasion techniques and fallacies',
    icon: '🔍',
    availableFor: ['youtube', 'pdf', 'web_url', 'plain_text']
  },
  {
    id: 'discovery',
    title: 'Discovery Mode',
    description: 'Extract key topics, themes, and cross-domain applications',
    icon: '💡',
    availableFor: ['youtube', 'pdf', 'web_url', 'plain_text']
  },
  {
    id: 'prompts',
    title: 'Prompt Generation',
    description: 'Generate AI prompts from content for various use cases',
    icon: '✨',
    availableFor: ['youtube', 'pdf', 'web_url', 'plain_text']
  },
  {
    id: 'health',
    title: 'Health Observations',
    description: 'AI vision analysis of video frames (YouTube only)',
    icon: '🏥',
    availableFor: ['youtube']
  }
]

export function ContentDetailHub({ contentId, onBack }: ContentDetailHubProps) {
  const [content, setContent] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedAnalysis, setExpandedAnalysis] = useState<AnalysisType | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    loadContent()
  }, [contentId])

  const loadContent = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await cacheApi.get(contentId)
      setContent(data)
    } catch (err: any) {
      console.error('Failed to load content:', err)
      setError(err.message || 'Failed to load content')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (!content) return
    const success = await copyToClipboard(content.transcript)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    if (!content) return
    downloadTextFile(content.transcript, `${content.video_title}.txt`)
  }

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'youtube': return '🎬'
      case 'pdf': return '📄'
      case 'web_url': return '🌐'
      case 'plain_text': return '📋'
      default: return '📄'
    }
  }

  const getSourceLabel = (sourceType: string) => {
    switch (sourceType) {
      case 'youtube': return 'YouTube Video'
      case 'pdf': return 'PDF Document'
      case 'web_url': return 'Web Article'
      case 'plain_text': return 'Pasted Text'
      default: return 'Content'
    }
  }

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return null
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return dateStr
    }
  }

  const isAnalysisComplete = (analysisId: AnalysisType): boolean => {
    if (!content) return false

    switch (analysisId) {
      case 'summary': return !!content.summary_result
      case 'rhetorical': return !!content.analysis_result
      case 'manipulation': return !!content.manipulation_result
      case 'discovery': return !!content.discovery_result
      case 'prompts': return !!content.prompts_result
      case 'health': return !!content.health_observation_result
      default: return false
    }
  }

  const getAnalysisDate = (analysisId: AnalysisType): string | undefined => {
    if (!content) return undefined

    switch (analysisId) {
      case 'summary': return content.summary_date
      case 'rhetorical': return content.analysis_date
      case 'manipulation': return content.manipulation_date
      case 'discovery': return content.discovery_date
      case 'prompts': return content.prompts_date
      case 'health': return content.health_observation_date
      default: return undefined
    }
  }

  const isAnalysisAvailable = (option: AnalysisOption): boolean => {
    if (!content) return false
    return option.availableFor.includes(content.source_type)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (error || !content) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <div className="text-red-500 mb-4">
          <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
          {error || 'Content not found'}
        </p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
        >
          Back to Library
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors mb-4"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Library
        </button>

        <div className="flex items-start gap-4">
          <div className="text-4xl">{getSourceIcon(content.source_type)}</div>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {content.video_title}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                {getSourceLabel(content.source_type)}
              </span>
              {content.author && (
                <>
                  <span>•</span>
                  <span>{content.author}</span>
                </>
              )}
              {content.upload_date && (
                <>
                  <span>•</span>
                  <span>{content.upload_date}</span>
                </>
              )}
              <span>•</span>
              <span>{content.word_count?.toLocaleString() || 0} words</span>
              {content.page_count && (
                <>
                  <span>•</span>
                  <span>{content.page_count} pages</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Full Content Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              📄 Full Content
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
              >
                {copied ? '✓ Copied' : 'Copy'}
              </button>
              <button
                onClick={handleDownload}
                className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
              >
                Download
              </button>
            </div>
          </div>
          <div className="prose dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg max-h-96 overflow-y-auto">
              {content.transcript}
            </pre>
          </div>
        </section>

        {/* Analysis Options Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🎯 Analysis Options
          </h2>
          <div className="space-y-3">
            {ANALYSIS_OPTIONS.map((option) => {
              const isComplete = isAnalysisComplete(option.id)
              const isAvailable = isAnalysisAvailable(option)
              const analysisDate = getAnalysisDate(option.id)

              if (!isAvailable) return null

              return (
                <div
                  key={option.id}
                  className={`border rounded-lg p-4 transition-colors ${
                    isComplete
                      ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <span className="text-2xl">{option.icon}</span>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                          {option.title}
                          {isComplete && (
                            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                              ✓ Complete
                            </span>
                          )}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {option.description}
                        </p>
                        {isComplete && analysisDate && (
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            Last run: {formatDate(analysisDate)}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {isComplete ? (
                        <>
                          <button
                            onClick={() => setExpandedAnalysis(expandedAnalysis === option.id ? null : option.id)}
                            className="px-3 py-1.5 text-sm bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-900/50 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-md transition-colors"
                          >
                            {expandedAnalysis === option.id ? 'Hide' : 'View'}
                          </button>
                          <button
                            className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                          >
                            Re-run
                          </button>
                        </>
                      ) : (
                        <button
                          className="px-4 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors"
                        >
                          Run Analysis
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Expanded Analysis Result */}
                  {expandedAnalysis === option.id && isComplete && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="bg-white dark:bg-gray-900 rounded-lg p-4">
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Analysis results will be displayed here (integrate existing components)
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      </div>
    </div>
  )
}
