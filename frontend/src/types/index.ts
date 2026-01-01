export interface Video {
  id: string
  title: string
  thumbnail: string
  duration: number
}

export interface TranscriptSegment {
  text: string
  start: number
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
  transcript_data?: TranscriptSegment[]
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
  transcript_data?: TranscriptSegment[]
  cached?: boolean
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

// Rhetorical Analysis Types

export type TechniqueStrength = 'strong' | 'moderate' | 'subtle'

export type SourceType = 'religious' | 'political' | 'literary' | 'philosophical' | 'scientific' | 'unknown'

export type PillarType = 'logos' | 'pathos' | 'ethos' | 'kairos'

export type LetterGrade = 'A+' | 'A' | 'A-' | 'B+' | 'B' | 'B-' | 'C+' | 'C' | 'C-' | 'D' | 'F'

export interface TechniqueMatch {
  technique_id: string
  technique_name: string
  category: string
  phrase: string
  start_time?: number
  end_time?: number
  explanation: string
  strength: TechniqueStrength
  context?: string
}

export interface QuoteMatch {
  phrase: string
  is_quote: boolean
  confidence: number
  source?: string
  source_type?: SourceType
  verified: boolean
  verification_details?: string
  start_time?: number
}

export interface PillarScore {
  pillar: PillarType
  pillar_name: string
  score: number
  explanation: string
  contributing_techniques: string[]
  key_examples: string[]
}

export interface TechniqueSummary {
  technique_id: string
  technique_name: string
  category: string
  count: number
  strongest_example: string
}

export interface AnalysisResult {
  overall_score: number
  overall_grade: LetterGrade
  pillar_scores: PillarScore[]
  technique_matches: TechniqueMatch[]
  technique_summary: TechniqueSummary[]
  total_techniques_found: number
  unique_techniques_used: number
  quote_matches: QuoteMatch[]
  total_quotes_found: number
  verified_quotes: number
  executive_summary: string
  strengths: string[]
  areas_for_improvement: string[]
  tokens_used: number
  analysis_duration_seconds: number
  transcript_word_count: number
}

export interface AnalysisRequest {
  transcript: string
  transcript_data?: TranscriptSegment[]
  verify_quotes?: boolean
  video_title?: string
  video_author?: string
}

export interface AnalysisStatus {
  status: 'ready' | 'unavailable'
  services: {
    openai: boolean
    searxng: boolean
    ready: boolean
  }
  message: string
}
