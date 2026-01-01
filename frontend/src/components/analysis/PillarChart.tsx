'use client'

import React from 'react'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell
} from 'recharts'
import type { PillarScore } from '@/types'

interface PillarChartProps {
  pillarScores: PillarScore[]
  variant?: 'radar' | 'bar'
}

// Pillar colors
const PILLAR_COLORS: Record<string, string> = {
  logos: '#3b82f6',   // blue
  pathos: '#ef4444',  // red
  ethos: '#22c55e',   // green
  kairos: '#a855f7'   // purple
}

// Pillar icons/symbols
const PILLAR_SYMBOLS: Record<string, string> = {
  logos: '🧠',
  pathos: '❤️',
  ethos: '⚖️',
  kairos: '⏰'
}

export function PillarChart({ pillarScores, variant = 'bar' }: PillarChartProps) {
  const chartData = pillarScores.map(p => ({
    pillar: p.pillar_name,
    score: p.score,
    fullMark: 100,
    color: PILLAR_COLORS[p.pillar] || '#6b7280'
  }))

  if (variant === 'radar') {
    return (
      <div className="w-full h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis
              dataKey="pillar"
              tick={{ fill: '#4b5563', fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#9ca3af', fontSize: 10 }}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '8px 12px'
              }}
              formatter={(value) => [`${value}/100`, 'Score']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  // Bar chart variant (default)
  return (
    <div className="w-full">
      <div className="space-y-3">
        {pillarScores.map((pillar) => (
          <div key={pillar.pillar} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <span>{PILLAR_SYMBOLS[pillar.pillar]}</span>
                <span className="font-medium text-gray-700">{pillar.pillar_name}</span>
              </span>
              <span
                className="font-bold"
                style={{ color: PILLAR_COLORS[pillar.pillar] }}
              >
                {pillar.score}/100
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-500"
                style={{
                  width: `${pillar.score}%`,
                  backgroundColor: PILLAR_COLORS[pillar.pillar]
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

interface PillarDetailCardProps {
  pillar: PillarScore
}

export function PillarDetailCard({ pillar }: PillarDetailCardProps) {
  const color = PILLAR_COLORS[pillar.pillar] || '#6b7280'
  const symbol = PILLAR_SYMBOLS[pillar.pillar] || '📊'

  return (
    <div
      className="p-4 rounded-lg border-2 transition-shadow hover:shadow-md"
      style={{ borderColor: color + '40' }}
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-xl">{symbol}</span>
          {pillar.pillar_name}
        </h4>
        <span
          className="text-2xl font-bold"
          style={{ color }}
        >
          {pillar.score}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-3">{pillar.explanation}</p>

      {pillar.key_examples.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-medium text-gray-500 mb-1">Key Examples:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {pillar.key_examples.slice(0, 2).map((example, idx) => (
              <li key={idx} className="italic truncate">&ldquo;{example}&rdquo;</li>
            ))}
          </ul>
        </div>
      )}

      {pillar.contributing_techniques.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {pillar.contributing_techniques.slice(0, 3).map((tech, idx) => (
            <span
              key={idx}
              className="text-xs px-2 py-0.5 rounded-full"
              style={{ backgroundColor: color + '20', color }}
            >
              {tech}
            </span>
          ))}
          {pillar.contributing_techniques.length > 3 && (
            <span className="text-xs text-gray-500">
              +{pillar.contributing_techniques.length - 3} more
            </span>
          )}
        </div>
      )}
    </div>
  )
}
