# Transcript Manipulation Analyzer - Implementation Progress

## Feature Overview

Extending the YouTube Transcript Downloader with a comprehensive **Transcript Manipulation Analyzer** that provides:

- **5 Analysis Dimensions** (vs current 4 rhetorical pillars)
- **User-selectable depth** (Quick ~15s vs Deep ~60s)
- **Claim verification** via SearXNG
- **Segment-level annotations** with manipulation technique tagging
- **Backward compatible** with existing cached analyses

---

## The 5 Analysis Dimensions

| Dimension | Score Meaning | Key Indicators |
|-----------|---------------|----------------|
| **Epistemic Integrity** | Scholarly rigor | Uncertainty acknowledgment, sources, base rates, clear definitions |
| **Argument Quality** | Logical coherence | Claim-evidence fit, fallacies, hidden premises, valid reasoning |
| **Manipulation Risk** | Coercion level (inverted) | Fear+urgency, identity capture, loaded language, conspiracy rhetoric |
| **Rhetorical Craft** | Style effectiveness (neutral) | Ethos/Pathos/Logos balance, devices, framing |
| **Fairness/Balance** | Even-handedness | Counterarguments, steelman vs strawman, consistent standards |

---

## Implementation Status

### ✅ COMPLETED - Sprint 1: Backend Foundation

#### 1. `backend/app/models/manipulation_analysis.py` (NEW)
Complete data models for the enhanced analysis:
- `ClaimType` enum (factual, causal, normative, prediction, prescriptive)
- `VerificationStatus` enum (verified, disputed, unverified, unverifiable)
- `DetectedClaim` - Claims with verification status
- `SegmentAnnotation` - Per-segment manipulation technique annotations
- `AnalyzedSegment` - Segment with claims and annotations
- `DimensionScore` - Score for each of 5 dimensions
- `DeviceSummary` - Summary of manipulation devices found
- `ManipulationAnalysisResult` - Complete analysis result
- `ManipulationAnalysisRequest` - Request with mode selection
- Helper functions: `calculate_overall_score()`, `score_to_grade()`

#### 2. `backend/app/data/manipulation_toolkit.py` (NEW)
Comprehensive detection toolkit:
- `DIMENSION_DEFINITIONS` - 5 dimensions with red/green flags
- `LANGUAGE_TECHNIQUES` - 8 techniques (vagueness_shield, certainty_inflation, passive_voice_hiding, presupposition, category_smuggling, motte_and_bailey, loaded_language, nominalization)
- `REASONING_TECHNIQUES` - 12 techniques (false_dilemma, strawman, ad_hominem, post_hoc, slippery_slope, whataboutism, appeal_to_authority, base_rate_neglect, anecdote_laundering, moving_goalposts, burden_shift, non_sequitur)
- `PROPAGANDA_TECHNIQUES` - 14 techniques (bandwagon, scapegoating, fear_salvation, identity_capture, outgroup_demonization, glittering_generalities, transfer, testimonial, plain_folks, pre_bunking, conspiracy_rhetoric, urgency_scarcity, us_vs_them, moral_outrage)
- Helper functions: `get_manipulation_toolkit_summary()`, `get_full_prompt_reference()`

#### 3. `backend/app/models/analysis.py` (UPDATED)
Added v2.0 optional fields for backward compatibility:
- `analysis_version` - "1.0" (rhetorical) or "2.0" (manipulation)
- `analysis_mode` - "quick" or "deep"
- `dimension_scores` - Dict of 5 dimension scores
- `segments` - List of analyzed segments
- `detected_claims`, `verified_claims` - Claim analysis
- `top_concerns`, `top_strengths`, `most_used_devices` - Enhanced summary
- `charitable_interpretation`, `concerning_interpretation` - Dual interpretations
- Updated `AnalysisRequest` with `analysis_mode`, `verify_claims`, `include_segments`

---

### ✅ COMPLETED - Sprint 2: Backend Services

#### 4. `backend/app/services/manipulation_pipeline.py` (NEW)
Complete analysis pipeline orchestrator:
- `ManipulationAnalysisPipeline` class with Quick and Deep modes
- Quick mode: Single comprehensive GPT-4 call (~15s)
- Deep mode: Multi-pass pipeline with claim extraction, manipulation scan, dimension scoring
- Full JSON schema for GPT response validation
- Integration with web search for claim verification

#### 5. `backend/app/services/web_search.py` (EXTENDED)
Added claim verification methods:
- `ClaimVerificationResult` dataclass
- `verify_claim(claim_text: str)` - Single claim verification via SearXNG
- `verify_claims_batch(claims: List, rate_limit_delay)` - Batch verification
- `_search_claim()` - Search for evidence about claims
- `_parse_claim_results()` - Determine verified/disputed/unverified status
- Fact-checking site weighting (Snopes, PolitiFact, FactCheck.org, etc.)

#### 6. `backend/app/routers/analysis.py` (EXTENDED)
Added manipulation analysis endpoints:
- `POST /api/analysis/manipulation` - Enhanced 5-dimension analysis
- `GET /api/analysis/manipulation/toolkit` - Full toolkit reference
- `GET /api/analysis/manipulation/toolkit/summary` - Text summary
- `GET /api/analysis/manipulation/dimensions/{dimension_id}` - Dimension details
- `GET /api/analysis/manipulation/techniques/{technique_id}` - Technique details

---

### ✅ COMPLETED - Dark Mode Fix

#### 7. Analysis Components (UPDATED)
All existing analysis components updated with dark mode support:
- `RhetoricalAnalysis.tsx` - Main container, header, tabs, footer
- `ScoreGauge.tsx` - Gauge backgrounds, labels
- `PillarChart.tsx` - Bar charts, detail cards
- `TechniqueList.tsx` - Tables, filters, cards, summary stats
- `QuoteAnalysis.tsx` - Quote cards, status badges, table view

---

### ✅ COMPLETED - Sprint 3: Frontend Foundation

#### 8. `frontend/src/types/index.ts` (UPDATED)
Added TypeScript types:
- `AnalysisMode`, `ClaimType`, `DimensionType`, `VerificationStatus`
- `DimensionScore`, `DetectedClaim`, `SegmentAnnotation`
- `AnalyzedSegment`, `DeviceSummary`
- `ManipulationAnalysisResult`, `ManipulationAnalysisRequest`
- `AnalysisProgress`, `DimensionDefinition`, `ManipulationTechnique`, `ManipulationToolkit`

#### 9. `frontend/src/services/api.ts` (UPDATED)
Added API methods:
- `analyzeManipulation()` - Call new endpoint with mode selection
- `getManipulationToolkit()` - Get full toolkit reference
- `getManipulationToolkitSummary()` - Get text summary
- `getManipulationTechniqueDetails()` - Get technique details
- `getDimensionDetails()` - Get dimension details

#### 10. `frontend/src/hooks/useManipulationAnalysis.ts` (CREATED)
New hook with:
- Quick/Deep mode selection
- Progress tracking for Deep mode
- Cache integration
- `useAnalysisEstimate()` helper for time estimates

---

### ✅ COMPLETED - Sprint 4: Frontend Components

#### 11. New Components (CREATED)
- `AnalysisModeSelector.tsx` - Quick/Deep mode toggle with feature lists
- `AnalysisProgressBar` - Progress display for Deep mode
- `CompactModeSelector` - Inline mode toggle for headers
- `DimensionScores.tsx` - 5-dimension score cards with expandable details
- `DimensionRadar.tsx` - SVG spider chart for dimensions
- `ClaimsPanel.tsx` - Claims list with type/verification filtering
- `ClaimsSummary` - Compact claims summary
- `ManipulationAnalysis.tsx` - Complete v2.0 analysis display with tabs

#### 12. Updated Components
- `TranscriptDisplay.tsx` - Added analysis type toggle (Manipulation/Rhetorical), mode selector, progress display

---

### ⏳ PENDING - Sprint 5: Polish

#### 13. UI/UX
- ~~**Dark mode support** for all analysis components~~ ✅ DONE
- ~~Progress indicators for Deep mode~~ ✅ DONE
- Deep mode argument graph visualization (optional enhancement)
- SegmentViewer.tsx - Interactive transcript with annotations (optional enhancement)

---

## File Structure

```
backend/app/
├── data/
│   ├── rhetorical_toolkit.py      # Existing - 37 rhetorical techniques
│   └── manipulation_toolkit.py    # NEW - 5 dimensions, 34 manipulation techniques
├── models/
│   ├── analysis.py                # UPDATED - v2.0 optional fields added
│   ├── manipulation_analysis.py   # NEW - Complete v2.0 models
│   └── cache.py                   # Existing
├── routers/
│   ├── analysis.py                # TO UPDATE - Add /manipulation endpoint
│   └── ...
└── services/
    ├── openai_service.py          # TO UPDATE - Add manipulation analysis methods
    ├── manipulation_pipeline.py   # TO CREATE - Pipeline orchestrator
    ├── web_search.py              # TO UPDATE - Add claim verification
    └── rhetorical_analysis.py     # Existing

frontend/src/
├── components/analysis/
│   ├── RhetoricalAnalysis.tsx     # TO UPDATE - Add new tabs
│   ├── DimensionScores.tsx        # TO CREATE
│   ├── DimensionRadar.tsx         # TO CREATE
│   ├── SegmentViewer.tsx          # TO CREATE
│   ├── ClaimsPanel.tsx            # TO CREATE
│   └── AnalysisModeSelector.tsx   # TO CREATE
├── hooks/
│   ├── useRhetoricalAnalysis.ts   # Existing
│   └── useManipulationAnalysis.ts # TO CREATE
├── types/
│   └── index.ts                   # TO UPDATE
└── services/
    └── api.ts                     # TO UPDATE
```

---

## Key Design Decisions

1. **Backward Compatibility**: New fields are optional in `AnalysisResult`, existing cached analyses still work
2. **Unified Analysis**: Single endpoint with mode selection, not separate endpoints
3. **Inverted Manipulation Risk**: Low manipulation = high contribution to overall score
4. **Dual Interpretations**: Provides both charitable and concerning readings
5. **Dark Mode**: All components must support dark mode (current issue being fixed)

---

## Continuation Prompt

```
The Transcript Manipulation Analyzer feature is now COMPLETE for the YouTube Transcript Downloader project.

STATUS: All sprints (1-4) are COMPLETE. The feature is ready for testing.

COMPLETED BACKEND FILES:
- backend/app/models/manipulation_analysis.py - Full data models
- backend/app/data/manipulation_toolkit.py - 5 dimensions, 34 techniques
- backend/app/models/analysis.py - Updated with v2.0 optional fields
- backend/app/services/manipulation_pipeline.py - Full Quick/Deep mode pipeline
- backend/app/services/web_search.py - Extended with claim verification
- backend/app/routers/analysis.py - Extended with /manipulation endpoints

COMPLETED FRONTEND FILES:
- frontend/src/types/index.ts - All manipulation analysis types added
- frontend/src/services/api.ts - analyzeManipulation() and toolkit methods
- frontend/src/hooks/useManipulationAnalysis.ts - Hook with progress tracking
- frontend/src/components/analysis/AnalysisModeSelector.tsx - Quick/Deep mode toggle
- frontend/src/components/analysis/DimensionScores.tsx - 5-dimension score cards + radar chart
- frontend/src/components/analysis/ClaimsPanel.tsx - Claims list with verification status
- frontend/src/components/analysis/ManipulationAnalysis.tsx - Complete v2.0 analysis display
- frontend/src/components/TranscriptDisplay.tsx - Updated with analysis type toggle

OPTIONAL ENHANCEMENTS (Sprint 5):
- SegmentViewer.tsx - Interactive transcript with clickable annotations
- ArgumentGraph.tsx - Toulmin argument structure visualization
- Export to PDF/Markdown for manipulation analysis reports

TO TEST:
1. Start the backend: cd backend && uvicorn app.main:app --reload
2. Start the frontend: cd frontend && npm run dev
3. Fetch a transcript and click "Manipulation Analysis" > "Quick Analysis" or "Deep Analysis"
```

---

## References

- Plan file: `~/.claude/plans/virtual-sniffing-pnueli.md`
- Original framework: User-provided "toolkit map" (psychology + rhetoric + argumentation + discourse analysis)
- Existing rhetorical analysis: `backend/app/services/rhetorical_analysis.py`
