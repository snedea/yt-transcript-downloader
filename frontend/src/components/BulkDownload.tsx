'use client'

import { useState } from 'react'
import { useBulkDownload } from '@/hooks/useBulkDownload'
import VideoSelector from './VideoSelector'
import TranscriptDisplay from './TranscriptDisplay'
import ProgressBar from './ProgressBar'
import ErrorMessage from './ErrorMessage'
import { downloadTextFile, sanitizeFilename } from '@/utils/download'

export default function BulkDownload() {
  const [playlistUrl, setPlaylistUrl] = useState('')
  const [selectedVideoIds, setSelectedVideoIds] = useState<string[]>([])
  const [cleanTranscript, setCleanTranscript] = useState(false)
  const {
    loading,
    error,
    videos,
    transcripts,
    progress,
    fetchPlaylistVideos,
    fetchBulkTranscripts,
    reset
  } = useBulkDownload()

  const handleFetchPlaylist = (e: React.FormEvent) => {
    e.preventDefault()
    if (playlistUrl.trim()) {
      reset()
      fetchPlaylistVideos(playlistUrl)
    }
  }

  const handleFetchTranscripts = () => {
    if (selectedVideoIds.length > 0) {
      if (selectedVideoIds.length > 50) {
        if (!confirm(`You're about to fetch ${selectedVideoIds.length} transcripts. This may take a while. Continue?`)) {
          return
        }
      }
      fetchBulkTranscripts(selectedVideoIds, cleanTranscript)
    }
  }

  const handleDownloadAll = () => {
    if (!transcripts) return

    transcripts.results.forEach((result) => {
      if (result.transcript) {
        const filename = `${sanitizeFilename(result.title)}_transcript.txt`
        downloadTextFile(result.transcript, filename)
      }
    })
  }

  const isValidPlaylistUrl = (url: string) => {
    return url.includes('youtube.com') && (url.includes('list=') || url.includes('channel/') || url.includes('@'))
  }

  return (
    <div className="space-y-6">
      {/* Phase 1: Playlist URL Input */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <form onSubmit={handleFetchPlaylist}>
          <div className="mb-4">
            <label
              htmlFor="playlistUrl"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              YouTube Playlist or Channel URL
            </label>
            <input
              type="text"
              id="playlistUrl"
              value={playlistUrl}
              onChange={(e) => setPlaylistUrl(e.target.value)}
              placeholder="https://www.youtube.com/playlist?list=..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !playlistUrl.trim() || !isValidPlaylistUrl(playlistUrl)}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            {loading && videos.length === 0 ? 'Fetching Videos...' : 'Get Videos'}
          </button>
        </form>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Phase 2: Video Selection */}
      {videos.length > 0 && !transcripts && (
        <>
          <VideoSelector videos={videos} onSelect={setSelectedVideoIds} />

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={cleanTranscript}
                  onChange={(e) => setCleanTranscript(e.target.checked)}
                  className="mr-2"
                  disabled={loading}
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Clean transcripts with AI (GPT-4o-mini)
                </span>
              </label>
            </div>

            <button
              onClick={handleFetchTranscripts}
              disabled={loading || selectedVideoIds.length === 0}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Fetching Transcripts...' : `Fetch ${selectedVideoIds.length} Transcripts`}
            </button>
          </div>
        </>
      )}

      {/* Phase 3: Progress */}
      {loading && progress.total > 0 && (
        <ProgressBar
          current={progress.current}
          total={progress.total}
          status="Fetching transcripts..."
        />
      )}

      {/* Phase 4: Results */}
      {transcripts && (
        <>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Results Summary
              </h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-blue-500">{transcripts.total}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-500">{transcripts.successful}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Successful</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-500">{transcripts.failed}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
                </div>
              </div>
            </div>

            <button
              onClick={handleDownloadAll}
              className="w-full bg-purple-500 hover:bg-purple-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Download All Successful Transcripts
            </button>
          </div>

          <div className="space-y-4">
            {transcripts.results.map((result) => (
              <div key={result.video_id}>
                {result.transcript ? (
                  <TranscriptDisplay
                    transcript={result.transcript}
                    videoTitle={result.title}
                    videoId={result.video_id}
                    tokensUsed={result.tokens_used}
                  />
                ) : (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <p className="font-medium text-red-800 dark:text-red-200">
                      {result.title}
                    </p>
                    <p className="text-sm text-red-600 dark:text-red-300">
                      Error: {result.error}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
