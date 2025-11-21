# API Documentation

This document describes the REST API endpoints provided by the YouTube Transcript Downloader backend.

## Base URL

- **Development:** `http://localhost:8000`
- **API Docs (Swagger UI):** `http://localhost:8000/docs`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding API key authentication.

## Endpoints

### Health Check

Check if the API server is running.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Get Single Transcript

Fetch the transcript for a single YouTube video.

```http
POST /api/transcript/single
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "clean": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video_url` | string | Yes | YouTube video URL or video ID |
| `clean` | boolean | No | Apply AI cleaning (default: false) |

**Success Response (200):**
```json
{
  "transcript": "Full transcript text here...",
  "video_title": "Rick Astley - Never Gonna Give You Up",
  "video_id": "dQw4w9WgXcQ",
  "tokens_used": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `transcript` | string | The full transcript text |
| `video_title` | string | Title of the video |
| `video_id` | string | YouTube video ID |
| `tokens_used` | integer | OpenAI tokens used (0 if not cleaned) |

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Invalid URL format |
| 404 | Transcript not found or disabled |
| 500 | Internal server error |

**Example:**
```bash
curl -X POST http://localhost:8000/api/transcript/single \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "clean": false}'
```

---

### Clean Transcript with AI

Clean an existing transcript using GPT-4o-mini.

```http
POST /api/transcript/clean
Content-Type: application/json
```

**Request Body:**
```json
{
  "transcript": "uh so today we're gonna talk about um you know programming..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transcript` | string | Yes | Raw transcript text to clean |

**Success Response (200):**
```json
{
  "cleaned_transcript": "Today we're going to talk about programming...",
  "tokens_used": 150
}
```

| Field | Type | Description |
|-------|------|-------------|
| `cleaned_transcript` | string | AI-cleaned transcript |
| `tokens_used` | integer | OpenAI tokens consumed |

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Empty transcript provided |
| 503 | OpenAI API unavailable or key not configured |

**Example:**
```bash
curl -X POST http://localhost:8000/api/transcript/clean \
  -H "Content-Type: application/json" \
  -d '{"transcript": "uh so today we are gonna um talk about coding"}'
```

---

### Get Playlist Videos

Extract the list of videos from a YouTube playlist or channel.

```http
POST /api/playlist/videos
Content-Type: application/json
```

**Request Body:**
```json
{
  "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `playlist_url` | string | Yes | YouTube playlist or channel URL |

**Success Response (200):**
```json
{
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
      "duration": "3:33"
    },
    {
      "id": "abc123xyz",
      "title": "Another Video Title",
      "thumbnail": "https://i.ytimg.com/vi/abc123xyz/default.jpg",
      "duration": "10:45"
    }
  ],
  "total": 2,
  "playlist_title": "My Playlist"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `videos` | array | List of video objects |
| `videos[].id` | string | YouTube video ID |
| `videos[].title` | string | Video title |
| `videos[].thumbnail` | string | Thumbnail URL |
| `videos[].duration` | string | Video duration (MM:SS or HH:MM:SS) |
| `total` | integer | Total number of videos |
| `playlist_title` | string | Name of the playlist |

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Invalid playlist URL |
| 404 | Playlist not found or private |
| 500 | yt-dlp extraction failed |

**Example:**
```bash
curl -X POST http://localhost:8000/api/playlist/videos \
  -H "Content-Type: application/json" \
  -d '{"playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"}'
```

---

### Bulk Download Transcripts

Download transcripts for multiple videos at once.

```http
POST /api/transcript/bulk
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_ids": ["dQw4w9WgXcQ", "abc123xyz", "def456uvw"],
  "clean": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video_ids` | array | Yes | List of YouTube video IDs |
| `clean` | boolean | No | Apply AI cleaning to all (default: false) |

**Success Response (200):**
```json
{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "video_title": "Rick Astley - Never Gonna Give You Up",
      "transcript": "Full transcript...",
      "status": "success",
      "tokens_used": 0
    },
    {
      "video_id": "abc123xyz",
      "video_title": "Another Video",
      "transcript": null,
      "status": "failed",
      "error": "Transcripts disabled",
      "tokens_used": 0
    }
  ],
  "total": 2,
  "successful": 1,
  "failed": 1,
  "total_tokens": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | List of result objects |
| `results[].video_id` | string | YouTube video ID |
| `results[].video_title` | string | Video title (if available) |
| `results[].transcript` | string/null | Transcript text or null if failed |
| `results[].status` | string | "success" or "failed" |
| `results[].error` | string | Error message (if failed) |
| `results[].tokens_used` | integer | Tokens used for this video |
| `total` | integer | Total videos processed |
| `successful` | integer | Number of successful downloads |
| `failed` | integer | Number of failed downloads |
| `total_tokens` | integer | Total OpenAI tokens used |

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Empty video_ids array |
| 500 | Internal server error |

**Example:**
```bash
curl -X POST http://localhost:8000/api/transcript/bulk \
  -H "Content-Type: application/json" \
  -d '{"video_ids": ["dQw4w9WgXcQ", "abc123xyz"], "clean": false}'
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "video_url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default:** 100 requests per minute per IP
- **Bulk endpoint:** Counts as 1 request regardless of video count
- **Header:** `X-RateLimit-Remaining` shows remaining requests

When rate limited, you'll receive:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```
Status code: 429

## Supported URL Formats

The API accepts various YouTube URL formats:

**Single Videos:**
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (just the ID)

**Playlists:**
- `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`

**Channels:**
- `https://www.youtube.com/@username/videos`
- `https://www.youtube.com/channel/CHANNEL_ID/videos`
- `https://www.youtube.com/c/channelname/videos`

## OpenAI Token Usage

When using AI cleaning (`clean: true`):

- **Model:** GPT-4o-mini
- **Cost:** ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Typical usage:** 500-2000 tokens per transcript

Token usage is tracked and returned in responses to help monitor costs.

## Best Practices

1. **Batch requests:** Use bulk endpoint for multiple videos
2. **Handle errors:** Always check for failed results in bulk responses
3. **Rate limiting:** Implement exponential backoff on 429 responses
4. **Clean selectively:** Only use AI cleaning when needed to save costs
5. **Cache results:** Store transcripts locally to avoid re-fetching
