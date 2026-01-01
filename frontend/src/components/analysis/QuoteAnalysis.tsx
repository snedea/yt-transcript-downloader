'use client'

import React from 'react'
import type { QuoteMatch, SourceType } from '@/types'

interface QuoteAnalysisProps {
  quotes: QuoteMatch[]
}

// Source type colors and icons
const SOURCE_STYLES: Record<SourceType, { color: string; icon: string; bg: string }> = {
  religious: { color: '#8b5cf6', icon: '📖', bg: 'bg-purple-50' },
  political: { color: '#ef4444', icon: '🏛️', bg: 'bg-red-50' },
  literary: { color: '#3b82f6', icon: '📚', bg: 'bg-blue-50' },
  philosophical: { color: '#22c55e', icon: '🤔', bg: 'bg-green-50' },
  scientific: { color: '#06b6d4', icon: '🔬', bg: 'bg-cyan-50' },
  unknown: { color: '#6b7280', icon: '❓', bg: 'bg-gray-50' }
}

export function QuoteAnalysis({ quotes }: QuoteAnalysisProps) {
  if (quotes.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <span className="text-4xl mb-2 block">💬</span>
        <p>No potential quotes or attributions detected.</p>
        <p className="text-sm mt-1">The speaker appears to use mostly original content.</p>
      </div>
    )
  }

  const verifiedQuotes = quotes.filter(q => q.verified && q.is_quote)
  const likelyQuotes = quotes.filter(q => !q.verified && q.is_quote)
  const originalContent = quotes.filter(q => !q.is_quote)

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-gray-600">
            {verifiedQuotes.length} verified quotes
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500" />
          <span className="text-gray-600">
            {likelyQuotes.length} likely quotes
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-gray-400" />
          <span className="text-gray-600">
            {originalContent.length} original
          </span>
        </div>
      </div>

      {/* Quote Cards */}
      <div className="space-y-3">
        {quotes.map((quote, idx) => (
          <QuoteCard key={idx} quote={quote} />
        ))}
      </div>
    </div>
  )
}

interface QuoteCardProps {
  quote: QuoteMatch
}

function QuoteCard({ quote }: QuoteCardProps) {
  const sourceType = quote.source_type || 'unknown'
  const style = SOURCE_STYLES[sourceType]

  return (
    <div className={`p-4 rounded-lg border ${style.bg}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{style.icon}</span>

        <div className="flex-1 min-w-0">
          <p className="text-gray-800 italic mb-2">&ldquo;{quote.phrase}&rdquo;</p>

          <div className="flex flex-wrap items-center gap-2">
            {/* Quote status badge */}
            {quote.is_quote ? (
              quote.verified ? (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Verified Quote
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Likely Quote
                </span>
              )
            ) : (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                Original Content
              </span>
            )}

            {/* Source badge */}
            {quote.source && (
              <span
                className="text-xs px-2 py-1 rounded-full"
                style={{ backgroundColor: style.color + '20', color: style.color }}
              >
                {quote.source}
              </span>
            )}

            {/* Confidence */}
            <span className="text-xs text-gray-500">
              {Math.round(quote.confidence * 100)}% confidence
            </span>
          </div>

          {/* Verification details */}
          {quote.verification_details && (
            <p className="text-xs text-gray-500 mt-2">
              {quote.verification_details}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// Simple table view alternative
export function QuoteTable({ quotes }: QuoteAnalysisProps) {
  if (quotes.length === 0) {
    return <p className="text-gray-500 text-center py-4">No quotes detected</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Phrase</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {quotes.map((quote, idx) => {
            const sourceType = quote.source_type || 'unknown'
            const style = SOURCE_STYLES[sourceType]

            return (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate" title={quote.phrase}>
                  {quote.phrase.length > 60 ? quote.phrase.substring(0, 60) + '...' : quote.phrase}
                </td>
                <td className="px-4 py-3">
                  <span
                    className="text-xs px-2 py-1 rounded-full capitalize"
                    style={{ backgroundColor: style.color + '20', color: style.color }}
                  >
                    {sourceType}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {quote.source || '-'}
                </td>
                <td className="px-4 py-3">
                  {quote.verified ? (
                    <span className="text-green-600 text-xs">Verified</span>
                  ) : quote.is_quote ? (
                    <span className="text-yellow-600 text-xs">Likely</span>
                  ) : (
                    <span className="text-gray-400 text-xs">Original</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {Math.round(quote.confidence * 100)}%
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
