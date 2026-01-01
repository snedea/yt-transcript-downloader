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

// ==========================================
// Manipulation Analysis Types (v2.0)
// ==========================================

export type AnalysisMode = 'quick' | 'deep'

export type ClaimType = 'factual' | 'causal' | 'normative' | 'prediction' | 'prescriptive'

export type VerificationStatus = 'verified' | 'disputed' | 'unverified' | 'unverifiable'

export type DimensionType =
  | 'epistemic_integrity'
  | 'argument_quality'
  | 'manipulation_risk'
  | 'rhetorical_craft'
  | 'fairness_balance'

export type ManipulationSeverity = 'low' | 'medium' | 'high'

export type TechniqueCategory = 'language' | 'reasoning' | 'propaganda'

// Dimension score for each of the 5 analysis dimensions
export interface DimensionScore {
  dimension: DimensionType
  dimension_name: string
  score: number  // 0-100
  confidence: number
  explanation: string
  red_flags: string[]
  strengths: string[]  // Backend sends 'strengths'
  green_flags?: string[]  // Alias for strengths (optional)
  key_examples: string[]
}

// Detected claims with optional verification
export interface DetectedClaim {
  claim_text: string
  claim_type: ClaimType
  confidence: number
  segment_index: number
  span: [number, number]
  verification_status?: VerificationStatus
  verification_details?: string
  supporting_sources?: string[]
  contradicting_sources?: string[]
}

// Per-segment manipulation technique annotations
export interface SegmentAnnotation {
  technique_id: string
  technique_name: string
  category: TechniqueCategory
  span: [number, number]
  label: string
  confidence: number
  explanation: string
  severity: ManipulationSeverity
}

// Analyzed segment with claims and annotations
export interface AnalyzedSegment {
  segment_index: number
  start_time: number
  end_time: number
  text: string
  claims: DetectedClaim[]
  annotations: SegmentAnnotation[]
}

// Summary of most-used manipulation devices
export interface DeviceSummary {
  device_id: string
  device_name: string
  category: TechniqueCategory
  count: number
  severity: ManipulationSeverity
  examples: string[]  // Example occurrences from transcript
}

// Complete manipulation analysis result
export interface ManipulationAnalysisResult {
  // Core scores
  overall_score: number
  overall_grade: LetterGrade

  // 5 Dimension scores
  dimension_scores: Record<DimensionType, DimensionScore>

  // Segment-level analysis
  segments: AnalyzedSegment[]

  // Claim analysis
  detected_claims: DetectedClaim[]
  verified_claims: DetectedClaim[]
  total_claims: number
  verified_claims_count: number

  // Summaries
  top_concerns: string[]
  top_strengths: string[]
  most_used_devices: DeviceSummary[]

  // Dual interpretations
  charitable_interpretation: string
  concerning_interpretation: string

  // Executive summary
  executive_summary: string

  // Metadata
  analysis_version: string  // "2.0"
  analysis_mode: AnalysisMode
  tokens_used: number
  analysis_duration_seconds: number
  transcript_word_count: number

  // Legacy compatibility (optional pillar scores)
  pillar_scores?: PillarScore[]
  technique_matches?: TechniqueMatch[]
  technique_summary?: TechniqueSummary[]
  quote_matches?: QuoteMatch[]
}

// Request for manipulation analysis
export interface ManipulationAnalysisRequest {
  transcript: string
  transcript_data?: TranscriptSegment[]
  analysis_mode: AnalysisMode
  verify_claims?: boolean
  include_segments?: boolean
  video_title?: string
  video_author?: string
}

// Progress tracking for deep mode
export interface AnalysisProgress {
  phase: 'claim_extraction' | 'manipulation_scan' | 'dimension_scoring' | 'claim_verification' | 'synthesis'
  phase_name: string
  progress: number  // 0-100
  message: string
}

// Manipulation toolkit types
export interface DimensionDefinition {
  id: DimensionType
  name: string
  description: string
  weight: number
  red_flags: string[]
  green_flags: string[]
  scoring_guide: string
}

export interface ManipulationTechnique {
  id: string
  name: string
  category: TechniqueCategory
  description: string
  severity: ManipulationSeverity
  examples: string[]
  detection_hints: string[]
}

export interface ManipulationToolkit {
  dimensions: Record<DimensionType, DimensionDefinition>
  language_techniques: Record<string, ManipulationTechnique>
  reasoning_techniques: Record<string, ManipulationTechnique>
  propaganda_techniques: Record<string, ManipulationTechnique>
}
