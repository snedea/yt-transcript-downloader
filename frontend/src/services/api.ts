import axios from 'axios'
import type {
  TranscriptRequest,
  TranscriptResponse,
  PlaylistRequest,
  PlaylistResponse,
  BulkTranscriptRequest,
  BulkResult,
  AnalysisRequest,
  AnalysisResult,
  AnalysisStatus,
  TranscriptSegment
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const transcriptApi = {
  fetchSingle: async (videoUrl: string, clean: boolean, useCache: boolean = true): Promise<TranscriptResponse> => {
    const response = await api.post<TranscriptResponse>('/api/transcript/single', {
      video_url: videoUrl,
      clean,
      use_cache: useCache
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

// Types for cache API
export interface CacheHistoryItem {
  video_id: string
  video_title: string
  author: string | null
  is_cleaned: boolean
  has_analysis: boolean
  created_at: string
  last_accessed: string
  access_count: number
}

export interface CacheHistoryResponse {
  items: CacheHistoryItem[]
  total: number
}

export interface CachedTranscript extends TranscriptResponse {
  cached: boolean
  created_at: string
  last_accessed: string
  access_count: number
  analysis_result?: AnalysisResult
  analysis_date?: string
  has_analysis: boolean
}

export const cacheApi = {
  /**
   * Get transcript history
   */
  getHistory: async (limit: number = 50, offset: number = 0): Promise<CacheHistoryResponse> => {
    const response = await api.get<CacheHistoryResponse>('/api/cache/history', {
      params: { limit, offset }
    })
    return response.data
  },

  /**
   * Get a cached transcript by video ID
   */
  getTranscript: async (videoId: string): Promise<CachedTranscript | null> => {
    try {
      const response = await api.get<CachedTranscript>(`/api/cache/transcript/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Search cached transcripts
   */
  search: async (query: string, limit: number = 20): Promise<CacheHistoryItem[]> => {
    const response = await api.get('/api/cache/search', {
      params: { q: query, limit }
    })
    return response.data.results
  },

  /**
   * Delete a cached transcript
   */
  delete: async (videoId: string): Promise<void> => {
    await api.delete(`/api/cache/transcript/${videoId}`)
  },

  /**
   * Get cache statistics
   */
  getStats: async (): Promise<{ total_transcripts: number }> => {
    const response = await api.get('/api/cache/stats')
    return response.data
  },

  /**
   * Save rhetorical analysis results
   */
  saveAnalysis: async (videoId: string, analysisResult: AnalysisResult): Promise<void> => {
    await api.post('/api/cache/analysis', {
      video_id: videoId,
      analysis_result: analysisResult
    })
  },

  /**
   * Get cached analysis for a video
   */
  getAnalysis: async (videoId: string): Promise<{ analysis: AnalysisResult; analysis_date: string } | null> => {
    try {
      const response = await api.get(`/api/cache/analysis/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
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

export const analysisApi = {
  /**
   * Analyze a transcript for rhetorical techniques
   */
  analyzeRhetoric: async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: {
      verifyQuotes?: boolean
      videoTitle?: string
      videoAuthor?: string
    }
  ): Promise<AnalysisResult> => {
    const response = await api.post<AnalysisResult>('/api/analysis/rhetorical', {
      transcript,
      transcript_data: transcriptData,
      verify_quotes: options?.verifyQuotes ?? true,
      video_title: options?.videoTitle,
      video_author: options?.videoAuthor
    })
    return response.data
  },

  /**
   * Check if analysis services are available
   */
  getStatus: async (): Promise<AnalysisStatus> => {
    const response = await api.get<AnalysisStatus>('/api/analysis/status')
    return response.data
  },

  /**
   * Get the complete rhetorical toolkit reference
   */
  getToolkit: async (): Promise<any> => {
    const response = await api.get('/api/analysis/toolkit')
    return response.data
  },

  /**
   * Get details about a specific technique
   */
  getTechniqueDetails: async (techniqueId: string): Promise<any> => {
    const response = await api.get(`/api/analysis/techniques/${techniqueId}`)
    return response.data
  }
}
