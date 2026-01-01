'use client'

import React, { useState } from 'react'
import type { DimensionScore, DimensionType } from '@/types'

// Dimension metadata
const DIMENSION_META: Record<DimensionType, {
  name: string
  icon: string
  color: string
  description: string
}> = {
  epistemic_integrity: {
    name: 'Epistemic Integrity',
    icon: '🔍',
    color: '#3b82f6', // blue
    description: 'Measures scholarly rigor, uncertainty acknowledgment, and evidence quality'
  },
  argument_quality: {
    name: 'Argument Quality',
    icon: '🧠',
    color: '#8b5cf6', // purple
    description: 'Evaluates logical coherence, claim-evidence fit, and reasoning validity'
  },
  manipulation_risk: {
    name: 'Manipulation Risk',
    icon: '⚠️',
    color: '#ef4444', // red
    description: 'Detects coercive persuasion, fear appeals, and identity capture (inverted: high = safe)'
  },
  rhetorical_craft: {
    name: 'Rhetorical Craft',
    icon: '🎭',
    color: '#f59e0b', // amber
    description: 'Assesses stylistic effectiveness without value judgment'
  },
  fairness_balance: {
    name: 'Fairness & Balance',
    icon: '⚖️',
    color: '#22c55e', // green
    description: 'Measures even-handedness, counterarguments, and consistent standards'
  }
}

// Ordered dimensions for display
const DIMENSION_ORDER: DimensionType[] = [
  'epistemic_integrity',
  'argument_quality',
  'manipulation_risk',
  'rhetorical_craft',
  'fairness_balance'
]

interface DimensionScoresProps {
  scores: Record<DimensionType, DimensionScore>
  variant?: 'cards' | 'bars' | 'compact'
}

export function DimensionScores({ scores, variant = 'cards' }: DimensionScoresProps) {
  const [expandedDimension, setExpandedDimension] = useState<DimensionType | null>(null)

  if (variant === 'bars') {
    return <DimensionBars scores={scores} />
  }

  if (variant === 'compact') {
    return <DimensionCompact scores={scores} />
  }

  return (
    <div className="space-y-4">
      {DIMENSION_ORDER.map((dimensionId) => {
        const score = scores[dimensionId]
        if (!score) return null

        const meta = DIMENSION_META[dimensionId]
        const isExpanded = expandedDimension === dimensionId

        return (
          <DimensionCard
            key={dimensionId}
            dimensionId={dimensionId}
            score={score}
            meta={meta}
            isExpanded={isExpanded}
            onToggle={() => setExpandedDimension(isExpanded ? null : dimensionId)}
          />
        )
      })}
    </div>
  )
}

interface DimensionCardProps {
  dimensionId: DimensionType
  score: DimensionScore
  meta: typeof DIMENSION_META[DimensionType]
  isExpanded: boolean
  onToggle: () => void
}

function DimensionCard({ dimensionId, score, meta, isExpanded, onToggle }: DimensionCardProps) {
  const getScoreColor = (s: number): string => {
    if (s >= 80) return 'text-green-600 dark:text-green-400'
    if (s >= 60) return 'text-yellow-600 dark:text-yellow-400'
    if (s >= 40) return 'text-orange-600 dark:text-orange-400'
    return 'text-red-600 dark:text-red-400'
  }

  return (
    <div
      className={`
        p-4 rounded-lg border-2 transition-all bg-white dark:bg-gray-800
        ${isExpanded ? 'border-indigo-300 dark:border-indigo-600 shadow-md' : 'border-gray-200 dark:border-gray-700'}
      `}
      style={{ borderLeftColor: meta.color, borderLeftWidth: '4px' }}
    >
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{meta.icon}</span>
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">
              {meta.name}
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              {meta.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className={`text-2xl font-bold ${getScoreColor(score.score)}`}>
              {score.score}
            </span>
            <span className="text-sm text-gray-400">/100</span>
          </div>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Progress bar */}
      <div className="mt-3 w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-500"
          style={{ width: `${score.score}%`, backgroundColor: meta.color }}
        />
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mt-4 space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          {/* Explanation */}
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {score.explanation}
          </p>

          {/* Red/Green flags */}
          <div className="grid grid-cols-2 gap-4">
            {/* Concerns */}
            {(score.red_flags?.length ?? 0) > 0 && (
              <div>
                <h5 className="text-xs font-medium text-red-600 dark:text-red-400 mb-2 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Concerns
                </h5>
                <ul className="space-y-1">
                  {score.red_flags?.map((flag, idx) => (
                    <li key={idx} className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-1.5">
                      <span className="text-red-400 mt-0.5">•</span>
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Strengths - backend sends 'strengths', fallback to 'green_flags' */}
            {((score.strengths?.length ?? 0) > 0 || (score.green_flags?.length ?? 0) > 0) && (
              <div>
                <h5 className="text-xs font-medium text-green-600 dark:text-green-400 mb-2 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Strengths
                </h5>
                <ul className="space-y-1">
                  {(score.strengths || score.green_flags || []).map((flag, idx) => (
                    <li key={idx} className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-1.5">
                      <span className="text-green-400 mt-0.5">•</span>
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Key examples */}
          {(score.key_examples?.length ?? 0) > 0 && (
            <div>
              <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Key Examples
              </h5>
              <div className="space-y-2">
                {(score.key_examples || []).slice(0, 3).map((example, idx) => (
                  <p key={idx} className="text-xs text-gray-600 dark:text-gray-400 italic bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    &ldquo;{example}&rdquo;
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Confidence */}
          <div className="text-xs text-gray-400 dark:text-gray-500">
            Analysis confidence: {Math.round((score.confidence ?? 0.8) * 100)}%
          </div>
        </div>
      )}
    </div>
  )
}

// Simple bar chart variant
function DimensionBars({ scores }: { scores: Record<DimensionType, DimensionScore> }) {
  return (
    <div className="space-y-3">
      {DIMENSION_ORDER.map((dimensionId) => {
        const score = scores[dimensionId]
        if (!score) return null

        const meta = DIMENSION_META[dimensionId]

        return (
          <div key={dimensionId} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <span>{meta.icon}</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{meta.name}</span>
              </span>
              <span className="font-bold" style={{ color: meta.color }}>
                {score.score}/100
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-500"
                style={{ width: `${score.score}%`, backgroundColor: meta.color }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Compact inline variant
function DimensionCompact({ scores }: { scores: Record<DimensionType, DimensionScore> }) {
  return (
    <div className="flex flex-wrap gap-2">
      {DIMENSION_ORDER.map((dimensionId) => {
        const score = scores[dimensionId]
        if (!score) return null

        const meta = DIMENSION_META[dimensionId]

        return (
          <div
            key={dimensionId}
            className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs"
            style={{ backgroundColor: meta.color + '20', color: meta.color }}
          >
            <span>{meta.icon}</span>
            <span className="font-medium">{score.score}</span>
          </div>
        )
      })}
    </div>
  )
}

// Radar/Spider chart for dimensions
interface DimensionRadarProps {
  scores: Record<DimensionType, DimensionScore>
  size?: number
}

export function DimensionRadar({ scores, size = 300 }: DimensionRadarProps) {
  const center = size / 2
  const radius = size * 0.4
  const angleStep = (2 * Math.PI) / DIMENSION_ORDER.length

  // Calculate polygon points for scores
  const scorePoints = DIMENSION_ORDER.map((dimensionId, i) => {
    const score = scores[dimensionId]?.score ?? 0
    const angle = i * angleStep - Math.PI / 2 // Start from top
    const r = (score / 100) * radius
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle)
    }
  })

  // Background grid points (100%, 75%, 50%, 25%)
  const gridLevels = [100, 75, 50, 25]

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="overflow-visible">
        {/* Background grid circles */}
        {gridLevels.map((level) => {
          const r = (level / 100) * radius
          return (
            <circle
              key={level}
              cx={center}
              cy={center}
              r={r}
              fill="none"
              stroke="currentColor"
              strokeOpacity={0.1}
              className="text-gray-400 dark:text-gray-600"
            />
          )
        })}

        {/* Axis lines */}
        {DIMENSION_ORDER.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2
          const x2 = center + radius * Math.cos(angle)
          const y2 = center + radius * Math.sin(angle)
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="currentColor"
              strokeOpacity={0.1}
              className="text-gray-400 dark:text-gray-600"
            />
          )
        })}

        {/* Score polygon */}
        <polygon
          points={scorePoints.map(p => `${p.x},${p.y}`).join(' ')}
          fill="#6366f1"
          fillOpacity={0.3}
          stroke="#6366f1"
          strokeWidth={2}
        />

        {/* Score points */}
        {scorePoints.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={4}
            fill="#6366f1"
            stroke="white"
            strokeWidth={2}
          />
        ))}

        {/* Labels */}
        {DIMENSION_ORDER.map((dimensionId, i) => {
          const meta = DIMENSION_META[dimensionId]
          const angle = i * angleStep - Math.PI / 2
          const labelRadius = radius + 30
          const x = center + labelRadius * Math.cos(angle)
          const y = center + labelRadius * Math.sin(angle)

          return (
            <g key={dimensionId}>
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-xs font-medium fill-gray-700 dark:fill-gray-300"
              >
                {meta.icon}
              </text>
            </g>
          )
        })}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-3 mt-4">
        {DIMENSION_ORDER.map((dimensionId) => {
          const meta = DIMENSION_META[dimensionId]
          const score = scores[dimensionId]

          return (
            <div key={dimensionId} className="flex items-center gap-1 text-xs">
              <span>{meta.icon}</span>
              <span className="text-gray-600 dark:text-gray-400">{meta.name.split(' ')[0]}</span>
              <span className="font-bold" style={{ color: meta.color }}>
                {score?.score ?? '-'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
