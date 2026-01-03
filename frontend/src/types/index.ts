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

// ==========================================
// Content Summary Types (v3.0)
// ==========================================

export type ContentType =
  | 'programming_technical'
  | 'tutorial_howto'
  | 'news_current_events'
  | 'educational'
  | 'entertainment'
  | 'discussion_opinion'
  | 'review'
  | 'interview'
  | 'other'

export type TechnicalCategory =
  | 'code_snippet'
  | 'library'
  | 'framework'
  | 'command'
  | 'tool'
  | 'api'
  | 'concept'

export type ImportanceLevel = 'high' | 'medium' | 'low'

export interface KeyConcept {
  concept: string
  explanation: string
  importance: ImportanceLevel
  timestamp?: number
}

export interface TechnicalDetail {
  category: TechnicalCategory
  name: string
  description?: string
  code?: string
  timestamp?: number
}

export interface SummaryActionItem {
  action: string
  context?: string
  priority: ImportanceLevel
}

export interface KeyMoment {
  timestamp: number
  title: string
  description: string
}

// Scholarly Context Types (for educational content)
export interface ScholarlyFigure {
  name: string
  role?: string
  period?: string
  relationships?: string
  significance?: string
}

export interface ScholarlySource {
  name: string
  type?: string
  description?: string
  significance?: string
}

export interface ScholarlyDebate {
  topic: string
  positions: string[]
  evidence?: string
  consensus?: string
}

export interface EvidenceType {
  type: string
  examples: string[]
  significance?: string
}

export interface TimePeriod {
  period: string
  dates?: string
  context?: string
}

export interface ScholarlyContext {
  figures: ScholarlyFigure[]
  sources: ScholarlySource[]
  debates: ScholarlyDebate[]
  evidence_types: EvidenceType[]
  methodology: string[]
  time_periods: TimePeriod[]
}

export interface ContentSummaryResult {
  // Content Type Detection
  content_type: ContentType
  content_type_confidence: number
  content_type_reasoning: string

  // Core Content
  tldr: string
  key_concepts: KeyConcept[]
  technical_details: TechnicalDetail[]
  has_technical_content: boolean
  action_items: SummaryActionItem[]

  // Organization
  keywords: string[]
  suggested_obsidian_tags: string[]

  // Timestamps
  key_moments: KeyMoment[]

  // Scholarly Context (for educational content)
  scholarly_context?: ScholarlyContext

  // Metadata
  tokens_used: number
  analysis_duration_seconds: number
  transcript_word_count: number
}

export interface ContentSummaryRequest {
  transcript: string
  transcript_data?: TranscriptSegment[]
  video_title?: string
  video_author?: string
  video_id?: string
  video_url?: string
}

// ==========================================
// Discovery Mode Types (v4.0 - Kinoshita Pattern)
// ==========================================

export type ContentSourceType = 'youtube' | 'pdf' | 'web_url' | 'plain_text' | 'markdown'

/**
 * A problem or goal identified in the content.
 */
export interface Problem {
  problem_id: string
  statement: string
  context: string
  blockers: string[]
  domain: string
  timestamp?: number
}

/**
 * A technique or method described in the content.
 */
export interface Technique {
  technique_id: string
  name: string
  principle: string
  implementation: string
  requirements: string[]
  domain: string
  source?: string
  timestamp?: number
}

/**
 * Potential application of a technique in another domain.
 */
export interface CrossDomainApplication {
  application_id: string
  source_technique: string
  target_domain: string
  hypothesis: string
  potential_problems_solved: string[]
  adaptation_needed: string
  confidence: number
  similar_existing_work?: string
}

/**
 * A reference mentioned or implied in the content.
 */
export interface ResearchReference {
  reference_id: string
  title?: string
  authors: string[]
  year?: number
  domain: string
  relevance: string
  mentioned_at?: number
}

/**
 * A concrete experiment idea with an optimized LLM prompt for execution.
 */
export interface ExperimentIdea {
  experiment_id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  time_estimate: string
  prerequisites: string[]
  success_criteria: string[]
  llm_prompt: string
  related_techniques: string[]
  related_problems: string[]
}

/**
 * Full discovery analysis result using the Kinoshita Pattern.
 */
export interface DiscoveryResult {
  // Content identification
  content_title: string
  source_type: ContentSourceType
  source_id: string
  source_url?: string

  // The Kinoshita Pattern extractions
  problems: Problem[]
  techniques: Technique[]
  cross_domain_applications: CrossDomainApplication[]
  research_trail: ResearchReference[]

  // Synthesis
  key_insights: string[]
  recommended_reads: string[]
  experiment_ideas: ExperimentIdea[]

  // Metadata
  analysis_version: string
  tokens_used: number
  analysis_duration_seconds: number
  analyzed_at: string
}

/**
 * Request for discovery analysis.
 */
export interface DiscoveryRequest {
  source?: string
  source_type?: ContentSourceType
  video_id?: string
  focus_domains?: string[]
  max_applications?: number
}

/**
 * Lightweight summary for library display.
 */
export interface DiscoverySummary {
  source_id: string
  content_title: string
  source_type: ContentSourceType
  problem_count: number
  technique_count: number
  application_count: number
  top_insight?: string
  analyzed_at: string
}

/**
 * Unified content representation from any source.
 */
export interface UnifiedContent {
  text: string
  source_type: ContentSourceType
  source_id: string
  source_url?: string
  title: string
  author?: string
  upload_date?: string
  word_count: number
  character_count: number
  extraction_success: boolean
  extraction_error?: string
}

/**
 * Content extraction request.
 */
export interface ContentExtractionRequest {
  source: string
  source_type?: ContentSourceType
  title?: string
  author?: string
}

/**
 * Response after uploading and extracting content.
 */
export interface ContentUploadResponse {
  success: boolean
  content?: UnifiedContent
  error?: string
}

// ==========================================
// Health Observations Types (v5.0)
// ==========================================

export type BodyRegion = 'face' | 'eyes' | 'skin' | 'hands' | 'neck' | 'posture' | 'other'

export type ObservationSeverity = 'informational' | 'worth_mentioning' | 'consider_checkup'

/**
 * A single health-related observation from a video frame.
 */
export interface HealthObservation {
  observation_id: string
  timestamp: number  // Seconds into video
  body_region: BodyRegion
  observation: string  // Descriptive, not diagnostic
  reasoning: string
  confidence: number  // 0-1
  limitations: string[]
  severity: ObservationSeverity
  related_conditions: string[]  // Educational context only
  references: string[]
}

/**
 * Analysis of a single video frame.
 */
export interface FrameAnalysis {
  frame_id: string
  timestamp: number
  humans_detected: number
  body_regions_visible: BodyRegion[]
  observations: HealthObservation[]
  image_quality_notes: string[]
}

/**
 * Complete health observation result for a video.
 */
export interface HealthObservationResult {
  video_id: string
  video_title: string
  video_url: string

  // Analysis metadata
  frames_extracted: number
  frames_with_humans: number
  frames_analyzed: number

  // Results
  observations: HealthObservation[]
  summary: string
  observations_by_region: Record<string, HealthObservation[]>
  frame_analyses: FrameAnalysis[]

  // Important notes
  limitations: string[]
  disclaimer: string

  // Metadata
  analysis_duration_seconds: number
  analyzed_at: string
  interval_seconds: number
  model_used: string
}

/**
 * Request for health observation analysis.
 */
export interface HealthObservationRequest {
  video_url: string
  video_id?: string
  video_title?: string
  interval_seconds?: number  // 5-120, default 30
  max_frames?: number  // 1-50, default 20
  skip_if_cached?: boolean
}

// ==========================================
// Prompt Generator Types (v6.0)
// ==========================================

export type PromptCategory =
  | 'app_builder'
  | 'research_deep_dive'
  | 'devils_advocate'
  | 'mermaid_diagrams'
  | 'sora'
  | 'nano_banana_pro'
  | 'validation_frameworks'

/**
 * Metadata for each prompt category (UI display).
 */
export interface PromptCategoryInfo {
  name: string
  icon: string
  color: string
  target_tool: string
  description: string
}

/**
 * A single generated prompt with Nate B Jones techniques.
 */
export interface GeneratedPrompt {
  prompt_id: string
  category: PromptCategory
  category_name: string
  category_icon: string
  title: string
  description: string
  prompt_content: string  // 500-2000 words, production-ready
  intent_specification: string
  disambiguation_questions: string[]
  failure_conditions: string[]
  success_criteria: string[]
  video_context_used: string[]
  analysis_context_used: string[]
  target_tool: string
  estimated_output_type: string
  word_count: number
}

/**
 * Complete result from prompt generation.
 */
export interface PromptGeneratorResult {
  content_title: string
  source_id?: string
  source_url?: string
  prompts: GeneratedPrompt[]
  prompts_by_category: Record<string, GeneratedPrompt>
  total_prompts: number
  total_word_count: number
  input_word_count: number
  analysis_types_used: string[]
  analysis_version: string
  tokens_used: number
  analysis_duration_seconds: number
  generated_at: string
  model_used: string
}

/**
 * Request for prompt generation.
 */
export interface PromptGeneratorRequest {
  transcript?: string
  video_id?: string
  source_text?: string
  source_url?: string
  include_discovery?: boolean
  include_summary?: boolean
  include_manipulation?: boolean
  categories?: PromptCategory[]
  video_title?: string
  video_author?: string
}
