'use client'

import React, { useState, useRef } from 'react'
import type { ManipulationAnalysisResult, DimensionType } from '@/types'
import { ScoreGauge } from './ScoreGauge'
import { DimensionScores, DimensionRadar } from './DimensionScores'
import { ClaimsPanel, ClaimsSummary } from './ClaimsPanel'
import { TechniqueList } from './TechniqueList'
import { QuoteAnalysis } from './QuoteAnalysis'

interface ManipulationAnalysisProps {
  result: ManipulationAnalysisResult
  videoTitle?: string
  videoAuthor?: string
  isCached?: boolean
  analysisDate?: string
}

type TabType = 'overview' | 'dimensions' | 'claims' | 'devices' | 'summary'

// Dimension colors for display
const DIMENSION_COLORS: Record<DimensionType, string> = {
  epistemic_integrity: '#3b82f6',
  argument_quality: '#8b5cf6',
  manipulation_risk: '#ef4444',
  rhetorical_craft: '#f59e0b',
  fairness_balance: '#22c55e'
}

export function ManipulationAnalysis({
  result,
  videoTitle,
  videoAuthor,
  isCached,
  analysisDate
}: ManipulationAnalysisProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const reportRef = useRef<HTMLDivElement>(null)

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'dimensions', label: 'Dimensions', icon: '🎯' },
    { id: 'claims', label: 'Claims', icon: '📝' },
    { id: 'devices', label: 'Devices', icon: '⚠️' },
    { id: 'summary', label: 'Summary', icon: '📋' }
  ]

  // Calculate average dimension score for display
  const avgDimensionScore = result.dimension_scores
    ? Math.round(
        Object.values(result.dimension_scores).reduce((sum, d) => sum + d.score, 0) /
        Object.values(result.dimension_scores).length
      )
    : result.overall_score

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden" ref={reportRef}>
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-700 dark:to-purple-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-2xl font-bold">Content Trust Analysis</h2>
              <span className={`text-xs px-2 py-1 rounded-full ${
                result.analysis_mode === 'deep'
                  ? 'bg-purple-400/30 text-purple-100'
                  : 'bg-indigo-400/30 text-indigo-100'
              }`}>
                {result.analysis_mode === 'deep' ? '🔬 Deep' : '⚡ Quick'} Analysis
              </span>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached
                </span>
              )}
            </div>
            {videoTitle && (
              <p className="text-indigo-100 text-sm">{videoTitle}</p>
            )}
            {videoAuthor && (
              <p className="text-indigo-200 text-xs mt-1">by {videoAuthor}</p>
            )}
            {isCached && analysisDate && (
              <p className="text-indigo-200 text-xs mt-1">
                Analyzed on {new Date(analysisDate).toLocaleDateString()}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold">{result.overall_score}</div>
            <div className="text-xl font-semibold text-indigo-200">{result.overall_grade}</div>
            <div className="text-xs text-indigo-300 mt-1">
              {result.overall_score >= 80 ? '✓ Highly Trustworthy' :
               result.overall_score >= 60 ? '~ Moderately Trustworthy' :
               result.overall_score >= 40 ? '⚠ Some Concerns' :
               '⚠ Significant Concerns'}
            </div>
          </div>
        </div>

        {/* Quick Dimension Scores */}
        {result.dimension_scores && (
          <div className="grid grid-cols-5 gap-2 mt-6">
            {(Object.entries(result.dimension_scores) as [DimensionType, typeof result.dimension_scores[DimensionType]][]).map(([key, dim]) => (
              <div
                key={key}
                className="text-center p-2 rounded-lg bg-white/10"
              >
                <div className="text-lg font-bold">{dim.score}</div>
                <div className="text-xs text-indigo-200 truncate" title={dim.dimension_name}>
                  {dim.dimension_name.split(' ')[0]}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.total_claims || 0}</div>
            <div className="text-xs text-indigo-200">Claims Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.verified_claims_count || 0}</div>
            <div className="text-xs text-indigo-200">Claims Verified</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.most_used_devices?.length || 0}</div>
            <div className="text-xs text-indigo-200">Devices Detected</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.transcript_word_count}</div>
            <div className="text-xs text-indigo-200">Words Analyzed</div>
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
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab result={result} />
        )}
        {activeTab === 'dimensions' && (
          <DimensionsTab result={result} />
        )}
        {activeTab === 'claims' && (
          <ClaimsTab result={result} />
        )}
        {activeTab === 'devices' && (
          <DevicesTab result={result} />
        )}
        {activeTab === 'summary' && (
          <SummaryTab result={result} />
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {result.analysis_mode === 'deep' ? 'Deep' : 'Quick'} analysis completed in {result.analysis_duration_seconds}s | {result.tokens_used} tokens used | v{result.analysis_version}
        </div>
      </div>
    </div>
  )
}

// Tab Components
function OverviewTab({ result }: { result: ManipulationAnalysisResult }) {
  return (
    <div className="space-y-8">
      {/* Score and Radar */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="flex flex-col items-center">
          <ScoreGauge
            score={result.overall_score}
            grade={result.overall_grade}
            label="Trust Score"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center max-w-xs">
            Higher = more trustworthy, less manipulation detected.<br/>
            Lower = more manipulation concerns found.
          </p>
        </div>
        <div className="flex justify-center">
          {result.dimension_scores && (
            <DimensionRadar scores={result.dimension_scores} size={280} />
          )}
        </div>
      </div>

      {/* Top Concerns & Strengths */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Concerns */}
        {result.top_concerns && result.top_concerns.length > 0 && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
            <h3 className="font-semibold text-red-800 dark:text-red-200 mb-3 flex items-center gap-2">
              <span>⚠️</span> Top Concerns
            </h3>
            <ul className="space-y-2">
              {result.top_concerns.map((concern, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-red-700 dark:text-red-300">
                  <span className="text-red-400 mt-0.5">•</span>
                  {concern}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Strengths */}
        {result.top_strengths && result.top_strengths.length > 0 && (
          <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
            <h3 className="font-semibold text-green-800 dark:text-green-200 mb-3 flex items-center gap-2">
              <span>✓</span> Key Strengths
            </h3>
            <ul className="space-y-2">
              {result.top_strengths.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-green-700 dark:text-green-300">
                  <span className="text-green-400 mt-0.5">•</span>
                  {strength}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Dual Interpretations */}
      {(result.charitable_interpretation || result.concerning_interpretation) && (
        <div className="grid md:grid-cols-2 gap-6">
          {result.charitable_interpretation && (
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2 flex items-center gap-2">
                <span>💙</span> Charitable Interpretation
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {result.charitable_interpretation}
              </p>
            </div>
          )}
          {result.concerning_interpretation && (
            <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
              <h4 className="font-medium text-amber-800 dark:text-amber-200 mb-2 flex items-center gap-2">
                <span>⚡</span> Critical Interpretation
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-300">
                {result.concerning_interpretation}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function DimensionsTab({ result }: { result: ManipulationAnalysisResult }) {
  if (!result.dimension_scores) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>Dimension scores not available for this analysis.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          5-Dimension Analysis
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Each dimension scores how trustworthy and well-reasoned the content is
        </p>
      </div>
      <DimensionScores scores={result.dimension_scores} variant="cards" />
    </div>
  )
}

function ClaimsTab({ result }: { result: ManipulationAnalysisResult }) {
  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          Detected Claims
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {result.total_claims || 0} claims extracted
          {result.verified_claims_count ? `, ${result.verified_claims_count} verified via web search` : ''}
        </p>
      </div>
      <ClaimsPanel
        claims={result.detected_claims || []}
        verifiedClaims={result.verified_claims}
      />
    </div>
  )
}

function DevicesTab({ result }: { result: ManipulationAnalysisResult }) {
  // Show manipulation devices (from most_used_devices) or fallback to technique_matches
  const hasDevices = result.most_used_devices && result.most_used_devices.length > 0
  const hasTechniques = result.technique_matches && result.technique_matches.length > 0

  if (!hasDevices && !hasTechniques) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <span className="text-4xl mb-2 block">🔍</span>
        <p>No manipulation devices detected.</p>
        <p className="text-sm mt-1">This content appears to use straightforward communication.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Most Used Devices Summary */}
      {hasDevices && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Most Used Manipulation Devices
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {result.most_used_devices!.map((device, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-l-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 ${
                  device.severity === 'high'
                    ? 'border-l-red-500'
                    : device.severity === 'medium'
                    ? 'border-l-yellow-500'
                    : 'border-l-gray-400'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-800 dark:text-gray-200">
                    {device.device_name}
                  </h4>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      device.severity === 'high'
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                        : device.severity === 'medium'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                    }`}>
                      {device.severity}
                    </span>
                    <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                      {device.count}x
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 capitalize">
                  {device.category}
                </span>
                {device.example && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 italic mt-2">
                    &ldquo;{device.example}&rdquo;
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback to legacy technique matches */}
      {hasTechniques && result.technique_summary && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Rhetorical Techniques ({result.technique_matches!.length})
          </h3>
          <TechniqueList
            techniques={result.technique_matches!}
            summary={result.technique_summary}
          />
        </div>
      )}
    </div>
  )
}

function SummaryTab({ result }: { result: ManipulationAnalysisResult }) {
  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">Executive Summary</h3>
        <div className="prose prose-sm dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
          {result.executive_summary.split('\n').map((paragraph, idx) => (
            <p key={idx} className="mb-3">{paragraph}</p>
          ))}
        </div>
      </div>

      {/* Claims Summary */}
      {result.detected_claims && result.detected_claims.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">Claims Overview</h3>
          <ClaimsSummary claims={result.detected_claims} />
        </div>
      )}

      {/* Dual Interpretations */}
      {(result.charitable_interpretation || result.concerning_interpretation) && (
        <div className="grid md:grid-cols-2 gap-6">
          {result.charitable_interpretation && (
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20">
              <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                💙 Charitable Reading
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {result.charitable_interpretation}
              </p>
            </div>
          )}
          {result.concerning_interpretation && (
            <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20">
              <h4 className="font-medium text-amber-800 dark:text-amber-200 mb-2">
                ⚡ Critical Reading
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-300">
                {result.concerning_interpretation}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Key Takeaways */}
      <div className="grid md:grid-cols-2 gap-6">
        {result.top_strengths && result.top_strengths.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
              <span className="text-green-500">✓</span> Key Strengths
            </h3>
            <ul className="space-y-2">
              {result.top_strengths.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700 dark:text-gray-300">{strength}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.top_concerns && result.top_concerns.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
              <span className="text-amber-500">!</span> Areas of Concern
            </h3>
            <ul className="space-y-2">
              {result.top_concerns.map((concern, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700 dark:text-gray-300">{concern}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
