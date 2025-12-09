'use client'

import { useState } from 'react'
import { downloadTextFile, copyToClipboard, generateFilename } from '@/utils/download'

interface TranscriptDisplayProps {
  transcript: string
  videoTitle: string
  videoId: string
  author?: string
  uploadDate?: string
  tokensUsed?: number
}

export default function TranscriptDisplay({
  transcript,
  videoTitle,
  videoId,
  author,
  uploadDate,
  tokensUsed
}: TranscriptDisplayProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    const success = await copyToClipboard(transcript)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    const filename = generateFilename(videoTitle || videoId, author, uploadDate)
    downloadTextFile(transcript, filename)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
          {videoTitle}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Video ID: {videoId}
        </p>
        {tokensUsed && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Tokens used: {tokensUsed}
          </p>
        )}
      </div>

      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-4 max-h-96 overflow-y-auto">
        <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
          {transcript}
        </pre>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleCopy}
          className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
        <button
          onClick={handleDownload}
          className="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Download as TXT
        </button>
      </div>
    </div>
  )
}
