# Testing Guide

This document provides testing instructions for the YouTube Transcript Downloader application.

## Prerequisites

- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000
- Valid OpenAI API key configured (optional, for transcript cleaning)

## Quick Start

### Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## API Testing

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"development"}
```

### 2. Single Video Transcript
```bash
curl -X POST http://localhost:8000/api/transcript/single \
  -H 'Content-Type: application/json' \
  -d '{"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","clean":false}'
```

**Expected Response:**
```json
{
  "transcript": "[♪♪♪] ♪ We're no strangers to love ♪...",
  "video_title": "dQw4w9WgXcQ",
  "video_id": "dQw4w9WgXcQ",
  "tokens_used": null
}
```

### 3. Playlist Videos
```bash
curl -X POST http://localhost:8000/api/playlist/videos \
  -H 'Content-Type: application/json' \
  -d '{"playlist_url":"https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"}'
```

**Expected Response:**
```json
{
  "videos": [
    {
      "id": "0VH1Lim8gL8",
      "title": "Deep Learning State of the Art (2020)",
      "thumbnail": "",
      "duration": 5261
    },
    ...
  ]
}
```

### 4. Bulk Transcript Download
```bash
curl -X POST http://localhost:8000/api/transcript/bulk \
  -H 'Content-Type: application/json' \
  -d '{"video_ids":["dQw4w9WgXcQ","jNQXAC9IVRw"],"clean":false}'
```

**Expected Response:**
```json
{
  "results": [...],
  "total": 2,
  "successful": 2,
  "failed": 0
}
```

### 5. Transcript Cleaning (with OpenAI)
```bash
curl -X POST http://localhost:8000/api/transcript/single \
  -H 'Content-Type: application/json' \
  -d '{"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","clean":true}'
```

**Note:** Requires valid OpenAI API key in `.env`

## Frontend Testing

### Manual Testing Checklist

1. **Single Video Download**
   - [ ] Open http://localhost:3000
   - [ ] Click "Single Video" tab
   - [ ] Enter URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - [ ] Click "Get Transcript"
   - [ ] Verify transcript appears
   - [ ] Click "Copy" button and verify clipboard
   - [ ] Click "Download" button and verify .txt file downloads

2. **Transcript Cleaning**
   - [ ] Enter same URL
   - [ ] Check "Clean transcript with AI" checkbox
   - [ ] Click "Get Transcript"
   - [ ] Verify cleaned transcript has better formatting
   - [ ] Verify token usage is displayed

3. **Bulk Download**
   - [ ] Click "Bulk Download" tab
   - [ ] Enter playlist URL: `https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`
   - [ ] Click "Fetch Videos"
   - [ ] Verify video list appears with checkboxes
   - [ ] Select 2-3 videos
   - [ ] Click "Fetch Transcripts"
   - [ ] Verify transcripts are fetched
   - [ ] Select transcripts to download
   - [ ] Click "Download Selected"
   - [ ] Verify files are downloaded

4. **Error Handling**
   - [ ] Test with invalid URL (expect error message)
   - [ ] Test with video without transcript (expect graceful error)
   - [ ] Test with private playlist (expect error message)
   - [ ] Test with empty input (button should be disabled)

5. **UI/UX**
   - [ ] Verify loading states appear during API calls
   - [ ] Verify error messages are clear and helpful
   - [ ] Test on mobile/responsive design
   - [ ] Verify dark mode (if system preference is dark)

## Known Issues & Limitations

### Video Transcript Availability
- Not all videos have transcripts (live streams, private videos, etc.)
- Some creators disable transcripts on their videos
- Expected: Clear error message "Transcripts are disabled for this video"

### OpenAI API
- Requires valid API key with available credits
- GPT-4o-mini costs approximately $0.15 per 1M input tokens
- If API key is invalid, cleaning will be skipped with warning

### Rate Limiting
- YouTube may rate limit requests for bulk operations
- Recommendation: Limit to 10-20 videos at a time
- Expected: "Request blocked by YouTube" error if rate limited

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing Sample URLs

### Single Videos
- Rick Astley: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Me at the zoo: `https://www.youtube.com/watch?v=jNQXAC9IVRw`

### Playlists
- Deep Learning: `https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`

## Automated Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Backend Issues
1. **Import Error**: Ensure `youtube-transcript-api>=1.2.3` is installed
2. **CORS Error**: Check `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
3. **OpenAI Error**: Verify API key format starts with `sk-`

### Frontend Issues
1. **Connection Refused**: Ensure backend is running on port 8000
2. **Module Not Found**: Run `npm install` to install dependencies
3. **Build Errors**: Delete `.next` folder and restart dev server

## Performance Benchmarks

### Expected Response Times
- Single transcript: 1-3 seconds
- Playlist metadata: 2-5 seconds
- Bulk transcripts (10 videos): 10-20 seconds
- Transcript cleaning: 2-5 seconds per transcript

## Security Testing

- [ ] Verify API key is not exposed in frontend
- [ ] Check `.env` is in `.gitignore`
- [ ] Test CORS protection (should block requests from other origins)
- [ ] Verify input validation for URLs
