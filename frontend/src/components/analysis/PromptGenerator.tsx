'use client'

import React, { useState } from 'react'
import type {
  PromptGeneratorResult,
  GeneratedPrompt,
  PromptCategory
} from '@/types'
import { PROMPT_CATEGORY_INFO } from '@/hooks/usePromptGenerator'

interface PromptGeneratorProps {
  result: PromptGeneratorResult
  videoTitle?: string
  videoAuthor?: string
  videoUrl?: string
  isCached?: boolean
  onRegenerate?: () => void
  isRegenerating?: boolean
}

const CATEGORY_COLORS: Record<string, string> = {
  indigo: 'border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20',
  blue: 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20',
  red: 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20',
  green: 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20',
  purple: 'border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20',
  yellow: 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20',
  teal: 'border-teal-200 dark:border-teal-800 bg-teal-50 dark:bg-teal-900/20'
}

const CATEGORY_TEXT_COLORS: Record<string, string> = {
  indigo: 'text-indigo-800 dark:text-indigo-200',
  blue: 'text-blue-800 dark:text-blue-200',
  red: 'text-red-800 dark:text-red-200',
  green: 'text-green-800 dark:text-green-200',
  purple: 'text-purple-800 dark:text-purple-200',
  yellow: 'text-yellow-800 dark:text-yellow-200',
  teal: 'text-teal-800 dark:text-teal-200'
}

const CATEGORY_HOVER_COLORS: Record<string, string> = {
  indigo: 'hover:bg-indigo-100 dark:hover:bg-indigo-900/30',
  blue: 'hover:bg-blue-100 dark:hover:bg-blue-900/30',
  red: 'hover:bg-red-100 dark:hover:bg-red-900/30',
  green: 'hover:bg-green-100 dark:hover:bg-green-900/30',
  purple: 'hover:bg-purple-100 dark:hover:bg-purple-900/30',
  yellow: 'hover:bg-yellow-100 dark:hover:bg-yellow-900/30',
  teal: 'hover:bg-teal-100 dark:hover:bg-teal-900/30'
}

export function PromptGenerator({
  result,
  videoTitle,
  videoAuthor,
  videoUrl,
  isCached,
  onRegenerate,
  isRegenerating
}: PromptGeneratorProps) {
  const [expandedPrompt, setExpandedPrompt] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const handleCopyPrompt = async (promptId: string, content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedId(promptId)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 dark:from-violet-700 dark:to-fuchsia-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold">Prompt Generator</h2>
              <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                Nate B Jones Techniques
              </span>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached
                </span>
              )}
            </div>
            <p className="text-violet-100 text-sm mb-1">
              7 production-ready prompts for AI tools
            </p>
            {videoTitle && (
              <p className="text-violet-200 text-xs">{videoTitle}</p>
            )}
            {videoAuthor && (
              <p className="text-violet-200 text-xs">by {videoAuthor}</p>
            )}
          </div>

          {/* Regenerate Button */}
          {onRegenerate && (
            <button
              onClick={onRegenerate}
              disabled={isRegenerating}
              className="bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed text-white text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
            >
              {isRegenerating ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </>
              ) : (
                <>Regenerate</>
              )}
            </button>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.total_prompts}</div>
            <div className="text-xs text-violet-200">Prompts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.total_word_count.toLocaleString()}</div>
            <div className="text-xs text-violet-200">Total Words</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.input_word_count.toLocaleString()}</div>
            <div className="text-xs text-violet-200">Input Words</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.tokens_used.toLocaleString()}</div>
            <div className="text-xs text-violet-200">Tokens Used</div>
          </div>
        </div>

        {/* Analysis Types Used */}
        {result.analysis_types_used.length > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs text-violet-200">Enriched with:</span>
            {result.analysis_types_used.map((type) => (
              <span
                key={type}
                className="text-xs bg-white/20 px-2 py-0.5 rounded"
              >
                {type}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Prompts List */}
      <div className="p-6 space-y-4">
        {result.prompts.map((prompt) => (
          <PromptCard
            key={prompt.prompt_id}
            prompt={prompt}
            isExpanded={expandedPrompt === prompt.prompt_id}
            onToggle={() => setExpandedPrompt(
              expandedPrompt === prompt.prompt_id ? null : prompt.prompt_id
            )}
            isCopied={copiedId === prompt.prompt_id}
            onCopy={() => handleCopyPrompt(prompt.prompt_id, prompt.prompt_content)}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Generated in {result.analysis_duration_seconds.toFixed(1)}s using {result.model_used}
        </div>
        <div className="text-xs text-gray-400 dark:text-gray-500">
          v{result.analysis_version}
        </div>
      </div>
    </div>
  )
}

interface PromptCardProps {
  prompt: GeneratedPrompt
  isExpanded: boolean
  onToggle: () => void
  isCopied: boolean
  onCopy: () => void
}

function PromptCard({
  prompt,
  isExpanded,
  onToggle,
  isCopied,
  onCopy
}: PromptCardProps) {
  const categoryInfo = PROMPT_CATEGORY_INFO[prompt.category as PromptCategory]
  const color = categoryInfo?.color || 'indigo'
  const borderColor = CATEGORY_COLORS[color] || CATEGORY_COLORS.indigo
  const textColor = CATEGORY_TEXT_COLORS[color] || CATEGORY_TEXT_COLORS.indigo
  const hoverColor = CATEGORY_HOVER_COLORS[color] || CATEGORY_HOVER_COLORS.indigo

  return (
    <div className={`rounded-lg border ${borderColor} overflow-hidden`}>
      {/* Header - Always visible */}
      <div
        className={`p-4 flex items-start justify-between ${hoverColor} transition-colors cursor-pointer`}
        onClick={onToggle}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <span className="text-xl">{prompt.category_icon}</span>
            <h3 className={`font-semibold ${textColor}`}>
              {prompt.category_name}
            </h3>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {prompt.word_count} words
            </span>
          </div>
          <h4 className={`font-medium ${textColor} opacity-90`}>
            {prompt.title}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {prompt.description}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            Target: {prompt.target_tool}
          </p>
        </div>
        <div className="flex items-center gap-2 ml-4">
          {/* Copy Button */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              onCopy()
            }}
            className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium transition-all ${
              isCopied
                ? 'bg-green-600 text-white'
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            {isCopied ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </button>
          {/* Expand/Collapse */}
          <span className="text-gray-500 dark:text-gray-400">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700">
          {/* Intent Specification */}
          <div className="p-4 bg-gray-50 dark:bg-gray-900/50">
            <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
              Intent Specification
            </h5>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {prompt.intent_specification}
            </p>
          </div>

          {/* Full Prompt Content */}
          <div className="p-4 bg-gray-900 dark:bg-gray-950">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-400 flex items-center gap-2">
                Full Production-Ready Prompt
              </span>
            </div>
            <pre className="text-xs text-gray-300 bg-gray-800 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto max-h-96 whitespace-pre-wrap font-mono">
              {prompt.prompt_content}
            </pre>
          </div>

          {/* Disambiguation Questions */}
          {prompt.disambiguation_questions.length > 0 && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                Disambiguation Questions
              </h5>
              <ul className="space-y-1">
                {prompt.disambiguation_questions.map((q, idx) => (
                  <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                    <span className="text-violet-500">?</span>
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Success Criteria & Failure Conditions */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 grid md:grid-cols-2 gap-4">
            {prompt.success_criteria.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                  Success Criteria
                </h5>
                <ul className="space-y-1">
                  {prompt.success_criteria.map((c, idx) => (
                    <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-green-500">✓</span>
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {prompt.failure_conditions.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                  Failure Handling
                </h5>
                <ul className="space-y-1">
                  {prompt.failure_conditions.map((f, idx) => (
                    <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-red-500">!</span>
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Context Used */}
          {(prompt.video_context_used.length > 0 || prompt.analysis_context_used.length > 0) && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
              <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                Context Used from Video
              </h5>
              <div className="flex flex-wrap gap-2">
                {prompt.video_context_used.map((ctx, idx) => (
                  <span
                    key={`video-${idx}`}
                    className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-1 rounded"
                  >
                    {ctx}
                  </span>
                ))}
                {prompt.analysis_context_used.map((ctx, idx) => (
                  <span
                    key={`analysis-${idx}`}
                    className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 px-2 py-1 rounded"
                  >
                    {ctx}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Expected Output */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-1">
              Expected Output
            </h5>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {prompt.estimated_output_type}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Loading state component for prompt generation
 */
export function PromptGeneratorLoading({
  progress
}: {
  progress?: {
    phase: string
    phase_name: string
    progress: number
    message: string
  }
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 dark:from-violet-700 dark:to-fuchsia-700 text-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <h2 className="text-xl font-bold">Generating Prompts...</h2>
        </div>

        {progress && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{progress.phase_name}</span>
              <span>{progress.progress}%</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div
                className="bg-white rounded-full h-2 transition-all duration-500"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
            <p className="text-sm text-violet-200">{progress.message}</p>
          </div>
        )}
      </div>

      {/* Placeholder cards */}
      <div className="p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 animate-pulse"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
            <div className="h-3 w-64 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
            <div className="h-3 w-48 bg-gray-200 dark:bg-gray-700 rounded mt-2" />
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Error state component for prompt generation
 */
export function PromptGeneratorError({
  error,
  onRetry
}: {
  error: string
  onRetry?: () => void
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-red-600 to-rose-600 dark:from-red-700 dark:to-rose-700 text-white p-6">
        <div className="flex items-center gap-3 mb-2">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-xl font-bold">Generation Failed</h2>
        </div>
        <p className="text-red-100">{error}</p>
      </div>
      {onRetry && (
        <div className="p-6 flex justify-center">
          <button
            onClick={onRetry}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  )
}

/**
 * Empty state / CTA component
 */
export function PromptGeneratorEmpty({
  onGenerate,
  isGenerating
}: {
  onGenerate: () => void
  isGenerating?: boolean
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="p-8 text-center">
        <div className="text-6xl mb-4">✨</div>
        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-2">
          Prompt Generator
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
          Generate 7 production-ready prompts for AI tools based on this video.
          Each prompt uses Nate B Jones&apos; techniques for explicit intent,
          disambiguation, and graceful failure handling.
        </p>

        {/* Category Preview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 max-w-lg mx-auto">
          {Object.entries(PROMPT_CATEGORY_INFO).slice(0, 4).map(([key, info]) => (
            <div
              key={key}
              className="text-center p-2 rounded-lg bg-gray-50 dark:bg-gray-700"
            >
              <span className="text-2xl">{info.icon}</span>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{info.name}</p>
            </div>
          ))}
        </div>

        <button
          onClick={onGenerate}
          disabled={isGenerating}
          className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 mx-auto"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Generating...
            </>
          ) : (
            <>
              <span>✨</span>
              Generate Prompts
            </>
          )}
        </button>
      </div>
    </div>
  )
}
