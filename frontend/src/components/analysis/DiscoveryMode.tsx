'use client'

import React, { useState } from 'react'
import type {
  DiscoveryResult,
  Problem,
  Technique,
  CrossDomainApplication,
  ResearchReference,
  ExperimentIdea
} from '@/types'

interface DiscoveryModeProps {
  result: DiscoveryResult
  videoTitle?: string
  videoAuthor?: string
  videoUrl?: string
  isCached?: boolean
  onReanalyze?: () => void
  isReanalyzing?: boolean
}

type TabType = 'overview' | 'problems' | 'techniques' | 'applications' | 'research' | 'experiments'

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100)
  let color = 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'

  if (percentage >= 80) {
    color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  } else if (percentage >= 60) {
    color = 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  } else if (percentage >= 40) {
    color = 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  }

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${color}`}>
      {percentage}% confidence
    </span>
  )
}

export function DiscoveryMode({
  result,
  videoTitle,
  videoAuthor,
  videoUrl,
  isCached,
  onReanalyze,
  isReanalyzing
}: DiscoveryModeProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [expandedTechnique, setExpandedTechnique] = useState<string | null>(null)
  const [expandedApplication, setExpandedApplication] = useState<string | null>(null)

  // Build tabs dynamically based on available content
  const tabs: { id: TabType; label: string; icon: string; count?: number }[] = [
    { id: 'overview', label: 'Overview', icon: '🔬' },
    { id: 'problems', label: 'Problems', icon: '🎯', count: result.problems.length },
    { id: 'techniques', label: 'Techniques', icon: '⚙️', count: result.techniques.length },
    { id: 'applications', label: 'Applications', icon: '💡', count: result.cross_domain_applications.length },
    { id: 'research', label: 'Research Trail', icon: '📚', count: result.research_trail.length },
    { id: 'experiments', label: 'Experiments', icon: '🧪', count: result.experiment_ideas.length }
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-700 dark:to-purple-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold">Discovery Mode</h2>
              <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                Kinoshita Pattern
              </span>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached
                </span>
              )}
            </div>
            <p className="text-indigo-100 text-sm mb-1">
              Cross-domain knowledge transfer analysis
            </p>
            {videoTitle && (
              <p className="text-indigo-200 text-xs">{videoTitle}</p>
            )}
            {videoAuthor && (
              <p className="text-indigo-200 text-xs">by {videoAuthor}</p>
            )}
          </div>

          {/* Reanalyze Button */}
          {onReanalyze && (
            <button
              onClick={onReanalyze}
              disabled={isReanalyzing}
              className="bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed text-white text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
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
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-5 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.problems.length}</div>
            <div className="text-xs text-indigo-200">Problems</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.techniques.length}</div>
            <div className="text-xs text-indigo-200">Techniques</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.cross_domain_applications.length}</div>
            <div className="text-xs text-indigo-200">Applications</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.research_trail.length}</div>
            <div className="text-xs text-indigo-200">References</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.key_insights.length}</div>
            <div className="text-xs text-indigo-200">Insights</div>
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
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
              {tab.count !== undefined && tab.count > 0 && (
                <span className="ml-1 text-xs bg-gray-200 dark:bg-gray-600 px-1.5 py-0.5 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab result={result} />
        )}
        {activeTab === 'problems' && (
          <ProblemsTab problems={result.problems} videoUrl={videoUrl} />
        )}
        {activeTab === 'techniques' && (
          <TechniquesTab
            techniques={result.techniques}
            videoUrl={videoUrl}
            expandedId={expandedTechnique}
            onToggle={setExpandedTechnique}
          />
        )}
        {activeTab === 'applications' && (
          <ApplicationsTab
            applications={result.cross_domain_applications}
            techniques={result.techniques}
            expandedId={expandedApplication}
            onToggle={setExpandedApplication}
          />
        )}
        {activeTab === 'research' && (
          <ResearchTab references={result.research_trail} videoUrl={videoUrl} />
        )}
        {activeTab === 'experiments' && (
          <ExperimentsTab
            experiments={result.experiment_ideas}
            recommendedReads={result.recommended_reads}
          />
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Analyzed in {result.analysis_duration_seconds.toFixed(1)}s | {result.tokens_used} tokens
        </div>
        <div className="text-xs text-gray-400 dark:text-gray-500">
          v{result.analysis_version}
        </div>
      </div>
    </div>
  )
}

// Tab Components

function OverviewTab({ result }: { result: DiscoveryResult }) {
  return (
    <div className="space-y-6">
      {/* Key Insights */}
      {result.key_insights.length > 0 && (
        <div className="p-4 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
          <h3 className="font-semibold text-indigo-800 dark:text-indigo-200 mb-3 flex items-center gap-2">
            <span>💎</span> Key Insights
          </h3>
          <ul className="space-y-2">
            {result.key_insights.map((insight, idx) => (
              <li key={idx} className="flex items-start gap-2 text-indigo-700 dark:text-indigo-300">
                <span className="text-indigo-400 mt-0.5">•</span>
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Problems Preview */}
      {result.problems.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🎯</span> Problems Identified
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {result.problems.slice(0, 2).map((problem) => (
              <div
                key={problem.problem_id}
                className="p-3 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20"
              >
                <div className="font-medium text-red-800 dark:text-red-200 mb-1">
                  {problem.statement}
                </div>
                <div className="text-xs text-red-600 dark:text-red-400">
                  Domain: {problem.domain}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Techniques Preview */}
      {result.techniques.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>⚙️</span> Techniques Discovered
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {result.techniques.slice(0, 2).map((technique) => (
              <div
                key={technique.technique_id}
                className="p-3 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20"
              >
                <div className="font-medium text-blue-800 dark:text-blue-200 mb-1">
                  {technique.name}
                </div>
                <p className="text-sm text-blue-600 dark:text-blue-400 line-clamp-2">
                  {technique.principle}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Applications Preview */}
      {result.cross_domain_applications.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>💡</span> Cross-Domain Applications
          </h3>
          <div className="space-y-3">
            {result.cross_domain_applications.slice(0, 2).map((app) => (
              <div
                key={app.application_id}
                className="p-3 rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-green-800 dark:text-green-200">
                    → {app.target_domain}
                  </span>
                  <ConfidenceBadge confidence={app.confidence} />
                </div>
                <p className="text-sm text-green-700 dark:text-green-300 italic">
                  &ldquo;{app.hypothesis}&rdquo;
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ProblemsTab({ problems, videoUrl }: { problems: Problem[]; videoUrl?: string }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {problems.length} problem{problems.length !== 1 ? 's' : ''} identified in the content
      </p>
      {problems.map((problem) => (
        <div
          key={problem.problem_id}
          className="p-4 rounded-lg border-l-4 border-l-red-500 bg-red-50 dark:bg-red-900/20"
        >
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-semibold text-red-800 dark:text-red-200">
              {problem.statement}
            </h4>
            {problem.timestamp !== undefined && videoUrl && (
              <a
                href={`${videoUrl}&t=${Math.floor(problem.timestamp)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                ⏱️ {formatTimestamp(problem.timestamp)}
              </a>
            )}
          </div>
          <p className="text-red-700 dark:text-red-300 text-sm mb-3">
            {problem.context}
          </p>
          {problem.blockers.length > 0 && (
            <div>
              <span className="text-xs font-medium text-red-600 dark:text-red-400">Blockers:</span>
              <ul className="mt-1 flex flex-wrap gap-2">
                {problem.blockers.map((blocker, idx) => (
                  <li
                    key={idx}
                    className="text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-1 rounded"
                  >
                    {blocker}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-2 text-xs text-red-500 dark:text-red-500">
            Domain: {problem.domain}
          </div>
        </div>
      ))}
    </div>
  )
}

function TechniquesTab({
  techniques,
  videoUrl,
  expandedId,
  onToggle
}: {
  techniques: Technique[]
  videoUrl?: string
  expandedId: string | null
  onToggle: (id: string | null) => void
}) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {techniques.length} technique{techniques.length !== 1 ? 's' : ''} identified
      </p>
      {techniques.map((technique) => {
        const isExpanded = expandedId === technique.technique_id
        return (
          <div
            key={technique.technique_id}
            className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 overflow-hidden"
          >
            <button
              onClick={() => onToggle(isExpanded ? null : technique.technique_id)}
              className="w-full p-4 text-left flex items-center justify-between hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            >
              <div>
                <h4 className="font-semibold text-blue-800 dark:text-blue-200">
                  {technique.name}
                </h4>
                <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                  {technique.domain}
                  {technique.source && ` • ${technique.source}`}
                </p>
              </div>
              <span className="text-blue-500 dark:text-blue-400">
                {isExpanded ? '▼' : '▶'}
              </span>
            </button>
            {isExpanded && (
              <div className="p-4 pt-0 border-t border-blue-200 dark:border-blue-800 space-y-3">
                <div>
                  <span className="text-xs font-medium text-blue-700 dark:text-blue-300">Principle:</span>
                  <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                    {technique.principle}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-medium text-blue-700 dark:text-blue-300">Implementation:</span>
                  <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                    {technique.implementation}
                  </p>
                </div>
                {technique.requirements.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-blue-700 dark:text-blue-300">Requirements:</span>
                    <ul className="mt-1 flex flex-wrap gap-2">
                      {technique.requirements.map((req, idx) => (
                        <li
                          key={idx}
                          className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-1 rounded"
                        >
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {technique.timestamp !== undefined && videoUrl && (
                  <a
                    href={`${videoUrl}&t=${Math.floor(technique.timestamp)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
                  >
                    ⏱️ Jump to {formatTimestamp(technique.timestamp)}
                  </a>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function ApplicationsTab({
  applications,
  techniques,
  expandedId,
  onToggle
}: {
  applications: CrossDomainApplication[]
  techniques: Technique[]
  expandedId: string | null
  onToggle: (id: string | null) => void
}) {
  // Create a map of technique IDs to names
  const techniqueMap = new Map(techniques.map(t => [t.technique_id, t.name]))

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {applications.length} cross-domain application{applications.length !== 1 ? 's' : ''} suggested
      </p>
      {applications.map((app) => {
        const isExpanded = expandedId === app.application_id
        const sourceTechniqueName = techniqueMap.get(app.source_technique) || app.source_technique

        return (
          <div
            key={app.application_id}
            className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 overflow-hidden"
          >
            <button
              onClick={() => onToggle(isExpanded ? null : app.application_id)}
              className="w-full p-4 text-left flex items-center justify-between hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-green-800 dark:text-green-200">
                    → {app.target_domain}
                  </h4>
                  <ConfidenceBadge confidence={app.confidence} />
                </div>
                <p className="text-sm text-green-700 dark:text-green-300 italic line-clamp-1">
                  &ldquo;{app.hypothesis}&rdquo;
                </p>
              </div>
              <span className="text-green-500 dark:text-green-400 ml-2">
                {isExpanded ? '▼' : '▶'}
              </span>
            </button>
            {isExpanded && (
              <div className="p-4 pt-0 border-t border-green-200 dark:border-green-800 space-y-3">
                <div>
                  <span className="text-xs font-medium text-green-700 dark:text-green-300">Source Technique:</span>
                  <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                    {sourceTechniqueName}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-medium text-green-700 dark:text-green-300">Hypothesis:</span>
                  <p className="text-sm text-green-600 dark:text-green-400 mt-1 italic">
                    &ldquo;{app.hypothesis}&rdquo;
                  </p>
                </div>
                {app.potential_problems_solved.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-green-700 dark:text-green-300">Problems This Could Solve:</span>
                    <ul className="mt-1 space-y-1">
                      {app.potential_problems_solved.map((problem, idx) => (
                        <li
                          key={idx}
                          className="text-sm text-green-600 dark:text-green-400 flex items-start gap-2"
                        >
                          <span className="text-green-400">✓</span>
                          {problem}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {app.adaptation_needed && (
                  <div>
                    <span className="text-xs font-medium text-green-700 dark:text-green-300">Adaptation Needed:</span>
                    <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                      {app.adaptation_needed}
                    </p>
                  </div>
                )}
                {app.similar_existing_work && (
                  <div className="text-xs text-green-500 dark:text-green-500 italic">
                    Prior art: {app.similar_existing_work}
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function ResearchTab({ references, videoUrl }: { references: ResearchReference[]; videoUrl?: string }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {references.length} reference{references.length !== 1 ? 's' : ''} mentioned or implied
      </p>
      {references.map((ref) => (
        <div
          key={ref.reference_id}
          className="p-4 rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20"
        >
          <div className="flex items-start justify-between mb-2">
            <div>
              {ref.title ? (
                <h4 className="font-semibold text-amber-800 dark:text-amber-200">
                  {ref.title}
                </h4>
              ) : (
                <h4 className="font-semibold text-amber-800 dark:text-amber-200 italic">
                  [Untitled Reference]
                </h4>
              )}
              {ref.authors.length > 0 && (
                <p className="text-sm text-amber-600 dark:text-amber-400">
                  {ref.authors.join(', ')}
                  {ref.year && ` (${ref.year})`}
                </p>
              )}
            </div>
            {ref.mentioned_at !== undefined && videoUrl && (
              <a
                href={`${videoUrl}&t=${Math.floor(ref.mentioned_at)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                ⏱️ {formatTimestamp(ref.mentioned_at)}
              </a>
            )}
          </div>
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {ref.relevance}
          </p>
          <div className="mt-2 text-xs text-amber-500 dark:text-amber-500">
            Domain: {ref.domain}
          </div>
        </div>
      ))}
    </div>
  )
}

function ExperimentsTab({
  experiments,
  recommendedReads
}: {
  experiments: ExperimentIdea[]
  recommendedReads: string[]
}) {
  const [expandedExperiment, setExpandedExperiment] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const handleCopyPrompt = async (experimentId: string, prompt: string) => {
    try {
      await navigator.clipboard.writeText(prompt)
      setCopiedId(experimentId)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
      case 'hard':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
    }
  }

  return (
    <div className="space-y-6">
      {/* Experiment Ideas */}
      {experiments.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>🧪</span> Experiment Ideas
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Each experiment includes an optimized LLM prompt you can copy directly to Claude, GPT-4, or other AI assistants
          </p>
          <div className="space-y-4">
            {experiments.map((experiment) => {
              const isExpanded = expandedExperiment === experiment.experiment_id
              const isCopied = copiedId === experiment.experiment_id

              return (
                <div
                  key={experiment.experiment_id}
                  className="rounded-lg border border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20 overflow-hidden"
                >
                  {/* Header - Always visible */}
                  <button
                    onClick={() => setExpandedExperiment(isExpanded ? null : experiment.experiment_id)}
                    className="w-full p-4 text-left flex items-start justify-between hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <h4 className="font-semibold text-purple-800 dark:text-purple-200">
                          {experiment.title}
                        </h4>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getDifficultyColor(experiment.difficulty)}`}>
                          {experiment.difficulty}
                        </span>
                        {experiment.time_estimate && (
                          <span className="text-xs text-purple-600 dark:text-purple-400">
                            ⏱️ {experiment.time_estimate}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-purple-700 dark:text-purple-300 line-clamp-2">
                        {experiment.description}
                      </p>
                    </div>
                    <span className="text-purple-500 dark:text-purple-400 ml-2 mt-1">
                      {isExpanded ? '▼' : '▶'}
                    </span>
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-purple-200 dark:border-purple-800">
                      {/* Prerequisites & Success Criteria */}
                      {(experiment.prerequisites.length > 0 || experiment.success_criteria.length > 0) && (
                        <div className="p-4 grid md:grid-cols-2 gap-4">
                          {experiment.prerequisites.length > 0 && (
                            <div>
                              <span className="text-xs font-medium text-purple-700 dark:text-purple-300">Prerequisites:</span>
                              <ul className="mt-1 space-y-1">
                                {experiment.prerequisites.map((prereq, idx) => (
                                  <li key={idx} className="text-sm text-purple-600 dark:text-purple-400 flex items-start gap-2">
                                    <span className="text-purple-400">•</span>
                                    {prereq}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {experiment.success_criteria.length > 0 && (
                            <div>
                              <span className="text-xs font-medium text-purple-700 dark:text-purple-300">Success Criteria:</span>
                              <ul className="mt-1 space-y-1">
                                {experiment.success_criteria.map((criteria, idx) => (
                                  <li key={idx} className="text-sm text-purple-600 dark:text-purple-400 flex items-start gap-2">
                                    <span className="text-green-500">✓</span>
                                    {criteria}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}

                      {/* LLM Prompt Section */}
                      <div className="p-4 bg-gray-900 dark:bg-gray-950">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-400 flex items-center gap-2">
                            <span>🤖</span> Copy-Pasteable LLM Prompt
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleCopyPrompt(experiment.experiment_id, experiment.llm_prompt)
                            }}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium transition-all ${
                              isCopied
                                ? 'bg-green-600 text-white'
                                : 'bg-purple-600 hover:bg-purple-700 text-white'
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
                                Copy Prompt
                              </>
                            )}
                          </button>
                        </div>
                        <div className="relative">
                          <pre className="text-xs text-gray-300 bg-gray-800 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto max-h-96 whitespace-pre-wrap font-mono">
                            {experiment.llm_prompt}
                          </pre>
                        </div>
                      </div>

                      {/* Related Items */}
                      {(experiment.related_techniques.length > 0 || experiment.related_problems.length > 0) && (
                        <div className="p-4 pt-0 flex flex-wrap gap-2">
                          {experiment.related_techniques.map((tech, idx) => (
                            <span key={`tech-${idx}`} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-1 rounded">
                              🔧 {tech}
                            </span>
                          ))}
                          {experiment.related_problems.map((prob, idx) => (
                            <span key={`prob-${idx}`} className="text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-1 rounded">
                              🎯 {prob}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommended Reading */}
      {recommendedReads.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <span>📖</span> Recommended Reading
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Suggested follow-up research and resources
          </p>
          <ul className="space-y-2">
            {recommendedReads.map((read, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 text-gray-700 dark:text-gray-300"
              >
                <span className="text-indigo-500 mt-0.5">📄</span>
                {read}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
