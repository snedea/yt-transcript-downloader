'use client'

import React from 'react'
import type { AnalysisMode, AnalysisProgress } from '@/types'

interface AnalysisModeSelectorProps {
  mode: AnalysisMode
  onChange: (mode: AnalysisMode) => void
  disabled?: boolean
  showEstimates?: boolean
  wordCount?: number
}

const MODE_INFO: Record<AnalysisMode, {
  label: string
  description: string
  estimate: string
  icon: string
  features: string[]
}> = {
  quick: {
    label: 'Quick Analysis',
    description: 'Fast overview with key insights',
    estimate: '~15 seconds',
    icon: '⚡',
    features: [
      '5 dimension scores',
      'Top concerns & strengths',
      'Manipulation technique detection',
      'Executive summary'
    ]
  },
  deep: {
    label: 'Deep Analysis',
    description: 'Comprehensive multi-pass analysis',
    estimate: '~60 seconds',
    icon: '🔬',
    features: [
      'Everything in Quick, plus:',
      'Claim extraction & verification',
      'Segment-level annotations',
      'Detailed technique breakdown',
      'Dual interpretations'
    ]
  }
}

export function AnalysisModeSelector({
  mode,
  onChange,
  disabled = false,
  showEstimates = true,
  wordCount
}: AnalysisModeSelectorProps) {
  const getEstimate = (m: AnalysisMode): string => {
    if (m === 'quick') {
      return MODE_INFO.quick.estimate
    }
    if (wordCount) {
      const baseSeconds = 45
      const perThousandWords = 15
      const estimatedSeconds = baseSeconds + Math.floor(wordCount / 1000) * perThousandWords
      if (estimatedSeconds < 60) {
        return `~${estimatedSeconds}s`
      }
      return `~${Math.ceil(estimatedSeconds / 60)}min`
    }
    return MODE_INFO.deep.estimate
  }

  return (
    <div className="flex gap-3">
      {(['quick', 'deep'] as AnalysisMode[]).map((m) => {
        const info = MODE_INFO[m]
        const isSelected = mode === m

        return (
          <button
            key={m}
            type="button"
            onClick={() => onChange(m)}
            disabled={disabled}
            className={`
              flex-1 p-4 rounded-lg border-2 text-left transition-all
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
              ${isSelected
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-indigo-300 dark:hover:border-indigo-700'
              }
            `}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{info.icon}</span>
              <span className={`font-semibold ${isSelected ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-800 dark:text-gray-200'}`}>
                {info.label}
              </span>
              {isSelected && (
                <svg className="w-5 h-5 text-indigo-600 dark:text-indigo-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {info.description}
            </p>

            {showEstimates && (
              <div className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {getEstimate(m)}
              </div>
            )}

            {/* Feature list on hover/focus */}
            <div className="mt-3 space-y-1 text-xs text-gray-500 dark:text-gray-500">
              {info.features.map((feature, idx) => (
                <div key={idx} className="flex items-center gap-1.5">
                  <svg className="w-3 h-3 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </button>
        )
      })}
    </div>
  )
}

interface AnalysisProgressBarProps {
  progress: AnalysisProgress
}

export function AnalysisProgressBar({ progress }: AnalysisProgressBarProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-700 dark:text-gray-300 font-medium">
          {progress.phase_name}
        </span>
        <span className="text-gray-500 dark:text-gray-400">
          {progress.progress}%
        </span>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className="h-2 rounded-full bg-indigo-500 transition-all duration-500"
          style={{ width: `${progress.progress}%` }}
        />
      </div>

      {progress.message && (
        <p className="text-xs text-gray-500 dark:text-gray-500">
          {progress.message}
        </p>
      )}
    </div>
  )
}

// Compact inline mode selector for use in headers/toolbars
interface CompactModeSelectorProps {
  mode: AnalysisMode
  onChange: (mode: AnalysisMode) => void
  disabled?: boolean
}

export function CompactModeSelector({
  mode,
  onChange,
  disabled = false
}: CompactModeSelectorProps) {
  return (
    <div className="inline-flex rounded-lg bg-gray-100 dark:bg-gray-700 p-1">
      {(['quick', 'deep'] as AnalysisMode[]).map((m) => {
        const isSelected = mode === m
        return (
          <button
            key={m}
            type="button"
            onClick={() => onChange(m)}
            disabled={disabled}
            className={`
              px-3 py-1.5 text-sm font-medium rounded-md transition-all
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              ${isSelected
                ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }
            `}
          >
            {m === 'quick' ? '⚡ Quick' : '🔬 Deep'}
          </button>
        )
      })}
    </div>
  )
}
