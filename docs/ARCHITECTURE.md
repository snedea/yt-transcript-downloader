# Architecture Documentation

This document describes the system architecture of Faceteer.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Pages     │  │ Components  │  │     Custom Hooks        │  │
│  │  (App Dir)  │  │   (React)   │  │  (State Management)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                │                                 │
│                         Axios API Client                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ REST API (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Routers   │  │  Services   │  │       Utilities         │  │
│  │ (Endpoints) │  │  (Business) │  │   (Helpers/Parsers)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │ YouTube  │ │  OpenAI  │ │  yt-dlp  │
             │   API    │ │   API    │ │  (CLI)   │
             └──────────┘ └──────────┘ └──────────┘
```

## Frontend Architecture

### Technology Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI component library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

### Directory Structure

```
frontend/src/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/             # React components
│   ├── SingleDownload.tsx  # Single video UI
│   ├── BulkDownload.tsx    # Bulk download UI
│   ├── VideoSelector.tsx   # Video selection list
│   ├── TranscriptDisplay.tsx # Transcript viewer
│   ├── ProgressBar.tsx     # Progress indicator
│   └── ErrorMessage.tsx    # Error display
├── hooks/                  # Custom React hooks
│   ├── useTranscript.ts    # Single transcript logic
│   └── useBulkDownload.ts  # Bulk download logic
├── services/               # API integration
│   └── api.ts              # Axios client
└── types/                  # TypeScript definitions
    └── index.ts            # Shared interfaces
```

### Component Hierarchy

```
App (layout.tsx)
└── Page (page.tsx)
    ├── Tab Navigation
    ├── SingleDownload
    │   ├── URL Input
    │   ├── Options (Clean with AI)
    │   └── TranscriptDisplay
    │       ├── Copy Button
    │       └── Download Button
    └── BulkDownload
        ├── URL Input
        ├── VideoSelector
        │   └── VideoItem (multiple)
        ├── ProgressBar
        └── Results
```

### State Management

State is managed through custom React hooks:

**useTranscript Hook:**
```typescript
const {
  transcript,      // Current transcript
  loading,         // Loading state
  error,           // Error message
  fetchTranscript, // Fetch function
  clearTranscript  // Reset function
} = useTranscript();
```

**useBulkDownload Hook:**
```typescript
const {
  videos,          // Video list
  selected,        // Selected video IDs
  progress,        // Download progress
  results,         // Download results
  loadPlaylist,    // Load video list
  downloadSelected // Start bulk download
} = useBulkDownload();
```

## Backend Architecture

### Technology Stack

- **FastAPI** - Modern async Python framework
- **youtube-transcript-api** - YouTube transcript fetching
- **OpenAI** - GPT-4o-mini for cleaning
- **yt-dlp** - Playlist/channel extraction
- **Pydantic** - Data validation

### Directory Structure

```
backend/app/
├── main.py                 # FastAPI application entry
├── config.py               # Configuration management
├── routers/                # API endpoints
│   ├── transcript.py       # Transcript operations
│   └── playlist.py         # Playlist operations
├── services/               # Business logic
│   ├── youtube.py          # YouTube transcript service
│   ├── openai_service.py   # AI cleaning service
│   └── playlist.py         # Playlist extraction
└── utils/                  # Helper functions
    ├── url_parser.py       # URL parsing
    └── validators.py       # Input validation
```

### Request Flow

```
HTTP Request
     │
     ▼
┌─────────────┐
│   Router    │  ← Endpoint handling, request validation
└─────────────┘
     │
     ▼
┌─────────────┐
│  Service    │  ← Business logic, external API calls
└─────────────┘
     │
     ▼
┌─────────────┐
│   Utils     │  ← URL parsing, validation helpers
└─────────────┘
     │
     ▼
HTTP Response
```

### Service Layer Details

**YouTubeService:**
- Instance-based API pattern (per youtube-transcript-api docs)
- Handles transcript fetching with language fallback
- Error handling for missing transcripts

```python
class YouTubeService:
    def __init__(self):
        self.api = YouTubeTranscriptApi()

    async def get_transcript(self, video_id: str) -> str:
        transcript = self.api.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
```

**OpenAIService:**
- API key validation on initialization
- GPT-4o-mini for cost efficiency
- Token usage tracking

```python
class OpenAIService:
    def __init__(self):
        self.client = OpenAI()
        self._validate_api_key()

    async def clean_transcript(self, text: str) -> tuple[str, int]:
        response = await self.client.chat.completions.create(...)
        return response.choices[0].message.content, response.usage.total_tokens
```

**PlaylistService:**
- Uses yt-dlp for reliable extraction
- Supports playlists and channels
- Returns video metadata (title, thumbnail, duration)

## Data Flow

### Single Transcript Download

```
1. User enters YouTube URL
2. Frontend sends POST /api/transcript/single
3. Backend parses URL → extracts video_id
4. YouTubeService fetches transcript
5. (Optional) OpenAIService cleans transcript
6. Response returned to frontend
7. User can copy/download result
```

### Bulk Playlist Download

```
1. User enters playlist URL
2. Frontend sends POST /api/playlist/videos
3. PlaylistService extracts video list via yt-dlp
4. Frontend displays video list with checkboxes
5. User selects videos and clicks download
6. Frontend sends POST /api/transcript/bulk
7. Backend processes videos in parallel (asyncio.gather)
8. Progress updates sent to frontend
9. User downloads individual or batch results
```

## Error Handling

### Frontend Errors

```typescript
try {
  const response = await api.getTranscript(url);
  setTranscript(response.data);
} catch (error) {
  if (axios.isAxiosError(error)) {
    setError(error.response?.data?.detail || "Failed to fetch transcript");
  }
}
```

### Backend Errors

```python
@router.post("/transcript/single")
async def get_transcript(request: TranscriptRequest):
    try:
        transcript = await youtube_service.get_transcript(video_id)
        return {"transcript": transcript}
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts disabled for this video")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript available")
```

## Security Considerations

### API Key Protection

- OpenAI API key stored in `.env` (not committed)
- Key validated on startup
- Graceful degradation if key missing

### CORS Configuration

```python
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation

- Pydantic models validate all requests
- URL parsing sanitizes input
- Rate limiting prevents abuse

## Performance Optimizations

### Backend

1. **Async/Await** - Non-blocking I/O operations
2. **Parallel Processing** - `asyncio.gather` for bulk downloads
3. **Connection Pooling** - Reused HTTP connections

### Frontend

1. **React 18 Features** - Concurrent rendering
2. **Memoization** - `useMemo`/`useCallback` for expensive operations
3. **Lazy Loading** - Components loaded on demand

## Deployment Considerations

### Development

```bash
# Backend
uvicorn app.main:app --reload --port 8000

# Frontend
npm run dev
```

### Production

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
npm run build
npm run start
```

### Environment Variables

| Environment | Backend Port | Frontend Port | Debug |
|-------------|-------------|---------------|-------|
| Development | 8000 | 3000 | True |
| Production | 8000 | 3000 | False |

## Future Improvements

1. **Caching** - Redis for frequently accessed transcripts
2. **Queue System** - Celery/RQ for background processing
3. **WebSocket** - Real-time progress updates
4. **Database** - Persist transcript history
5. **Authentication** - User accounts and quotas
