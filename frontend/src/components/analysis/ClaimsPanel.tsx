'use client'

import React, { useState, useMemo } from 'react'
import type { DetectedClaim, ClaimType, VerificationStatus } from '@/types'

interface ClaimsPanelProps {
  claims: DetectedClaim[]
  verifiedClaims?: DetectedClaim[]
}

// Claim type metadata
const CLAIM_TYPE_META: Record<ClaimType, { label: string; color: string; icon: string }> = {
  factual: { label: 'Factual', color: '#3b82f6', icon: '📊' },
  causal: { label: 'Causal', color: '#8b5cf6', icon: '🔗' },
  normative: { label: 'Normative', color: '#f59e0b', icon: '⚖️' },
  prediction: { label: 'Prediction', color: '#06b6d4', icon: '🔮' },
  prescriptive: { label: 'Prescriptive', color: '#22c55e', icon: '📋' }
}

// Verification status metadata
const VERIFICATION_META: Record<VerificationStatus, { label: string; color: string; icon: string; bg: string }> = {
  verified: { label: 'Verified', color: '#22c55e', icon: '✓', bg: 'bg-green-100 dark:bg-green-900/30' },
  disputed: { label: 'Disputed', color: '#ef4444', icon: '✗', bg: 'bg-red-100 dark:bg-red-900/30' },
  unverified: { label: 'Unverified', color: '#f59e0b', icon: '?', bg: 'bg-yellow-100 dark:bg-yellow-900/30' },
  unverifiable: { label: 'Unverifiable', color: '#6b7280', icon: '–', bg: 'bg-gray-100 dark:bg-gray-700' }
}

type FilterType = 'all' | ClaimType
type FilterVerification = 'all' | VerificationStatus

export function ClaimsPanel({ claims, verifiedClaims = [] }: ClaimsPanelProps) {
  const [typeFilter, setTypeFilter] = useState<FilterType>('all')
  const [verificationFilter, setVerificationFilter] = useState<FilterVerification>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedClaim, setExpandedClaim] = useState<number | null>(null)

  // Merge claims with verification data
  const mergedClaims = useMemo(() => {
    const verifiedMap = new Map(
      verifiedClaims.map(c => [c.claim_text, c])
    )
    return claims.map(claim => ({
      ...claim,
      ...(verifiedMap.get(claim.claim_text) || {})
    }))
  }, [claims, verifiedClaims])

  // Get unique claim types for filter
  const claimTypes = useMemo(() => {
    const types = new Set(claims.map(c => c.claim_type))
    return Array.from(types) as ClaimType[]
  }, [claims])

  // Filter claims
  const filteredClaims = useMemo(() => {
    let filtered = [...mergedClaims]

    if (typeFilter !== 'all') {
      filtered = filtered.filter(c => c.claim_type === typeFilter)
    }

    if (verificationFilter !== 'all') {
      filtered = filtered.filter(c => c.verification_status === verificationFilter)
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(c => c.claim_text.toLowerCase().includes(term))
    }

    return filtered
  }, [mergedClaims, typeFilter, verificationFilter, searchTerm])

  // Summary stats
  const stats = useMemo(() => {
    const byType: Record<string, number> = {}
    const byStatus: Record<string, number> = {}

    mergedClaims.forEach(c => {
      byType[c.claim_type] = (byType[c.claim_type] || 0) + 1
      if (c.verification_status) {
        byStatus[c.verification_status] = (byStatus[c.verification_status] || 0) + 1
      }
    })

    return { byType, byStatus, total: mergedClaims.length }
  }, [mergedClaims])

  if (claims.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <span className="text-4xl mb-2 block">📝</span>
        <p>No claims detected in this transcript.</p>
        <p className="text-sm mt-1">Try deep analysis mode for claim extraction.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4">
        {/* By Type */}
        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">By Claim Type</h4>
          <div className="flex flex-wrap gap-2">
            {claimTypes.map(type => {
              const meta = CLAIM_TYPE_META[type]
              return (
                <button
                  key={type}
                  onClick={() => setTypeFilter(typeFilter === type ? 'all' : type)}
                  className={`
                    flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-all
                    ${typeFilter === type ? 'ring-2 ring-offset-1 ring-indigo-500' : ''}
                  `}
                  style={{ backgroundColor: meta.color + '20', color: meta.color }}
                >
                  <span>{meta.icon}</span>
                  <span>{meta.label}</span>
                  <span className="font-bold">{stats.byType[type] || 0}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* By Verification Status */}
        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">By Verification</h4>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(VERIFICATION_META) as VerificationStatus[]).map(status => {
              const meta = VERIFICATION_META[status]
              const count = stats.byStatus[status] || 0
              if (count === 0) return null
              return (
                <button
                  key={status}
                  onClick={() => setVerificationFilter(verificationFilter === status ? 'all' : status)}
                  className={`
                    flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-all
                    ${verificationFilter === status ? 'ring-2 ring-offset-1 ring-indigo-500' : ''}
                    ${meta.bg}
                  `}
                  style={{ color: meta.color }}
                >
                  <span>{meta.icon}</span>
                  <span>{meta.label}</span>
                  <span className="font-bold">{count}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search claims..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {filteredClaims.length} of {stats.total} claims
        </span>
      </div>

      {/* Claims List */}
      <div className="space-y-2">
        {filteredClaims.map((claim, idx) => (
          <ClaimCard
            key={idx}
            claim={claim}
            isExpanded={expandedClaim === idx}
            onToggle={() => setExpandedClaim(expandedClaim === idx ? null : idx)}
          />
        ))}

        {filteredClaims.length === 0 && (
          <div className="text-center py-4 text-gray-500 dark:text-gray-400">
            No claims match your filters
          </div>
        )}
      </div>
    </div>
  )
}

interface ClaimCardProps {
  claim: DetectedClaim
  isExpanded: boolean
  onToggle: () => void
}

function ClaimCard({ claim, isExpanded, onToggle }: ClaimCardProps) {
  const typeMeta = CLAIM_TYPE_META[claim.claim_type]
  const verificationMeta = claim.verification_status
    ? VERIFICATION_META[claim.verification_status]
    : null

  return (
    <div
      className={`
        p-3 rounded-lg border transition-all
        ${isExpanded
          ? 'border-indigo-300 dark:border-indigo-600 bg-indigo-50 dark:bg-indigo-900/10'
          : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
        }
      `}
    >
      <button
        onClick={onToggle}
        className="w-full text-left"
      >
        <div className="flex items-start gap-3">
          {/* Type icon */}
          <span className="text-xl flex-shrink-0">{typeMeta.icon}</span>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-800 dark:text-gray-200">
              {claim.claim_text}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {/* Claim type */}
              <span
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ backgroundColor: typeMeta.color + '20', color: typeMeta.color }}
              >
                {typeMeta.label}
              </span>

              {/* Verification status */}
              {verificationMeta && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${verificationMeta.bg}`}
                  style={{ color: verificationMeta.color }}
                >
                  {verificationMeta.icon} {verificationMeta.label}
                </span>
              )}

              {/* Confidence */}
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {Math.round(claim.confidence * 100)}% confidence
              </span>
            </div>
          </div>

          {/* Expand icon */}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-3">
          {/* Verification details */}
          {claim.verification_details && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium">Verification: </span>
              {claim.verification_details}
            </div>
          )}

          {/* Supporting sources */}
          {claim.supporting_sources && claim.supporting_sources.length > 0 && (
            <div>
              <h5 className="text-xs font-medium text-green-600 dark:text-green-400 mb-1">
                Supporting Sources
              </h5>
              <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                {claim.supporting_sources.map((source, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-green-400">•</span>
                    <a
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline truncate"
                    >
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Contradicting sources */}
          {claim.contradicting_sources && claim.contradicting_sources.length > 0 && (
            <div>
              <h5 className="text-xs font-medium text-red-600 dark:text-red-400 mb-1">
                Contradicting Sources
              </h5>
              <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                {claim.contradicting_sources.map((source, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-red-400">•</span>
                    <a
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline truncate"
                    >
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Position in transcript */}
          <div className="text-xs text-gray-400 dark:text-gray-500">
            Segment #{claim.segment_index + 1}
            {claim.span && ` • Characters ${claim.span[0]}-${claim.span[1]}`}
          </div>
        </div>
      )}
    </div>
  )
}

// Summary view for claims
interface ClaimsSummaryProps {
  claims: DetectedClaim[]
}

export function ClaimsSummary({ claims }: ClaimsSummaryProps) {
  const stats = useMemo(() => {
    const byType: Record<string, number> = {}
    const byStatus: Record<string, number> = {}

    claims.forEach(c => {
      byType[c.claim_type] = (byType[c.claim_type] || 0) + 1
      if (c.verification_status) {
        byStatus[c.verification_status] = (byStatus[c.verification_status] || 0) + 1
      }
    })

    return { byType, byStatus, total: claims.length }
  }, [claims])

  if (claims.length === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-3">
      <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
        <span className="font-bold">{stats.total}</span> claims detected
      </div>
      {stats.byStatus['verified'] && (
        <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400">
          <span className="font-bold">{stats.byStatus['verified']}</span> verified
        </div>
      )}
      {stats.byStatus['disputed'] && (
        <div className="flex items-center gap-1 text-sm text-red-600 dark:text-red-400">
          <span className="font-bold">{stats.byStatus['disputed']}</span> disputed
        </div>
      )}
    </div>
  )
}
