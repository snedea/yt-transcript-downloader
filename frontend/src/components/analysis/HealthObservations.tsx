'use client'

import React, { useState } from 'react'
import type {
  HealthObservationResult,
  HealthObservation,
  BodyRegion,
  ObservationSeverity
} from '@/types'

interface HealthObservationsProps {
  result: HealthObservationResult
  videoTitle?: string
  videoUrl?: string
  isCached?: boolean
  onReanalyze?: () => void
  isReanalyzing?: boolean
}

type TabType = 'overview' | 'eyes' | 'face' | 'skin' | 'hands' | 'neck' | 'posture' | 'other'

// Body region display configuration
const BODY_REGION_INFO: Record<BodyRegion, { label: string; icon: string; color: string }> = {
  eyes: { label: 'Eyes', icon: '👁️', color: 'bg-blue-500' },
  face: { label: 'Face', icon: '👤', color: 'bg-purple-500' },
  skin: { label: 'Skin', icon: '🖐️', color: 'bg-orange-500' },
  hands: { label: 'Hands', icon: '✋', color: 'bg-green-500' },
  neck: { label: 'Neck', icon: '🦒', color: 'bg-pink-500' },
  posture: { label: 'Posture', icon: '🚶', color: 'bg-indigo-500' },
  other: { label: 'Other', icon: '📍', color: 'bg-gray-500' }
}

// Severity display configuration
const SEVERITY_INFO: Record<ObservationSeverity, { label: string; icon: string; color: string; bgColor: string }> = {
  informational: {
    label: 'Informational',
    icon: 'ℹ️',
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30'
  },
  worth_mentioning: {
    label: 'Worth Mentioning',
    icon: '💬',
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/30'
  },
  consider_checkup: {
    label: 'Consider Checkup',
    icon: '⚕️',
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-100 dark:bg-orange-900/30'
  }
}

function formatTimestamp(seconds: number): string {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100)
  let color = 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'

  if (percentage >= 70) {
    color = 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  } else if (percentage >= 50) {
    color = 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  } else {
    color = 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  }

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${color}`}>
      {percentage}% confidence
    </span>
  )
}

function ObservationCard({
  observation,
  videoUrl
}: {
  observation: HealthObservation
  videoUrl: string
}) {
  const [expanded, setExpanded] = useState(false)
  const regionInfo = BODY_REGION_INFO[observation.body_region]
  const severityInfo = SEVERITY_INFO[observation.severity]

  // Build YouTube URL with timestamp
  const timestampUrl = `${videoUrl}&t=${Math.floor(observation.timestamp)}s`

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-3">
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`${regionInfo.color} text-white text-xs px-2 py-0.5 rounded`}>
            {regionInfo.icon} {regionInfo.label}
          </span>
          <a
            href={timestampUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            @ {formatTimestamp(observation.timestamp)}
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
        <div className="flex items-center gap-2">
          <ConfidenceBadge confidence={observation.confidence} />
          <span className={`${severityInfo.bgColor} ${severityInfo.color} text-xs px-2 py-0.5 rounded-full`}>
            {severityInfo.icon} {severityInfo.label}
          </span>
        </div>
      </div>

      {/* Observation text */}
      <p className="text-gray-800 dark:text-gray-200 font-medium mb-2">
        {observation.observation}
      </p>

      {/* Reasoning */}
      {observation.reasoning && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span className="font-medium">Why notable:</span> {observation.reasoning}
        </p>
      )}

      {/* Expandable details */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
      >
        {expanded ? 'Hide details' : 'Show details'}
        <svg className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-3">
          {/* Limitations */}
          {observation.limitations.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Limitations:</p>
              <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc list-inside">
                {observation.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Related conditions (educational) */}
          {observation.related_conditions.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Related (educational context only):
              </p>
              <div className="flex flex-wrap gap-1">
                {observation.related_conditions.map((cond, idx) => (
                  <span key={idx} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded">
                    {cond}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* References */}
          {observation.references.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">References:</p>
              <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc list-inside">
                {observation.references.map((ref, idx) => (
                  <li key={idx}>{ref}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function HealthObservations({
  result,
  videoTitle,
  videoUrl,
  isCached,
  onReanalyze,
  isReanalyzing
}: HealthObservationsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [disclaimerExpanded, setDisclaimerExpanded] = useState(false)

  // Build video URL if not provided
  const fullVideoUrl = videoUrl || `https://www.youtube.com/watch?v=${result.video_id}`

  // Get counts by region
  const regionCounts = Object.entries(result.observations_by_region).reduce((acc, [region, obs]) => {
    acc[region as BodyRegion] = obs.length
    return acc
  }, {} as Record<BodyRegion, number>)

  // Build tabs dynamically based on available regions
  const tabs: { id: TabType; label: string; icon: string; count?: number }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' }
  ]

  // Add tabs for each body region that has observations
  const regionOrder: BodyRegion[] = ['eyes', 'face', 'skin', 'hands', 'neck', 'posture', 'other']
  regionOrder.forEach(region => {
    const count = regionCounts[region] || 0
    if (count > 0) {
      const info = BODY_REGION_INFO[region]
      tabs.push({ id: region as TabType, label: info.label, icon: info.icon, count })
    }
  })

  // Render observations for a specific region
  const renderRegionObservations = (region: BodyRegion) => {
    const observations = result.observations_by_region[region] || []
    if (observations.length === 0) {
      return (
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          No observations for this body region.
        </p>
      )
    }
    return observations.map(obs => (
      <ObservationCard key={obs.observation_id} observation={obs} videoUrl={fullVideoUrl} />
    ))
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header with Warning */}
      <div className="bg-gradient-to-r from-rose-600 to-pink-600 dark:from-rose-700 dark:to-pink-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold">Health Observations</h2>
              <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                v0.1 BETA
              </span>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached
                </span>
              )}
            </div>

            {/* Prominent Warning */}
            <div className="bg-white/10 rounded-lg p-3 mb-3">
              <p className="text-sm font-medium flex items-center gap-2">
                <span className="text-xl">⚠️</span>
                EDUCATIONAL TOOL ONLY - NOT MEDICAL ADVICE
              </p>
              <p className="text-xs text-rose-200 mt-1">
                This tool identifies visual observations that MAY warrant professional evaluation.
                Always consult a healthcare provider for medical concerns.
              </p>
            </div>

            {videoTitle && (
              <p className="text-rose-200 text-sm">{videoTitle}</p>
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
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.frames_extracted}</div>
            <div className="text-xs text-rose-200">Frames Extracted</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.frames_with_humans}</div>
            <div className="text-xs text-rose-200">With Humans</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.frames_analyzed}</div>
            <div className="text-xs text-rose-200">Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.observations.length}</div>
            <div className="text-xs text-rose-200">Observations</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-rose-500 text-rose-600 dark:text-rose-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs px-2 py-0.5 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' ? (
          <div className="space-y-6">
            {/* Summary */}
            <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">Summary</h3>
              <p className="text-gray-700 dark:text-gray-300">{result.summary}</p>
            </div>

            {/* All Observations */}
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white mb-3">
                All Observations ({result.observations.length})
              </h3>
              {result.observations.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No health-related observations were found in this video.
                </p>
              ) : (
                result.observations.map(obs => (
                  <ObservationCard key={obs.observation_id} observation={obs} videoUrl={fullVideoUrl} />
                ))
              )}
            </div>

            {/* Limitations */}
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">General Limitations</h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 list-disc list-inside space-y-1">
                {result.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>

            {/* Full Disclaimer (collapsible) */}
            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <button
                onClick={() => setDisclaimerExpanded(!disclaimerExpanded)}
                className="w-full flex items-center justify-between text-left"
              >
                <span className="font-medium text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  <span>📋</span> Full Disclaimer
                </span>
                <svg className={`w-5 h-5 text-amber-600 transition-transform ${disclaimerExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {disclaimerExpanded && (
                <div className="mt-3 pt-3 border-t border-amber-200 dark:border-amber-800">
                  <p className="text-sm text-amber-900 dark:text-amber-100 whitespace-pre-wrap">
                    {result.disclaimer}
                  </p>
                </div>
              )}
            </div>

            {/* Metadata */}
            <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-4">
              <span>Analysis completed in {result.analysis_duration_seconds.toFixed(1)}s</span>
              <span>Frame interval: {result.interval_seconds}s</span>
              <span>Model: {result.model_used}</span>
            </div>
          </div>
        ) : (
          // Render region-specific tab content
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <span>{BODY_REGION_INFO[activeTab as BodyRegion]?.icon}</span>
              {BODY_REGION_INFO[activeTab as BodyRegion]?.label} Observations
            </h3>
            {renderRegionObservations(activeTab as BodyRegion)}
          </div>
        )}
      </div>
    </div>
  )
}

export default HealthObservations
