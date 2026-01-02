'use client'

import React, { useState } from 'react'
import type { ContentSummaryResult, ContentType, TechnicalDetail, KeyConcept, SummaryActionItem, KeyMoment, ScholarlyContext } from '@/types'
import {
  downloadAsMarkdown,
  downloadAsText,
  downloadAsJson,
  copyMarkdownToClipboard,
  type ExportOptions
} from '@/utils/summaryExport'

interface ContentSummaryProps {
  result: ContentSummaryResult
  videoTitle?: string
  videoAuthor?: string
  videoUrl?: string
  videoId?: string
  isCached?: boolean
  onReanalyze?: () => void
  isReanalyzing?: boolean
}

type TabType = 'overview' | 'concepts' | 'scholarly' | 'technical' | 'actions' | 'moments'

// Content type display info
const CONTENT_TYPE_INFO: Record<ContentType, { label: string; icon: string; color: string }> = {
  programming_technical: { label: 'Programming & Technical', icon: '💻', color: 'bg-blue-500' },
  tutorial_howto: { label: 'Tutorial / How-To', icon: '📝', color: 'bg-green-500' },
  news_current_events: { label: 'News & Current Events', icon: '📰', color: 'bg-red-500' },
  educational: { label: 'Educational', icon: '🎓', color: 'bg-purple-500' },
  entertainment: { label: 'Entertainment', icon: '🎬', color: 'bg-pink-500' },
  discussion_opinion: { label: 'Discussion & Opinion', icon: '💬', color: 'bg-yellow-500' },
  review: { label: 'Review', icon: '⭐', color: 'bg-orange-500' },
  interview: { label: 'Interview', icon: '🎤', color: 'bg-indigo-500' },
  other: { label: 'Other', icon: '📄', color: 'bg-gray-500' }
}

// Technical category display
const TECH_CATEGORY_INFO: Record<string, { label: string; icon: string }> = {
  code_snippet: { label: 'Code Snippets', icon: '📝' },
  library: { label: 'Libraries', icon: '📚' },
  framework: { label: 'Frameworks', icon: '🏗️' },
  command: { label: 'Commands', icon: '⌨️' },
  tool: { label: 'Tools', icon: '🔧' },
  api: { label: 'APIs', icon: '🔌' },
  concept: { label: 'Concepts', icon: '💡' }
}

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function ContentSummary({
  result,
  videoTitle,
  videoAuthor,
  videoUrl,
  videoId,
  isCached,
  onReanalyze,
  isReanalyzing
}: ContentSummaryProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [copied, setCopied] = useState(false)
  const [exportMenuOpen, setExportMenuOpen] = useState(false)

  const contentTypeInfo = CONTENT_TYPE_INFO[result.content_type] || CONTENT_TYPE_INFO.other

  const exportOptions: ExportOptions = {
    videoTitle,
    videoAuthor,
    videoUrl,
    videoId
  }

  const handleCopyMarkdown = async () => {
    const success = await copyMarkdownToClipboard(result, exportOptions)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Check if scholarly context has content
  const hasScholarlyContent = !!(result.scholarly_context && (
    result.scholarly_context.figures.length > 0 ||
    result.scholarly_context.sources.length > 0 ||
    result.scholarly_context.debates.length > 0 ||
    result.scholarly_context.evidence_types.length > 0 ||
    result.scholarly_context.methodology.length > 0 ||
    result.scholarly_context.time_periods.length > 0
  ))

  // Build tabs dynamically based on available content
  const allTabs: { id: TabType; label: string; icon: string; available: boolean }[] = [
    { id: 'overview' as const, label: 'Overview', icon: '📊', available: true },
    { id: 'concepts' as const, label: 'Concepts', icon: '💡', available: result.key_concepts.length > 0 },
    { id: 'scholarly' as const, label: 'Scholarly', icon: '📚', available: hasScholarlyContent },
    { id: 'technical' as const, label: 'Technical', icon: '💻', available: result.has_technical_content },
    { id: 'actions' as const, label: 'Actions', icon: '✅', available: result.action_items.length > 0 },
    { id: 'moments' as const, label: 'Moments', icon: '⏱️', available: result.key_moments.length > 0 }
  ]
  const tabs = allTabs.filter(tab => tab.available)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-700 dark:to-teal-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold">Content Summary</h2>
              <span className={`text-xs px-2 py-1 rounded-full ${contentTypeInfo.color} text-white flex items-center gap-1`}>
                <span>{contentTypeInfo.icon}</span>
                {contentTypeInfo.label}
              </span>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached
                </span>
              )}
            </div>
            {videoTitle && (
              <p className="text-emerald-100 text-sm">{videoTitle}</p>
            )}
            {videoAuthor && (
              <p className="text-emerald-200 text-xs mt-1">by {videoAuthor}</p>
            )}
          </div>

          {/* Export Buttons */}
          <div className="flex items-center gap-2">
            {onReanalyze && (
              <button
                onClick={onReanalyze}
                disabled={isReanalyzing}
                className="bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed text-white text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                title="Re-run analysis with latest prompts"
              >
                {isReanalyzing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  '🔄 Re-analyze'
                )}
              </button>
            )}
            <button
              onClick={handleCopyMarkdown}
              className="bg-white/20 hover:bg-white/30 text-white text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
            >
              {copied ? '✓ Copied!' : '📋 Copy MD'}
            </button>
            <div className="relative">
              <button
                onClick={() => setExportMenuOpen(!exportMenuOpen)}
                className="bg-white/20 hover:bg-white/30 text-white text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
              >
                ⬇️ Export
              </button>
              {exportMenuOpen && (
                <div className="absolute right-0 mt-1 w-40 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10">
                  <button
                    onClick={() => { downloadAsMarkdown(result, exportOptions); setExportMenuOpen(false) }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-t-lg"
                  >
                    📝 Markdown (.md)
                  </button>
                  <button
                    onClick={() => { downloadAsText(result, exportOptions); setExportMenuOpen(false) }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    📄 Plain Text (.txt)
                  </button>
                  <button
                    onClick={() => { downloadAsJson(result, exportOptions); setExportMenuOpen(false) }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-b-lg"
                  >
                    🔧 JSON (.json)
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.key_concepts.length}</div>
            <div className="text-xs text-emerald-200">Key Concepts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.action_items.length}</div>
            <div className="text-xs text-emerald-200">Action Items</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.keywords.length}</div>
            <div className="text-xs text-emerald-200">Keywords</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.transcript_word_count}</div>
            <div className="text-xs text-emerald-200">Words</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 min-w-fit py-3 px-4 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-emerald-600 dark:text-emerald-400 border-b-2 border-emerald-600 dark:border-emerald-400 bg-emerald-50 dark:bg-emerald-900/20'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab result={result} videoUrl={videoUrl} />
        )}
        {activeTab === 'concepts' && (
          <ConceptsTab concepts={result.key_concepts} videoUrl={videoUrl} />
        )}
        {activeTab === 'scholarly' && result.scholarly_context && (
          <ScholarlyTab context={result.scholarly_context} />
        )}
        {activeTab === 'technical' && (
          <TechnicalTab details={result.technical_details} videoUrl={videoUrl} />
        )}
        {activeTab === 'actions' && (
          <ActionsTab items={result.action_items} />
        )}
        {activeTab === 'moments' && (
          <MomentsTab moments={result.key_moments} videoUrl={videoUrl} />
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Analyzed in {result.analysis_duration_seconds}s | {result.tokens_used} tokens
        </div>
        <div className="flex flex-wrap gap-1">
          {result.suggested_obsidian_tags.slice(0, 5).map((tag, idx) => (
            <span
              key={idx}
              className="text-xs bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 rounded-full"
            >
              {tag}
            </span>
          ))}
          {result.suggested_obsidian_tags.length > 5 && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              +{result.suggested_obsidian_tags.length - 5} more
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// Tab Components

function OverviewTab({ result, videoUrl }: { result: ContentSummaryResult; videoUrl?: string }) {
  return (
    <div className="space-y-6">
      {/* TLDR */}
      <div className="p-4 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800">
        <h3 className="font-semibold text-emerald-800 dark:text-emerald-200 mb-2 flex items-center gap-2">
          <span>📋</span> TLDR
        </h3>
        <p className="text-emerald-700 dark:text-emerald-300">
          {result.tldr}
        </p>
      </div>

      {/* Top Concepts Preview */}
      {result.key_concepts.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>💡</span> Top Concepts
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {result.key_concepts.slice(0, 4).map((concept, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border ${
                  concept.importance === 'high'
                    ? 'border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20'
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800'
                }`}
              >
                <div className="font-medium text-gray-800 dark:text-gray-200 flex items-center gap-2">
                  {concept.importance === 'high' && <span className="text-amber-500">★</span>}
                  {concept.concept}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                  {concept.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keywords */}
      {result.keywords.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🏷️</span> Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {result.keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions Preview */}
      {result.action_items.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>✅</span> Quick Actions
          </h3>
          <ul className="space-y-2">
            {result.action_items.slice(0, 3).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className={`mt-0.5 ${item.priority === 'high' ? 'text-red-500' : 'text-gray-400'}`}>
                  {item.priority === 'high' ? '❗' : '•'}
                </span>
                <span className="text-gray-700 dark:text-gray-300">{item.action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function ConceptsTab({ concepts, videoUrl }: { concepts: KeyConcept[]; videoUrl?: string }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {concepts.length} key concepts extracted from the content
      </p>
      {concepts.map((concept, idx) => (
        <div
          key={idx}
          className={`p-4 rounded-lg border-l-4 ${
            concept.importance === 'high'
              ? 'border-l-amber-500 bg-amber-50 dark:bg-amber-900/20'
              : concept.importance === 'medium'
              ? 'border-l-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-l-gray-300 bg-gray-50 dark:bg-gray-800'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
              {concept.importance === 'high' && <span className="text-amber-500">★</span>}
              {concept.concept}
            </h4>
            {concept.timestamp !== undefined && concept.timestamp !== null && (
              <a
                href={videoUrl ? `${videoUrl}&t=${Math.floor(concept.timestamp)}` : '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                ⏱️ {formatTimestamp(concept.timestamp)}
              </a>
            )}
          </div>
          <p className="text-gray-700 dark:text-gray-300">{concept.explanation}</p>
        </div>
      ))}
    </div>
  )
}

function TechnicalTab({ details, videoUrl }: { details: TechnicalDetail[]; videoUrl?: string }) {
  // Group by category
  const grouped = details.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = []
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, TechnicalDetail[]>)

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        {details.length} technical items extracted
      </p>
      {Object.entries(grouped).map(([category, items]) => {
        const categoryInfo = TECH_CATEGORY_INFO[category] || { label: category, icon: '📦' }
        return (
          <div key={category}>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
              <span>{categoryInfo.icon}</span> {categoryInfo.label}
            </h4>
            <div className="space-y-3">
              {items.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-800 dark:text-gray-200">{item.name}</span>
                    {item.timestamp !== undefined && item.timestamp !== null && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        ⏱️ {formatTimestamp(item.timestamp)}
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">{item.description}</p>
                  )}
                  {item.code && (
                    <pre className="mt-2 p-2 bg-gray-900 text-gray-100 rounded text-sm overflow-x-auto">
                      <code>{item.code}</code>
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ActionsTab({ items }: { items: SummaryActionItem[] }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {items.length} action items to remember or follow up on
      </p>
      {items.map((item, idx) => (
        <div
          key={idx}
          className={`p-4 rounded-lg border-l-4 flex items-start gap-3 ${
            item.priority === 'high'
              ? 'border-l-red-500 bg-red-50 dark:bg-red-900/20'
              : item.priority === 'medium'
              ? 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
              : 'border-l-gray-300 bg-gray-50 dark:bg-gray-800'
          }`}
        >
          <input
            type="checkbox"
            className="mt-1 h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
          />
          <div className="flex-1">
            <p className={`text-gray-800 dark:text-gray-200 ${item.priority === 'high' ? 'font-medium' : ''}`}>
              {item.action}
            </p>
            {item.context && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 italic">
                {item.context}
              </p>
            )}
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${
            item.priority === 'high'
              ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
              : item.priority === 'medium'
              ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
          }`}>
            {item.priority}
          </span>
        </div>
      ))}
    </div>
  )
}

function MomentsTab({ moments, videoUrl }: { moments: KeyMoment[]; videoUrl?: string }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {moments.length} key moments in the video
      </p>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-emerald-200 dark:bg-emerald-800" />

        {moments.map((moment, idx) => (
          <div key={idx} className="relative pl-10 pb-6">
            {/* Timeline dot */}
            <div className="absolute left-2.5 w-3 h-3 bg-emerald-500 rounded-full" />

            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-800 dark:text-gray-200">{moment.title}</h4>
                <a
                  href={videoUrl ? `${videoUrl}&t=${Math.floor(moment.timestamp)}` : '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-2 py-1 rounded hover:bg-emerald-200 dark:hover:bg-emerald-800"
                >
                  ⏱️ {formatTimestamp(moment.timestamp)}
                </a>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">{moment.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ScholarlyTab({ context }: { context: ScholarlyContext }) {
  const totalItems =
    context.figures.length +
    context.sources.length +
    context.debates.length +
    context.evidence_types.length +
    context.methodology.length +
    context.time_periods.length

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {totalItems} scholarly elements extracted from educational content
      </p>

      {/* Historical Figures */}
      {context.figures.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>👤</span> Historical Figures & Named Individuals
          </h4>
          <div className="grid md:grid-cols-2 gap-3">
            {context.figures.map((figure, idx) => (
              <div
                key={idx}
                className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800"
              >
                <div className="font-medium text-purple-800 dark:text-purple-200">
                  {figure.name}
                  {figure.period && (
                    <span className="ml-2 text-xs font-normal text-purple-600 dark:text-purple-400">
                      ({figure.period})
                    </span>
                  )}
                </div>
                {figure.role && (
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                    <span className="font-medium">Role:</span> {figure.role}
                  </p>
                )}
                {figure.relationships && (
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                    <span className="font-medium">Relationships:</span> {figure.relationships}
                  </p>
                )}
                {figure.significance && (
                  <p className="text-sm text-purple-600 dark:text-purple-400 mt-1 italic">
                    {figure.significance}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources & Texts */}
      {context.sources.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>📜</span> Sources & Texts Discussed
          </h4>
          <div className="space-y-2">
            {context.sources.map((source, idx) => (
              <div
                key={idx}
                className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800"
              >
                <div className="font-medium text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  {source.name}
                  {source.type && (
                    <span className="text-xs bg-amber-200 dark:bg-amber-800 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded">
                      {source.type}
                    </span>
                  )}
                </div>
                {source.description && (
                  <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                    {source.description}
                  </p>
                )}
                {source.significance && (
                  <p className="text-sm text-amber-600 dark:text-amber-400 mt-1 italic">
                    {source.significance}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scholarly Debates */}
      {context.debates.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>⚖️</span> Scholarly Debates & Contested Topics
          </h4>
          <div className="space-y-3">
            {context.debates.map((debate, idx) => (
              <div
                key={idx}
                className="p-4 bg-rose-50 dark:bg-rose-900/20 rounded-lg border border-rose-200 dark:border-rose-800"
              >
                <div className="font-medium text-rose-800 dark:text-rose-200 mb-2">
                  {debate.topic}
                </div>
                {debate.positions.length > 0 && (
                  <div className="mb-2">
                    <span className="text-sm font-medium text-rose-700 dark:text-rose-300">Positions:</span>
                    <ul className="mt-1 space-y-1">
                      {debate.positions.map((position, pidx) => (
                        <li key={pidx} className="text-sm text-rose-600 dark:text-rose-400 flex items-start gap-2">
                          <span className="text-rose-400">•</span>
                          {position}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {debate.evidence && (
                  <p className="text-sm text-rose-700 dark:text-rose-300 mt-2">
                    <span className="font-medium">Evidence:</span> {debate.evidence}
                  </p>
                )}
                {debate.consensus && (
                  <p className="text-sm text-rose-600 dark:text-rose-400 mt-1 italic">
                    <span className="font-medium not-italic">Consensus:</span> {debate.consensus}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence Types */}
      {context.evidence_types.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🔍</span> Types of Evidence Presented
          </h4>
          <div className="grid md:grid-cols-2 gap-3">
            {context.evidence_types.map((evidence, idx) => (
              <div
                key={idx}
                className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
              >
                <div className="font-medium text-blue-800 dark:text-blue-200 capitalize">
                  {evidence.type.replace(/_/g, ' ')}
                </div>
                {evidence.examples.length > 0 && (
                  <ul className="mt-1 space-y-0.5">
                    {evidence.examples.map((example, eidx) => (
                      <li key={eidx} className="text-sm text-blue-600 dark:text-blue-400 flex items-start gap-1">
                        <span>-</span> {example}
                      </li>
                    ))}
                  </ul>
                )}
                {evidence.significance && (
                  <p className="text-sm text-blue-500 dark:text-blue-500 mt-1 italic">
                    {evidence.significance}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Time Periods */}
      {context.time_periods.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🕰️</span> Historical Periods
          </h4>
          <div className="flex flex-wrap gap-2">
            {context.time_periods.map((period, idx) => (
              <div
                key={idx}
                className="p-3 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800"
              >
                <div className="font-medium text-teal-800 dark:text-teal-200">
                  {period.period}
                  {period.dates && (
                    <span className="ml-2 text-xs font-normal text-teal-600 dark:text-teal-400">
                      {period.dates}
                    </span>
                  )}
                </div>
                {period.context && (
                  <p className="text-sm text-teal-600 dark:text-teal-400 mt-1">
                    {period.context}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Methodology */}
      {context.methodology.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🔬</span> Analytical Methodology
          </h4>
          <div className="flex flex-wrap gap-2">
            {context.methodology.map((method, idx) => (
              <span
                key={idx}
                className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1.5 rounded-lg text-sm"
              >
                {method}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
