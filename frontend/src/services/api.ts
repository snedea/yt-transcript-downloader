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
  TranscriptSegment,
  ManipulationAnalysisResult,
  ManipulationAnalysisRequest,
  AnalysisMode,
  ManipulationToolkit,
  DimensionDefinition,
  ManipulationTechnique,
  ContentSummaryResult,
  DiscoveryResult,
  DiscoveryRequest,
  ContentSourceType,
  UnifiedContent,
  ContentExtractionRequest,
  ContentUploadResponse,
  HealthObservationResult,
  HealthObservationRequest
} from '@/types'

// Use relative URLs (empty string) when NEXT_PUBLIC_API_URL is not set or empty
// This allows the app to work behind a reverse proxy (Caddy/nginx)
const API_BASE = process.env.NEXT_PUBLIC_API_URL !== undefined && process.env.NEXT_PUBLIC_API_URL !== ''
  ? process.env.NEXT_PUBLIC_API_URL
  : (typeof window !== 'undefined' ? '' : 'http://localhost:8000')

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
  has_summary: boolean
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
  // Rhetorical analysis (v1.0 - 4 pillars)
  analysis_result?: AnalysisResult
  analysis_date?: string
  has_analysis: boolean
  // Manipulation/Trust analysis (v2.0 - 5 dimensions)
  manipulation_result?: ManipulationAnalysisResult
  manipulation_date?: string
  has_manipulation: boolean
  // Content summary
  summary_result?: ContentSummaryResult
  summary_date?: string
  has_summary: boolean
  // Discovery analysis (Kinoshita Pattern)
  discovery_result?: DiscoveryResult
  discovery_date?: string
  has_discovery: boolean
  // Health observations (visual analysis)
  health_observation_result?: HealthObservationResult
  health_observation_date?: string
  has_health: boolean
}

// Library/Search API types
export interface LibraryItem {
  video_id: string
  video_title: string
  author: string | null
  is_cleaned: boolean
  has_analysis: boolean  // true if either rhetorical or manipulation exists
  has_summary: boolean
  has_manipulation: boolean  // trust analysis v2.0
  has_rhetorical: boolean    // rhetorical analysis v1.0
  has_discovery: boolean     // discovery analysis (Kinoshita pattern)
  has_health: boolean        // health observations (visual analysis)
  analysis_type: 'manipulation' | 'rhetorical' | 'both' | null
  content_type: string | null
  keywords: string[]
  tldr: string | null
  created_at: string
  last_accessed: string
  access_count: number
}

export interface SearchFilters {
  q?: string
  content_type?: string[]
  has_summary?: boolean
  has_analysis?: boolean
  tags?: string[]
  limit?: number
  offset?: number
  order_by?: 'last_accessed' | 'created_at' | 'title'
}

export interface SearchResponse {
  query: string
  filters: Partial<SearchFilters>
  results: LibraryItem[]
  count: number
}

export interface TagCount {
  tag: string
  count: number
}

export interface LibraryStats {
  total: number
  with_summary: number
  with_analysis: number
  with_trust: number
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
  },

  /**
   * Save content summary results
   */
  saveSummary: async (videoId: string, summaryResult: ContentSummaryResult): Promise<void> => {
    await api.post('/api/cache/summary', {
      video_id: videoId,
      summary_result: summaryResult
    })
  },

  /**
   * Save manipulation/trust analysis results (separate from rhetorical)
   */
  saveManipulation: async (videoId: string, manipulationResult: ManipulationAnalysisResult): Promise<void> => {
    console.log('[cacheApi.saveManipulation] Saving to:', `/api/cache/manipulation`, {
      videoId,
      resultScore: manipulationResult?.overall_score,
      resultGrade: manipulationResult?.overall_grade
    })
    const response = await api.post('/api/cache/manipulation', {
      video_id: videoId,
      manipulation_result: manipulationResult
    })
    console.log('[cacheApi.saveManipulation] Response:', response.status, response.data)
  },

  /**
   * Get cached manipulation/trust analysis for a video
   */
  getManipulation: async (videoId: string): Promise<{ manipulation: ManipulationAnalysisResult; manipulation_date: string } | null> => {
    try {
      const response = await api.get(`/api/cache/manipulation/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Get cached summary for a video
   */
  getSummary: async (videoId: string): Promise<{ summary: ContentSummaryResult; summary_date: string } | null> => {
    try {
      const response = await api.get(`/api/cache/summary/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Advanced search with full-text search and faceted filtering
   */
  advancedSearch: async (filters: SearchFilters): Promise<SearchResponse> => {
    const params = new URLSearchParams()
    if (filters.q) params.set('q', filters.q)
    if (filters.content_type) {
      filters.content_type.forEach(t => params.append('content_type', t))
    }
    if (filters.has_summary !== undefined) params.set('has_summary', String(filters.has_summary))
    if (filters.has_analysis !== undefined) params.set('has_analysis', String(filters.has_analysis))
    if (filters.tags) {
      filters.tags.forEach(t => params.append('tags', t))
    }
    if (filters.limit) params.set('limit', String(filters.limit))
    if (filters.offset) params.set('offset', String(filters.offset))
    if (filters.order_by) params.set('order_by', filters.order_by)

    const response = await api.get<SearchResponse>(`/api/cache/search/advanced?${params}`)
    return response.data
  },

  /**
   * Get all tags for faceted search
   */
  getTags: async (limit: number = 100): Promise<{ tags: TagCount[] }> => {
    const response = await api.get<{ tags: TagCount[] }>('/api/cache/tags', {
      params: { limit }
    })
    return response.data
  },

  /**
   * Get content type distribution
   */
  getContentTypes: async (): Promise<{ content_types: Record<string, number> }> => {
    const response = await api.get<{ content_types: Record<string, number> }>('/api/cache/content-types')
    return response.data
  },

  /**
   * Get library statistics
   */
  getLibraryStats: async (): Promise<LibraryStats> => {
    const response = await api.get<LibraryStats>('/api/cache/library/stats')
    return response.data
  },

  /**
   * Rebuild full-text search index
   */
  rebuildFtsIndex: async (): Promise<void> => {
    await api.post('/api/cache/fts/rebuild')
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
   * Analyze a transcript for rhetorical techniques (v1.0)
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
   * Enhanced manipulation analysis with 5 dimensions (v2.0)
   * Modes: 'quick' (~15s) or 'deep' (~60s with claim verification)
   */
  analyzeManipulation: async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: {
      mode?: AnalysisMode
      verifyClaims?: boolean
      includeSegments?: boolean
      videoTitle?: string
      videoAuthor?: string
    }
  ): Promise<ManipulationAnalysisResult> => {
    const response = await api.post<ManipulationAnalysisResult>('/api/analysis/manipulation', {
      transcript,
      transcript_data: transcriptData,
      analysis_mode: options?.mode ?? 'quick',
      verify_claims: options?.verifyClaims ?? false,
      include_segments: options?.includeSegments ?? true,
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
   * Get the complete rhetorical toolkit reference (v1.0)
   */
  getToolkit: async (): Promise<any> => {
    const response = await api.get('/api/analysis/toolkit')
    return response.data
  },

  /**
   * Get the manipulation toolkit reference (v2.0)
   * Includes 5 dimensions and 34 manipulation techniques
   */
  getManipulationToolkit: async (): Promise<ManipulationToolkit> => {
    const response = await api.get<ManipulationToolkit>('/api/analysis/manipulation/toolkit')
    return response.data
  },

  /**
   * Get manipulation toolkit as text summary
   */
  getManipulationToolkitSummary: async (): Promise<string> => {
    const response = await api.get<{ summary: string }>('/api/analysis/manipulation/toolkit/summary')
    return response.data.summary
  },

  /**
   * Get details about a specific rhetorical technique
   */
  getTechniqueDetails: async (techniqueId: string): Promise<any> => {
    const response = await api.get(`/api/analysis/techniques/${techniqueId}`)
    return response.data
  },

  /**
   * Get details about a specific manipulation technique
   */
  getManipulationTechniqueDetails: async (techniqueId: string): Promise<ManipulationTechnique> => {
    const response = await api.get<ManipulationTechnique>(`/api/analysis/manipulation/techniques/${techniqueId}`)
    return response.data
  },

  /**
   * Get details about a specific analysis dimension
   */
  getDimensionDetails: async (dimensionId: string): Promise<DimensionDefinition> => {
    const response = await api.get<DimensionDefinition>(`/api/analysis/manipulation/dimensions/${dimensionId}`)
    return response.data
  },

  /**
   * Content summary analysis (~10s) - extracts key concepts, TLDR, technical details
   * Optimized for note-taking and Obsidian export
   */
  analyzeSummary: async (
    transcript: string,
    transcriptData?: TranscriptSegment[],
    options?: {
      videoTitle?: string
      videoAuthor?: string
      videoId?: string
      videoUrl?: string
    }
  ): Promise<ContentSummaryResult> => {
    const response = await api.post<ContentSummaryResult>('/api/analysis/summary', {
      transcript,
      transcript_data: transcriptData,
      video_title: options?.videoTitle,
      video_author: options?.videoAuthor,
      video_id: options?.videoId,
      video_url: options?.videoUrl
    })
    return response.data
  },

  /**
   * Discovery Mode analysis (~30s) - Kinoshita Pattern for cross-domain knowledge transfer
   * Extracts problems, techniques, cross-domain applications, and research trail
   */
  analyzeDiscovery: async (
    options: {
      source?: string
      sourceType?: ContentSourceType
      videoId?: string
      focusDomains?: string[]
      maxApplications?: number
    }
  ): Promise<DiscoveryResult> => {
    const response = await api.post<DiscoveryResult>('/api/analysis/discovery', {
      source: options.source,
      source_type: options.sourceType,
      video_id: options.videoId,
      focus_domains: options.focusDomains,
      max_applications: options.maxApplications ?? 5
    })
    return response.data
  }
}

/**
 * Content extraction API for universal content ingestion
 */
export const contentApi = {
  /**
   * Extract content from a URL or text source
   */
  extract: async (
    source: string,
    options?: {
      sourceType?: ContentSourceType
      title?: string
      author?: string
    }
  ): Promise<UnifiedContent> => {
    const response = await api.post<UnifiedContent>('/api/content/extract', {
      source,
      source_type: options?.sourceType,
      title: options?.title,
      author: options?.author
    })
    return response.data
  },

  /**
   * Upload a file for content extraction
   */
  upload: async (
    file: File,
    options?: {
      title?: string
      author?: string
    }
  ): Promise<ContentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams()
    if (options?.title) params.set('title', options.title)
    if (options?.author) params.set('author', options.author)

    const url = params.toString()
      ? `/api/content/upload?${params}`
      : '/api/content/upload'

    const response = await api.post<ContentUploadResponse>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Detect content type without extracting
   */
  detect: async (source: string): Promise<{
    source_type: ContentSourceType
    normalized_source: string
    video_id: string | null
    is_youtube: boolean
    is_url: boolean
    is_file: boolean
  }> => {
    const response = await api.get('/api/content/detect', {
      params: { source }
    })
    return response.data
  }
}

/**
 * Discovery cache API for storing discovery results
 */
export const discoveryCacheApi = {
  /**
   * Save discovery analysis results
   */
  saveDiscovery: async (videoId: string, discoveryResult: DiscoveryResult): Promise<void> => {
    await api.post('/api/cache/discovery', {
      video_id: videoId,
      discovery_result: discoveryResult
    })
  },

  /**
   * Get cached discovery results for a video
   */
  getDiscovery: async (videoId: string): Promise<{ discovery: DiscoveryResult; discovery_date: string } | null> => {
    try {
      const response = await api.get(`/api/cache/discovery/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  }
}

/**
 * Health Observations API for video frame analysis
 * EDUCATIONAL TOOL ONLY - NOT MEDICAL ADVICE
 */
export const healthApi = {
  /**
   * Analyze a video for health observations
   * Extracts frames, filters for human presence, analyzes with Claude vision
   */
  analyzeHealth: async (
    videoUrl: string,
    options?: {
      videoId?: string
      videoTitle?: string
      intervalSeconds?: number
      maxFrames?: number
      skipIfCached?: boolean
    }
  ): Promise<HealthObservationResult> => {
    const response = await api.post<HealthObservationResult>('/api/health/observations', {
      video_url: videoUrl,
      video_id: options?.videoId,
      video_title: options?.videoTitle,
      interval_seconds: options?.intervalSeconds ?? 30,
      max_frames: options?.maxFrames ?? 20,
      skip_if_cached: options?.skipIfCached ?? true
    })
    return response.data
  },

  /**
   * Get cached health observations for a video
   */
  getHealthObservations: async (videoId: string): Promise<HealthObservationResult | null> => {
    try {
      const response = await api.get<HealthObservationResult>(`/api/health/observations/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Check health analysis service status
   */
  getStatus: async (): Promise<{
    status: 'ready' | 'unavailable'
    claude_cli_available: boolean
    disclaimer: string
    message: string
  }> => {
    const response = await api.get('/api/health/status')
    return response.data
  },

  /**
   * Get the full health observation disclaimer
   */
  getDisclaimer: async (): Promise<{
    disclaimer: string
    version: string
    important_notes: string[]
  }> => {
    const response = await api.get('/api/health/disclaimer')
    return response.data
  }
}
