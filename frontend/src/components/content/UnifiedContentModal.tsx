'use client'

import { useState } from 'react'
import { contentApi } from '@/services/api'

type ContentInputTab = 'url' | 'pdf' | 'text'

interface UnifiedContentModalProps {
  isOpen: boolean
  onClose: () => void
  onContentAdded: (contentId: string) => void
}

export function UnifiedContentModal({
  isOpen,
  onClose,
  onContentAdded
}: UnifiedContentModalProps) {
  const [activeTab, setActiveTab] = useState<ContentInputTab>('url')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [textTitle, setTextTitle] = useState('')
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [pdfTitle, setPdfTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async () => {
    setError(null)
    setLoading(true)

    try {
      if (activeTab === 'url') {
        if (!urlInput.trim()) {
          setError('Please enter a URL')
          setLoading(false)
          return
        }

        const response = await contentApi.submit(urlInput, {
          inputType: 'url',
          saveToLibrary: true
        })

        onContentAdded(response.library_id)
        resetAndClose()

      } else if (activeTab === 'text') {
        if (!textInput.trim()) {
          setError('Please paste some text')
          setLoading(false)
          return
        }

        const response = await contentApi.submit(textInput, {
          inputType: 'text',
          title: textTitle || undefined,
          saveToLibrary: true
        })

        onContentAdded(response.library_id)
        resetAndClose()

      } else if (activeTab === 'pdf') {
        if (!pdfFile) {
          setError('Please select a PDF file')
          setLoading(false)
          return
        }

        const response = await contentApi.upload(pdfFile, {
          title: pdfTitle || undefined
        })

        if (response.success && response.content) {
          onContentAdded(response.content.source_id)
          resetAndClose()
        } else {
          setError(response.error || 'PDF upload failed')
        }
      }
    } catch (err: any) {
      console.error('Content submission error:', err)
      setError(err.response?.data?.detail || err.message || 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  const resetAndClose = () => {
    setUrlInput('')
    setTextInput('')
    setTextTitle('')
    setPdfFile(null)
    setPdfTitle('')
    setError(null)
    setLoading(false)
    onClose()
  }

  const getButtonText = () => {
    if (loading) return 'Processing...'
    if (activeTab === 'url') return 'Capture Content'
    if (activeTab === 'pdf') return 'Upload & Extract'
    if (activeTab === 'text') return 'Save Content'
    return 'Submit'
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Only PDF files are supported')
        return
      }
      setPdfFile(file)
      setError(null)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            💎 Add Content
          </h2>
          <button
            onClick={resetAndClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            disabled={loading}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 px-6">
          <button
            onClick={() => setActiveTab('url')}
            className={`px-4 py-3 font-medium transition-colors border-b-2 ${
              activeTab === 'url'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
            disabled={loading}
          >
            🌐 URL
          </button>
          <button
            onClick={() => setActiveTab('pdf')}
            className={`px-4 py-3 font-medium transition-colors border-b-2 ${
              activeTab === 'pdf'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
            disabled={loading}
          >
            📄 PDF Upload
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`px-4 py-3 font-medium transition-colors border-b-2 ${
              activeTab === 'text'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
            disabled={loading}
          >
            📋 Paste Text
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* URL Tab */}
          {activeTab === 'url' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste any URL
                </label>
                <input
                  type="text"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://youtube.com/watch?v=... or any article URL"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  disabled={loading}
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit()
                    }
                  }}
                />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Supports YouTube videos, articles, blog posts, Wikipedia, and more
                </p>
              </div>
            </div>
          )}

          {/* PDF Upload Tab */}
          {activeTab === 'pdf' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select PDF file
                </label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="pdf-upload"
                    disabled={loading}
                  />
                  <label
                    htmlFor="pdf-upload"
                    className="cursor-pointer flex flex-col items-center space-y-2"
                  >
                    <svg
                      className="w-12 h-12 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Click to select or drag & drop
                    </span>
                    {pdfFile && (
                      <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
                        {pdfFile.name}
                      </span>
                    )}
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Document title (optional)
                </label>
                <input
                  type="text"
                  value={pdfTitle}
                  onChange={(e) => setPdfTitle(e.target.value)}
                  placeholder="Override auto-detected title"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  disabled={loading}
                />
              </div>
            </div>
          )}

          {/* Paste Text Tab */}
          {activeTab === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title (optional)
                </label>
                <input
                  type="text"
                  value={textTitle}
                  onChange={(e) => setTextTitle(e.target.value)}
                  placeholder="Give your content a title"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste your text
                </label>
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste any text - emails, articles, notes, transcripts..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white min-h-[200px] resize-y font-mono text-sm"
                  disabled={loading}
                  autoFocus
                />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {textInput.length} characters
                </p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <button
            onClick={resetAndClose}
            className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
          >
            {getButtonText()}
          </button>
        </div>
      </div>
    </div>
  )
}
