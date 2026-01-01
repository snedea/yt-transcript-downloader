'use client'

import React, { useState, useMemo } from 'react'
import type { TechniqueMatch, TechniqueSummary, TechniqueStrength } from '@/types'

interface TechniqueListProps {
  techniques: TechniqueMatch[]
  summary: TechniqueSummary[]
}

type SortField = 'technique_name' | 'category' | 'phrase' | 'strength'
type SortDirection = 'asc' | 'desc'

// Category colors
const CATEGORY_COLORS: Record<string, string> = {
  repetition: '#3b82f6',
  structure: '#8b5cf6',
  contrast: '#ef4444',
  sound: '#22c55e',
  wordplay: '#f59e0b',
  comparison: '#06b6d4',
  substitution: '#ec4899',
  irony: '#6366f1',
  exaggeration: '#f97316',
  other: '#6b7280'
}

// Strength order for sorting
const STRENGTH_ORDER: Record<TechniqueStrength, number> = {
  strong: 3,
  moderate: 2,
  subtle: 1
}

// Strength styles
const STRENGTH_STYLES: Record<TechniqueStrength, { bg: string; text: string; label: string }> = {
  strong: { bg: 'bg-green-100', text: 'text-green-700', label: 'Strong' },
  moderate: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Moderate' },
  subtle: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Subtle' }
}

export function TechniqueList({ techniques, summary }: TechniqueListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('strength')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [strengthFilter, setStrengthFilter] = useState<string>('all')

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(techniques.map(t => t.category || 'other'))
    return ['all', ...Array.from(cats).sort()]
  }, [techniques])

  // Filter and sort techniques
  const filteredTechniques = useMemo(() => {
    let filtered = [...techniques]

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(t =>
        t.technique_name.toLowerCase().includes(term) ||
        t.phrase.toLowerCase().includes(term) ||
        t.explanation.toLowerCase().includes(term) ||
        t.category.toLowerCase().includes(term)
      )
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(t => (t.category || 'other') === categoryFilter)
    }

    // Apply strength filter
    if (strengthFilter !== 'all') {
      filtered = filtered.filter(t => t.strength === strengthFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortField) {
        case 'technique_name':
          comparison = a.technique_name.localeCompare(b.technique_name)
          break
        case 'category':
          comparison = (a.category || 'other').localeCompare(b.category || 'other')
          break
        case 'phrase':
          comparison = a.phrase.localeCompare(b.phrase)
          break
        case 'strength':
          comparison = STRENGTH_ORDER[a.strength] - STRENGTH_ORDER[b.strength]
          break
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [techniques, searchTerm, sortField, sortDirection, categoryFilter, strengthFilter])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const SortHeader = ({ field, label }: { field: SortField; label: string }) => (
    <th
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {label}
        <span className="text-gray-400">
          {sortField === field ? (
            sortDirection === 'asc' ? '↑' : '↓'
          ) : '↕'}
        </span>
      </div>
    </th>
  )

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="flex flex-wrap gap-2 mb-4">
        {summary.slice(0, 8).map((tech) => (
          <div
            key={tech.technique_id}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
            style={{
              backgroundColor: (CATEGORY_COLORS[tech.category] || '#6b7280') + '20',
              color: CATEGORY_COLORS[tech.category] || '#6b7280'
            }}
          >
            <span className="font-medium">{tech.technique_name}</span>
            <span className="bg-white/50 px-1.5 py-0.5 rounded-full text-xs font-bold">
              {tech.count}x
            </span>
          </div>
        ))}
        {summary.length > 8 && (
          <span className="text-sm text-gray-500 self-center">
            +{summary.length - 8} more techniques
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search techniques, phrases, explanations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* Category Filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>

        {/* Strength Filter */}
        <select
          value={strengthFilter}
          onChange={(e) => setStrengthFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="all">All Strengths</option>
          <option value="strong">Strong</option>
          <option value="moderate">Moderate</option>
          <option value="subtle">Subtle</option>
        </select>

        {/* Results count */}
        <span className="text-sm text-gray-500">
          {filteredTechniques.length} of {techniques.length} techniques
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <SortHeader field="technique_name" label="Technique" />
              <SortHeader field="category" label="Category" />
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Phrase
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Analysis
              </th>
              <SortHeader field="strength" label="Strength" />
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredTechniques.map((tech, idx) => {
              const strengthStyle = STRENGTH_STYLES[tech.strength]
              const categoryColor = CATEGORY_COLORS[tech.category] || CATEGORY_COLORS.other

              return (
                <tr key={`${tech.technique_id}-${idx}`} className="hover:bg-gray-50">
                  {/* Technique Name */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="font-medium text-gray-900">
                      {tech.technique_name}
                    </span>
                  </td>

                  {/* Category */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: categoryColor + '20',
                        color: categoryColor
                      }}
                    >
                      <span
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: categoryColor }}
                      />
                      {(tech.category || 'other').charAt(0).toUpperCase() + (tech.category || 'other').slice(1)}
                    </span>
                  </td>

                  {/* Phrase */}
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-700 italic max-w-xs">
                      &ldquo;{tech.phrase}&rdquo;
                    </p>
                    {tech.start_time !== undefined && (
                      <span className="text-xs text-gray-400">
                        @ {formatTimestamp(tech.start_time)}
                      </span>
                    )}
                  </td>

                  {/* Analysis/Explanation */}
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-600 max-w-md">
                      {tech.explanation}
                    </p>
                  </td>

                  {/* Strength */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${strengthStyle.bg} ${strengthStyle.text}`}>
                      {strengthStyle.label}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {filteredTechniques.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No techniques match your filters
          </div>
        )}
      </div>
    </div>
  )
}

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

interface TechniqueCardProps {
  technique: TechniqueMatch
}

export function TechniqueCard({ technique }: TechniqueCardProps) {
  const color = CATEGORY_COLORS[technique.category] || '#6b7280'
  const strengthStyle = STRENGTH_STYLES[technique.strength]

  return (
    <div
      className="p-4 rounded-lg border-l-4 bg-white shadow-sm"
      style={{ borderLeftColor: color }}
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-800">{technique.technique_name}</h4>
        <span className={`text-xs px-2 py-0.5 rounded-full ${strengthStyle.bg} ${strengthStyle.text}`}>
          {strengthStyle.label}
        </span>
      </div>
      <p className="text-sm text-gray-600 italic mb-2">&ldquo;{technique.phrase}&rdquo;</p>
      <p className="text-sm text-gray-700">{technique.explanation}</p>
    </div>
  )
}
