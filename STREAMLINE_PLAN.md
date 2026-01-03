# Faceteer UX Streamline - Implementation Plan

## 🎯 Vision

Transform Faceteer from a feature-fragmented tool into a seamless, unified content analysis platform with a single entry point and intelligent content-type detection.

## 📋 Core Principles

1. **Single Entry Point** - One place to input ANY content (URL, PDF, text)
2. **Smart Detection** - App infers intent from input type
3. **Progressive Disclosure** - Show "what next?" after capture, not before
4. **Content-First** - Everything is a tile in your library
5. **Unified History** - All content types in one chronological stream

---

## 🏗️ Architecture Overview

### Current State
```
┌─────────────────────────────────────┐
│  Sidebar Navigation                 │
│  - Library (separate view)          │
│  - New Video (modal)                │
│  - Discovery (separate view)        │
│  - Prompts (separate view)          │
│  - Health (separate view)           │
└─────────────────────────────────────┘
```

### Target State
```
┌─────────────────────────────────────┐
│  Minimal Sidebar                    │
│  - Faceteer (home)                  │
│  - Recent History (10 items)        │
│  - Account Settings                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Main View: Unified Library         │
│  [🔍 Search] [➕]                   │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │ 📄│ │ 🎬│ │ 🌐│ │ 📋│          │
│  │PDF│ │YT │ │Web│ │Txt│          │
│  └───┘ └───┘ └───┘ └───┘          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Content Detail View                │
│  Source: [YouTube/PDF/Web/Text]     │
│                                     │
│  What would you like to do?         │
│  ☑ Summary (done)                   │
│  ☑ Rhetorical Analysis (done)       │
│  ☐ Manipulation Detection           │
│  ☐ Discovery Mode                   │
│  ☐ Prompt Generation                │
│  ☐ Health Observations              │
└─────────────────────────────────────┘
```

---

## 🎨 UI/UX Changes

### 1. Navigation Simplification

**Remove:**
- ❌ Library icon (library IS the home view)
- ❌ "New Video" button (replaced by + modal)
- ❌ Individual feature views in sidebar (Discovery, Prompts, Health)

**Keep:**
- ✅ Faceteer header (click → home)
- ✅ Recent history (10 most recent items)
- ✅ Account/settings

**Add:**
- ➕ Add Content button (next to search)

### 2. Unified Content Entry Modal

**Location:** Triggered by + button next to search bar

**Modal Structure:**
```
┌─────────────────────────────────────┐
│  Add Content                    [X] │
├─────────────────────────────────────┤
│  [URL] [PDF Upload] [Paste Text]   │ ← Tabs
├─────────────────────────────────────┤
│                                     │
│  [Tab Content Here]                 │
│                                     │
│  [Capture Content] ←── Smart button │
└─────────────────────────────────────┘
```

**Tab 1: URL**
- Single input field
- Placeholder: "Paste any URL - YouTube, article, webpage..."
- Smart detection:
  - YouTube → "Fetching transcript..."
  - Article → "Extracting article content..."
  - Wikipedia → "Extracting Wikipedia page..."
- Button text: "Capture Content" or "Fetch" or "Analyze"

**Tab 2: PDF Upload**
- Drag & drop zone
- File picker
- Shows preview of first page after selection
- Optional: Title and Author override fields
- Button text: "Upload & Extract"

**Tab 3: Paste Text**
- Large textarea
- Character count
- Optional: Title field
- Button text: "Save & Analyze"
- **CRITICAL:** Store original text in database (like PDFs)
  - Add `original_text` field to `Transcript` model
  - For text pastes, store in `file_path` as a generated text file
  - Or add new column `raw_content_text` for paste text

**Bulk Download (Advanced):**
- Keep as a 4th tab or collapse into URL tab with "Bulk mode" toggle
- Show when YouTube playlist/channel detected

### 3. Content Detail View Redesign

**Current:** Separate views for each analysis type

**New:** Unified "Content Hub" with progressive actions

```
┌─────────────────────────────────────────────────────┐
│ ← Back to Library                                   │
├─────────────────────────────────────────────────────┤
│ 📄 "Document Title"                                 │
│ Source: YouTube • youtube.com/watch?v=...           │
│ Added: Jan 3, 2026 • 2,450 words                   │
├─────────────────────────────────────────────────────┤
│ 📄 Full Content                                     │
│ [Transcript text here...]                           │
│ [Copy] [Download]                                   │
├─────────────────────────────────────────────────────┤
│ 🎯 Analysis Options                                 │
│                                                     │
│ ✅ Summary                    [View] [Re-run]      │
│    Generated Jan 3, 2026                            │
│                                                     │
│ ✅ Rhetorical Analysis        [View] [Re-run]      │
│    Trust Score: 7.2/10 • Jan 3, 2026               │
│                                                     │
│ ⬜ Manipulation Detection     [Run Analysis]        │
│    Detect persuasion techniques and fallacies       │
│                                                     │
│ ⬜ Discovery Mode             [Run Analysis]        │
│    Extract key topics and themes                    │
│                                                     │
│ ⬜ Prompt Generation          [Run Analysis]        │
│    Generate AI prompts from content                 │
│                                                     │
│ ⬜ Health Observations        [Run Analysis]        │
│    (YouTube videos only)                            │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Checkmarks (✅) for completed analyses
- Show timestamp of last run
- "View" button expands inline or navigates to full view
- "Re-run" option to refresh analysis
- Gray out unavailable options (e.g., Health for PDFs)

### 4. Library View (Home) Enhancements

**Header:**
```
┌─────────────────────────────────────────────────────┐
│ Faceteer                                            │
│ [🔍 Search across all content...    ] [➕ Add]     │
│                                                     │
│ Filters: [💻 Technical] [📝 Tutorial] ...          │
│          [✓ Summary] [✓ Analyzed] [Clear all]      │
└─────────────────────────────────────────────────────┘
```

**Content Cards:**
```
┌──────────────────┐
│  [Thumbnail]     │  ← YouTube thumb, PDF AI thumb, web favicon
│                  │
│  📄 Document     │  ← Source icon (🎬 YT, 📄 PDF, 🌐 Web, 📋 Text)
│  Title           │
│                  │
│  🏷️ tech, ai    │  ← Auto-extracted tags
│  ✅ Summary      │  ← Status badges (what's been done)
│  ✅ Analysis     │
│                  │
│  Jan 3, 2026     │  ← Last accessed
└──────────────────┘
```

**Empty State:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              📦                                     │
│       No content yet                                │
│                                                     │
│  Click [➕] to add your first piece of content:    │
│  • Paste a YouTube URL                             │
│  • Upload a PDF document                            │
│  • Paste text from anywhere                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Phase 1: Backend Preparation

#### 1.1 Data Model Updates

**File:** `backend/app/models/cache.py`

```python
# Add new fields to Transcript model
class Transcript(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Store original pasted text
    raw_content_text: Optional[str] = Field(default=None)
    # Alternative: Store as file and reference path
    raw_content_file_path: Optional[str] = Field(default=None)

    # NEW: Unified content type (not just YouTube)
    content_source_type: str = Field(default="youtube")  # youtube|pdf|web|text
```

**Migration:** Create Alembic migration to add new columns

#### 1.2 Content Extractor Enhancement

**File:** `backend/app/services/content_extractor.py`

Already supports:
- ✅ YouTube
- ✅ PDF
- ✅ Web URLs
- ✅ Plain text

**Add:**
- Store original text for paste text sources
- Generate source_id for pasted text (hash of content)

#### 1.3 Cache Service Updates

**File:** `backend/app/services/cache_service.py`

```python
def save(
    self,
    session: Session,
    video_id: str,
    video_title: str,
    transcript_text: str,
    user_id: str,
    # ... existing params ...

    # NEW params
    content_source_type: str = "youtube",
    raw_content_text: Optional[str] = None,
) -> bool:
    # Save raw_content_text if provided
    # ...
```

#### 1.4 New Endpoint: Unified Content Submission

**File:** `backend/app/routers/content.py`

```python
@router.post("/submit")
async def submit_content_unified(
    content_input: str = Form(...),
    input_type: Optional[str] = Form(None),  # "url", "text" (PDF via /upload)
    title_override: Optional[str] = Form(None),
    save_to_library: bool = Form(True),
    # ...
):
    """
    Unified content submission endpoint.

    Auto-detects:
    - YouTube URLs
    - Web article URLs
    - Plain text

    Returns extracted content + adds to library.
    """
    # Detect content type
    source_type, normalized, video_id = detect_source_type(content_input)

    # Extract content
    content = await extract_content(...)

    # Save to library (cache)
    cache_service.save(...)

    # Return content + library item ID
    return {
        "content": content,
        "library_id": video_id,
        "source_type": source_type
    }
```

### Phase 2: Frontend Restructuring

#### 2.1 Navigation Updates

**File:** `frontend/src/components/layout/Sidebar.tsx`

**Changes:**
- Remove navigation items for Library, Discovery, Prompts, Health
- Keep only:
  - ContentLens header (click → library)
  - No nav items in main area (or just history items)
  - Account footer

**New:**
```tsx
const navItems = [
  // REMOVED: Library, New Video, Discovery, Prompts, Health
  // Navigation happens via:
  // - Click ContentLens → Library (home)
  // - Recent history items shown in sidebar
]

// Add recent history section
<div className="recent-history">
  <h3>Recent</h3>
  {recentItems.map(item => (
    <button onClick={() => onItemSelect(item.id)}>
      <SourceIcon type={item.source_type} />
      <span>{item.title}</span>
    </button>
  ))}
</div>
```

#### 2.2 Create Unified Content Modal

**New File:** `frontend/src/components/content/UnifiedContentModal.tsx`

```tsx
type ContentInputTab = 'url' | 'pdf' | 'text'

interface UnifiedContentModalProps {
  isOpen: boolean
  onClose: () => void
  onContentAdded: (contentId: string) => void
}

export function UnifiedContentModal({ ... }: UnifiedContentModalProps) {
  const [activeTab, setActiveTab] = useState<ContentInputTab>('url')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (activeTab === 'url') {
      // Submit URL
      const response = await api.submitContent({ source: urlInput, type: 'url' })
      onContentAdded(response.library_id)
    } else if (activeTab === 'text') {
      // Submit text
      const response = await api.submitContent({ source: textInput, type: 'text' })
      onContentAdded(response.library_id)
    } else if (activeTab === 'pdf') {
      // Upload PDF
      const response = await api.uploadPDF(pdfFile)
      onContentAdded(response.library_id)
    }
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <h2>Add Content</h2>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="url">URL</Tab>
        <Tab value="pdf">PDF Upload</Tab>
        <Tab value="text">Paste Text</Tab>
      </Tabs>

      {/* Tab Content */}
      {activeTab === 'url' && (
        <URLInputTab
          value={urlInput}
          onChange={setUrlInput}
          onSubmit={handleSubmit}
          loading={loading}
        />
      )}
      {activeTab === 'pdf' && (
        <PDFUploadTab
          file={pdfFile}
          onFileSelect={setPdfFile}
          onSubmit={handleSubmit}
          loading={loading}
        />
      )}
      {activeTab === 'text' && (
        <TextInputTab
          value={textInput}
          onChange={setTextInput}
          onSubmit={handleSubmit}
          loading={loading}
        />
      )}
    </Modal>
  )
}
```

#### 2.3 Update Library View

**File:** `frontend/src/components/library/LibraryView.tsx`

**Changes:**
- Add + button next to search
- Remove "New Video" navigation
- Show all content types (not just videos)
- Update card to show source type icon

```tsx
<div className="library-header">
  <div className="search-bar">
    <SearchBar ... />
    <button
      className="add-content-btn"
      onClick={() => setShowContentModal(true)}
    >
      ➕ Add
    </button>
  </div>
</div>

<UnifiedContentModal
  isOpen={showContentModal}
  onClose={() => setShowContentModal(false)}
  onContentAdded={handleContentAdded}
/>
```

#### 2.4 Update Video Card Component

**File:** `frontend/src/components/library/VideoCard.tsx`

**Rename:** → `ContentCard.tsx`

**Changes:**
- Show source type icon (🎬 YouTube, 📄 PDF, 🌐 Web, 📋 Text)
- Show status badges for completed analyses
- Handle different content types

```tsx
export function ContentCard({ item }: { item: LibraryItem }) {
  return (
    <div className="content-card">
      {/* Thumbnail */}
      <div className="thumbnail">
        {item.thumbnail_path ? (
          <img src={item.thumbnail_path} />
        ) : (
          <SourceTypeIcon type={item.source_type} />
        )}
      </div>

      {/* Content Info */}
      <div className="content-info">
        <div className="source-badge">
          <SourceIcon type={item.source_type} />
          {item.source_type}
        </div>

        <h3>{item.title}</h3>

        {/* Status Badges */}
        <div className="status-badges">
          {item.has_summary && <Badge>✓ Summary</Badge>}
          {item.has_analysis && <Badge>✓ Analysis</Badge>}
          {item.has_discovery && <Badge>✓ Discovery</Badge>}
          {item.has_prompts && <Badge>✓ Prompts</Badge>}
        </div>

        {/* Tags */}
        {item.tags && (
          <div className="tags">
            {item.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
          </div>
        )}

        {/* Metadata */}
        <div className="metadata">
          <span>{formatDate(item.last_accessed)}</span>
          <span>{item.word_count} words</span>
        </div>
      </div>
    </div>
  )
}
```

#### 2.5 Create Content Detail Hub

**New File:** `frontend/src/components/content/ContentDetailHub.tsx`

```tsx
interface ContentDetailHubProps {
  contentId: string
  onBack: () => void
}

export function ContentDetailHub({ contentId, onBack }: ContentDetailHubProps) {
  const { content, analyses, loading } = useContentDetail(contentId)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)

  return (
    <div className="content-detail-hub">
      {/* Header */}
      <div className="header">
        <button onClick={onBack}>← Back</button>
        <h1>{content.title}</h1>
        <SourceBadge type={content.source_type} url={content.source_url} />
        <div className="metadata">
          Added {formatDate(content.created_at)} • {content.word_count} words
        </div>
      </div>

      {/* Full Content */}
      <section className="full-content">
        <h2>📄 Full Content</h2>
        <div className="content-text">{content.text}</div>
        <div className="actions">
          <button>Copy</button>
          <button>Download</button>
        </div>
      </section>

      {/* Analysis Options */}
      <section className="analysis-options">
        <h2>🎯 Analysis Options</h2>

        {/* Summary */}
        <AnalysisCard
          title="Summary"
          status={analyses.summary ? 'completed' : 'pending'}
          timestamp={analyses.summary?.timestamp}
          onView={() => setExpandedSection('summary')}
          onRun={() => runAnalysis('summary')}
        />

        {/* Rhetorical Analysis */}
        <AnalysisCard
          title="Rhetorical Analysis"
          description="5-dimension trust evaluation"
          status={analyses.rhetorical ? 'completed' : 'pending'}
          timestamp={analyses.rhetorical?.timestamp}
          preview={analyses.rhetorical?.trust_score}
          onView={() => setExpandedSection('rhetorical')}
          onRun={() => runAnalysis('rhetorical')}
        />

        {/* Manipulation Detection */}
        <AnalysisCard
          title="Manipulation Detection"
          description="Detect persuasion techniques and fallacies"
          status={analyses.manipulation ? 'completed' : 'pending'}
          timestamp={analyses.manipulation?.timestamp}
          onView={() => setExpandedSection('manipulation')}
          onRun={() => runAnalysis('manipulation')}
        />

        {/* Discovery Mode */}
        <AnalysisCard
          title="Discovery Mode"
          description="Extract key topics and themes"
          status={analyses.discovery ? 'completed' : 'pending'}
          timestamp={analyses.discovery?.timestamp}
          onView={() => setExpandedSection('discovery')}
          onRun={() => runAnalysis('discovery')}
        />

        {/* Prompt Generation */}
        <AnalysisCard
          title="Prompt Generation"
          description="Generate AI prompts from content"
          status={analyses.prompts ? 'completed' : 'pending'}
          timestamp={analyses.prompts?.timestamp}
          onView={() => setExpandedSection('prompts')}
          onRun={() => runAnalysis('prompts')}
        />

        {/* Health Observations (YouTube only) */}
        {content.source_type === 'youtube' && (
          <AnalysisCard
            title="Health Observations"
            description="AI vision analysis of video frames"
            status={analyses.health ? 'completed' : 'pending'}
            timestamp={analyses.health?.timestamp}
            onView={() => setExpandedSection('health')}
            onRun={() => runAnalysis('health')}
          />
        )}
      </section>

      {/* Expanded Analysis View */}
      {expandedSection && (
        <ExpandedAnalysisView
          type={expandedSection}
          data={analyses[expandedSection]}
          onClose={() => setExpandedSection(null)}
        />
      )}
    </div>
  )
}
```

### Phase 3: Code Reuse & Refactoring

#### 3.1 Existing Components to Reuse

**Analysis Components (NO CHANGES):**
- ✅ `RhetoricalAnalysis.tsx` - Reuse as-is in expanded view
- ✅ `ManipulationAnalysis.tsx` - Reuse as-is
- ✅ `ContentSummary.tsx` - Reuse as-is
- ✅ `DiscoveryMode.tsx` - Reuse as-is
- ✅ `PromptGenerator.tsx` - Reuse as-is
- ✅ `HealthObservations.tsx` - Reuse as-is

**Just wire them into the new ContentDetailHub with conditional rendering.**

#### 3.2 Components to Deprecate

**Remove/Archive:**
- ❌ `SingleDownload.tsx` - Replaced by UnifiedContentModal
- ❌ `VideoDetail.tsx` - Replaced by ContentDetailHub
- ❌ Separate view components (DiscoveryView, HealthView, PromptGeneratorView)
  - Keep the analysis components, remove the standalone page wrappers

#### 3.3 API Client Updates

**File:** `frontend/src/services/api.ts`

```typescript
// NEW: Unified content submission
export async function submitContent(input: {
  source: string
  type: 'url' | 'text'
  title?: string
  save_to_library?: boolean
}): Promise<{ content: UnifiedContent; library_id: string }> {
  const formData = new FormData()
  formData.append('content_input', input.source)
  formData.append('input_type', input.type)
  if (input.title) formData.append('title_override', input.title)
  formData.append('save_to_library', String(input.save_to_library ?? true))

  const response = await fetch(`${API_URL}/api/content/submit`, {
    method: 'POST',
    body: formData,
    credentials: 'include'
  })
  return response.json()
}

// Update existing uploadPDF to save to library by default
export async function uploadPDF(
  file: File,
  options?: { title?: string; author?: string; save_to_library?: boolean }
): Promise<ContentUploadResponse> {
  // ... existing code with save_to_library=true by default
}
```

### Phase 4: Main App Integration

**File:** `frontend/src/app/page.tsx`

**Changes:**
- Remove view state management for separate views
- Default to library view always
- ContentDetailHub shown when item selected

```tsx
type ViewType = 'library' | 'detail'

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>('library')
  const [selectedContentId, setSelectedContentId] = useState<string | null>(null)

  return (
    <div className="app">
      <Sidebar
        onHomeClick={() => setCurrentView('library')}
        selectedItemId={selectedContentId}
        onItemSelect={(id) => {
          setSelectedContentId(id)
          setCurrentView('detail')
        }}
      />

      <main>
        {currentView === 'library' ? (
          <LibraryView onItemSelect={(id) => {
            setSelectedContentId(id)
            setCurrentView('detail')
          }} />
        ) : currentView === 'detail' && selectedContentId ? (
          <ContentDetailHub
            contentId={selectedContentId}
            onBack={() => setCurrentView('library')}
          />
        ) : null}
      </main>
    </div>
  )
}
```

---

## 🚀 Implementation Phases

### Phase 1: Backend Foundation (Day 1-2)
1. ✅ Create safety commit (DONE)
2. Add `raw_content_text` field to Transcript model
3. Create Alembic migration
4. Update cache_service.save() to accept raw_content_text
5. Create `/api/content/submit` unified endpoint
6. Update content_extractor to store original text
7. Test all content types (URL, PDF, text) → library

### Phase 2: Frontend Core Components (Day 3-4)
1. Create `UnifiedContentModal.tsx`
   - URL tab
   - PDF upload tab
   - Paste text tab
2. Create `ContentDetailHub.tsx`
   - Full content display
   - Analysis options grid
   - Status badges
3. Rename `VideoCard.tsx` → `ContentCard.tsx`
   - Add source type icons
   - Add status badges
4. Update `api.ts` with new endpoints

### Phase 3: Navigation & Integration (Day 5)
1. Simplify Sidebar
   - Remove old nav items
   - Add recent history section
2. Update LibraryView
   - Add + button
   - Integrate UnifiedContentModal
   - Use ContentCard component
3. Update main page.tsx
   - Remove view state complexity
   - Wire library + detail hub

### Phase 4: Analysis Integration (Day 6)
1. Wire existing analysis components into ContentDetailHub
2. Create AnalysisCard component
3. Create ExpandedAnalysisView wrapper
4. Test each analysis type from detail hub

### Phase 5: Polish & Testing (Day 7)
1. Update button text ("Capture Content", not "Get Transcript")
2. Add empty states
3. Add loading states
4. Test all content types → all analysis types
5. Update README with new UX
6. Create user guide/documentation

### Phase 6: Cleanup & Deploy (Day 8)
1. Remove deprecated components
2. Update routing
3. Run tests
4. Docker rebuild
5. Deploy

---

## 📝 Button Text Recommendations

| Context | Old Text | New Text |
|---------|----------|----------|
| URL input | "Get Transcript" | "Capture Content" |
| PDF upload | "Upload" | "Upload & Extract" |
| Text paste | "Submit" | "Save Content" |
| Bulk | "Download Selected" | "Add to Library" |
| Analysis | "Analyze" | "Run Analysis" |

---

## ✅ Success Criteria

1. **Single Entry Point**: ✅ User can add ANY content via + modal
2. **Smart Detection**: ✅ App auto-detects YouTube/web/text
3. **Progressive Disclosure**: ✅ "What next?" shown AFTER capture
4. **Content-First**: ✅ Everything appears as tile in library
5. **Unified History**: ✅ All content types in one view
6. **Original Text Preserved**: ✅ Pasted text stored for retrieval
7. **Status Visibility**: ✅ Can see what analyses are done
8. **No Duplication**: ✅ Removed redundant entry points

---

## 🔄 Migration Path

### For Existing Users
- No data loss - all existing transcripts remain
- New fields added to database (nullable)
- Old "videos" now called "content items"
- All existing analyses preserved
- Navigation simplified (no feature loss)

### Backwards Compatibility
- Existing API endpoints remain functional
- Old video URLs still work
- Cache structure unchanged (only extended)

---

## 📊 File Change Summary

### Backend Changes
```
MODIFIED:
- backend/app/models/cache.py (add fields)
- backend/app/services/cache_service.py (save raw text)
- backend/app/routers/content.py (add unified endpoint)

CREATED:
- backend/migrations/versions/005_add_raw_content_text.py
```

### Frontend Changes
```
MODIFIED:
- frontend/src/app/page.tsx (simplify views)
- frontend/src/components/layout/Sidebar.tsx (remove nav, add history)
- frontend/src/components/library/LibraryView.tsx (add + button)
- frontend/src/components/library/VideoCard.tsx → ContentCard.tsx
- frontend/src/services/api.ts (new endpoints)

CREATED:
- frontend/src/components/content/UnifiedContentModal.tsx
- frontend/src/components/content/ContentDetailHub.tsx
- frontend/src/components/content/AnalysisCard.tsx
- frontend/src/components/content/ExpandedAnalysisView.tsx

DEPRECATED:
- frontend/src/components/SingleDownload.tsx
- frontend/src/components/VideoDetail.tsx
- frontend/src/components/discovery/DiscoveryView.tsx
- frontend/src/components/health/HealthView.tsx
- frontend/src/components/prompts/PromptGeneratorView.tsx
```

---

## 🎯 Next Steps

1. **Review this plan** with team/user
2. **Get approval** on UX changes
3. **Start Phase 1** (backend foundation)
4. **Iterate** based on feedback

---

**End of Plan**
