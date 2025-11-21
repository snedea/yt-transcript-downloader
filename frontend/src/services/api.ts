import axios from 'axios'
import type {
  TranscriptRequest,
  TranscriptResponse,
  PlaylistRequest,
  PlaylistResponse,
  BulkTranscriptRequest,
  BulkResult
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const transcriptApi = {
  fetchSingle: async (videoUrl: string, clean: boolean): Promise<TranscriptResponse> => {
    const response = await api.post<TranscriptResponse>('/api/transcript/single', {
      video_url: videoUrl,
      clean
    })
    return response.data
  },

  fetchBulk: async (videoIds: string[], clean: boolean): Promise<BulkResult> => {
    const response = await api.post<BulkResult>('/api/transcript/bulk', {
      video_ids: videoIds,
      clean
    })
    return response.data
  },

  cleanTranscript: async (transcript: string): Promise<{ cleaned_transcript: string; tokens_used: number }> => {
    const response = await api.post('/api/transcript/clean', { transcript })
    return response.data
  }
}

export const playlistApi = {
  getVideos: async (playlistUrl: string): Promise<PlaylistResponse> => {
    const response = await api.post<PlaylistResponse>('/api/playlist/videos', {
      playlist_url: playlistUrl
    })
    return response.data
  }
}
