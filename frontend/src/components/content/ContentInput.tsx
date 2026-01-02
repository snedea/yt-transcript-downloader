'use client'

import React, { useState, useRef, useCallback } from 'react'
import type { ContentSourceType } from '@/types'

interface ContentInputProps {
  onAnalyze: (source: string, sourceType: ContentSourceType, file?: File) => Promise<void>
  isAnalyzing: boolean
  disabled?: boolean
}

type InputMode = 'url' | 'text' | 'file'

export function ContentInput({ onAnalyze, isAnalyzing, disabled }: ContentInputProps) {
  const [mode, setMode] = useState<InputMode>('url')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const detectSourceType = (url: string): ContentSourceType => {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return 'youtube'
    }
    if (url.endsWith('.pdf')) {
      return 'pdf'
    }
    return 'web_url'
  }

  const handleSubmit = async () => {
    if (mode === 'url' && urlInput.trim()) {
      const sourceType = detectSourceType(urlInput.trim())
      await onAnalyze(urlInput.trim(), sourceType)
    } else if (mode === 'text' && textInput.trim()) {
      await onAnalyze(textInput.trim(), 'plain_text')
    } else if (mode === 'file' && selectedFile) {
      await onAnalyze(selectedFile.name, 'pdf', selectedFile)
    }
  }

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
        setMode('file')
      }
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const isValid = (mode === 'url' && urlInput.trim()) ||
                  (mode === 'text' && textInput.trim().split(/\s+/).length >= 50) ||
                  (mode === 'file' && selectedFile)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <span>🔬</span> Discovery Mode - Analyze Any Content
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Upload a PDF, paste a URL, or enter text to extract cross-domain insights using the Kinoshita Pattern.
      </p>

      {/* Mode Tabs */}
      <div className="flex rounded-lg bg-gray-100 dark:bg-gray-700 p-1 mb-4">
        <button
          onClick={() => setMode('url')}
          className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-all ${
            mode === 'url'
              ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          🔗 URL
        </button>
        <button
          onClick={() => setMode('file')}
          className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-all ${
            mode === 'file'
              ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          📄 PDF Upload
        </button>
        <button
          onClick={() => setMode('text')}
          className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-all ${
            mode === 'text'
              ? 'bg-white dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          📝 Paste Text
        </button>
      </div>

      {/* URL Input */}
      {mode === 'url' && (
        <div className="space-y-3">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://arxiv.org/abs/... or any web URL"
            disabled={isAnalyzing || disabled}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Supports web articles, blog posts, and documentation pages.
          </p>
        </div>
      )}

      {/* File Upload */}
      {mode === 'file' && (
        <div className="space-y-3">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
              ${dragActive
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500'
              }
              ${isAnalyzing || disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={isAnalyzing || disabled}
              className="hidden"
            />
            {selectedFile ? (
              <div className="space-y-2">
                <div className="text-4xl">📄</div>
                <p className="font-medium text-gray-900 dark:text-white">{selectedFile.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedFile(null)
                  }}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-4xl">📤</div>
                <p className="font-medium text-gray-700 dark:text-gray-300">
                  Drop a PDF here or click to upload
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Research papers, whitepapers, technical documents
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Text Input */}
      {mode === 'text' && (
        <div className="space-y-3">
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Paste article text, notes, or any content you want to analyze..."
            disabled={isAnalyzing || disabled}
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed resize-none"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Minimum 50 words required. Current: {textInput.trim().split(/\s+/).filter(Boolean).length} words
          </p>
        </div>
      )}

      {/* Analyze Button */}
      <button
        onClick={handleSubmit}
        disabled={!isValid || isAnalyzing || disabled}
        className="mt-4 w-full bg-gradient-to-r from-indigo-600 to-purple-600
                 hover:from-indigo-700 hover:to-purple-700
                 text-white font-medium py-3 px-6 rounded-lg
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 flex items-center justify-center gap-2"
      >
        {isAnalyzing ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyzing with Kinoshita Pattern...
          </>
        ) : (
          <>
            <span>🔬</span>
            Run Discovery Analysis
          </>
        )}
      </button>
    </div>
  )
}
