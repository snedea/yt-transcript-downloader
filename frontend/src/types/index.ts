export interface Video {
  id: string
  title: string
  thumbnail: string
  duration: number
}

export interface Transcript {
  video_id: string
  video_title: string
  title: string  // For bulk results
  transcript: string
  author?: string
  upload_date?: string
  tokens_used?: number
  error?: string
}

export interface BulkResult {
  results: Transcript[]
  total: number
  successful: number
  failed: number
}

export interface TranscriptRequest {
  video_url: string
  clean: boolean
}

export interface TranscriptResponse {
  transcript: string
  video_title: string
  video_id: string
  author?: string
  upload_date?: string
  tokens_used?: number
}

export interface PlaylistRequest {
  playlist_url: string
}

export interface PlaylistResponse {
  videos: Video[]
}

export interface BulkTranscriptRequest {
  video_ids: string[]
  clean: boolean
}
