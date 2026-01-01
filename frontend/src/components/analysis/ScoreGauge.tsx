'use client'

import React from 'react'
import type { LetterGrade } from '@/types'

interface ScoreGaugeProps {
  score: number
  grade: LetterGrade
  label?: string
}

export function ScoreGauge({ score, grade, label = 'Overall Score' }: ScoreGaugeProps) {
  // Calculate color based on score
  const getScoreColor = (score: number): string => {
    if (score >= 90) return '#22c55e' // green-500
    if (score >= 80) return '#84cc16' // lime-500
    if (score >= 70) return '#eab308' // yellow-500
    if (score >= 60) return '#f97316' // orange-500
    return '#ef4444' // red-500
  }

  const color = getScoreColor(score)

  // SVG circle parameters
  const size = 180
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const dashOffset = circumference - progress

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background circle */}
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{
              transition: 'stroke-dashoffset 1s ease-out, stroke 0.3s ease'
            }}
          />
        </svg>

        {/* Score text in center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-4xl font-bold"
            style={{ color }}
          >
            {score}
          </span>
          <span
            className="text-2xl font-semibold mt-1"
            style={{ color }}
          >
            {grade}
          </span>
        </div>
      </div>

      {label && (
        <p className="mt-2 text-sm text-gray-600 font-medium">{label}</p>
      )}
    </div>
  )
}

interface MiniScoreProps {
  score: number
  label: string
  color?: string
}

export function MiniScore({ score, label, color }: MiniScoreProps) {
  const defaultColor = score >= 70 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444'
  const displayColor = color || defaultColor

  return (
    <div className="flex flex-col items-center p-3 bg-gray-50 rounded-lg">
      <span
        className="text-2xl font-bold"
        style={{ color: displayColor }}
      >
        {score}
      </span>
      <span className="text-xs text-gray-600 mt-1 text-center">{label}</span>
    </div>
  )
}
