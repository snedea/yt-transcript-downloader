'use client'

import React, { useState, useRef } from 'react'
import type { AnalysisResult } from '@/types'
import { ScoreGauge, MiniScore } from './ScoreGauge'
import { PillarChart, PillarDetailCard } from './PillarChart'
import { TechniqueList } from './TechniqueList'
import { QuoteAnalysis } from './QuoteAnalysis'
import { exportToPdf, exportToMarkdown } from '@/utils/pdfExport'

interface RhetoricalAnalysisProps {
  result: AnalysisResult
  videoTitle?: string
  videoAuthor?: string
  isCached?: boolean
  analysisDate?: string
}

type TabType = 'overview' | 'techniques' | 'quotes' | 'summary'

export function RhetoricalAnalysis({ result, videoTitle, videoAuthor, isCached, analysisDate }: RhetoricalAnalysisProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [exporting, setExporting] = useState(false)
  const reportRef = useRef<HTMLDivElement>(null)

  const handleExportPdf = async () => {
    if (!reportRef.current) return
    setExporting(true)
    try {
      await exportToPdf(reportRef.current, videoTitle || 'Rhetorical Analysis')
    } catch (error) {
      console.error('PDF export failed:', error)
      alert('Failed to export PDF. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  const handleExportMarkdown = () => {
    exportToMarkdown(result, videoTitle, videoAuthor)
  }

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'techniques', label: 'Techniques', icon: '🎯' },
    { id: 'quotes', label: 'Quotes', icon: '💬' },
    { id: 'summary', label: 'Summary', icon: '📝' }
  ]

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden" ref={reportRef}>
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-2xl font-bold">Rhetorical Analysis Report</h2>
              {isCached && (
                <span className="text-xs bg-white/20 text-white px-2 py-1 rounded-full">
                  Cached Analysis
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
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="text-center">
            <div className="text-2xl font-bold">{result.total_techniques_found}</div>
            <div className="text-xs text-indigo-200">Techniques Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.unique_techniques_used}</div>
            <div className="text-xs text-indigo-200">Unique Types</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.total_quotes_found}</div>
            <div className="text-xs text-indigo-200">Quotes Detected</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{result.transcript_word_count}</div>
            <div className="text-xs text-indigo-200">Words Analyzed</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b">
        <div className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
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
        {activeTab === 'techniques' && (
          <TechniquesTab result={result} />
        )}
        {activeTab === 'quotes' && (
          <QuotesTab result={result} />
        )}
        {activeTab === 'summary' && (
          <SummaryTab result={result} />
        )}
      </div>

      {/* Footer with Export Options */}
      <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t">
        <div className="text-xs text-gray-500">
          Analysis completed in {result.analysis_duration_seconds}s | {result.tokens_used} tokens used
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportMarkdown}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Export Markdown
          </button>
          <button
            onClick={handleExportPdf}
            disabled={exporting}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {exporting ? 'Exporting...' : 'Export PDF'}
          </button>
        </div>
      </div>
    </div>
  )
}

// Tab Components
function OverviewTab({ result }: { result: AnalysisResult }) {
  return (
    <div className="space-y-8">
      {/* Score and Pillars */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="flex justify-center">
          <ScoreGauge
            score={result.overall_score}
            grade={result.overall_grade}
            label="Rhetorical Effectiveness"
          />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">The Four Pillars</h3>
          <PillarChart pillarScores={result.pillar_scores} variant="bar" />
        </div>
      </div>

      {/* Pillar Details */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Pillar Analysis</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {result.pillar_scores.map((pillar) => (
            <PillarDetailCard key={pillar.pillar} pillar={pillar} />
          ))}
        </div>
      </div>
    </div>
  )
}

function TechniquesTab({ result }: { result: AnalysisResult }) {
  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Rhetorical Techniques ({result.total_techniques_found})
        </h3>
        <p className="text-sm text-gray-500">
          {result.unique_techniques_used} unique techniques identified across the transcript
        </p>
      </div>
      <TechniqueList
        techniques={result.technique_matches}
        summary={result.technique_summary}
      />
    </div>
  )
}

function QuotesTab({ result }: { result: AnalysisResult }) {
  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Quote Attribution Analysis
        </h3>
        <p className="text-sm text-gray-500">
          {result.verified_quotes} of {result.total_quotes_found} potential quotes verified via web search
        </p>
      </div>
      <QuoteAnalysis quotes={result.quote_matches} />
    </div>
  )
}

function SummaryTab({ result }: { result: AnalysisResult }) {
  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Executive Summary</h3>
        <div className="prose prose-sm max-w-none text-gray-700">
          {result.executive_summary.split('\n').map((paragraph, idx) => (
            <p key={idx} className="mb-3">{paragraph}</p>
          ))}
        </div>
      </div>

      {/* Strengths */}
      {result.strengths.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span className="text-green-500">+</span> Rhetorical Strengths
          </h3>
          <ul className="space-y-2">
            {result.strengths.map((strength, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement */}
      {result.areas_for_improvement.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span className="text-amber-500">!</span> Areas for Improvement
          </h3>
          <ul className="space-y-2">
            {result.areas_for_improvement.map((area, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <svg className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">{area}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
