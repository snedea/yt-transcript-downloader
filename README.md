# Faceteer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

> 💎 **Every angle, every insight—without surrendering hours.**
>
> Stop consuming content. Start commanding it. Faceteer examines any content from multiple perspectives—paste URLs, upload PDFs, or paste text, then facet it for rhetoric, manipulation, claims, and insights in minutes, not hours.

## ✨ Features

### Universal Content Ingestion
- 🎬 **YouTube Videos** - Automatic transcript extraction with metadata
- 📄 **PDF Documents** - Full-text extraction with AI-generated thumbnails
- 🌐 **Web URLs** - Smart article extraction from any website
- 📋 **Plain Text** - Paste content from emails, documents, anywhere
- 🤖 **Smart Detection** - Automatically identifies content type and extracts appropriately
- 📦 **Bulk Operations** - Process entire YouTube playlists or channels at once

### Multi-Perspective Analysis
- 🔍 **Rhetorical Analysis** - 5-dimension trust evaluation:
  - **Epistemic Integrity** - Scholarly vs sloppy reasoning
  - **Argument Quality** - Logic, evidence, and coherence
  - **Manipulation Risk** - Coercive persuasion markers
  - **Rhetorical Craft** - Style and persuasion techniques
  - **Fairness/Balance** - One-sidedness detection
- 🎯 **Manipulation Detection** - Identify 34+ manipulation techniques across language, reasoning, and propaganda
- 📊 **Claim Extraction** - Auto-detect and categorize factual, causal, normative, and predictive claims
- ✅ **Claim Verification** - Optional web search verification (Deep mode)
- 💡 **Discovery Mode** - Extract key topics, themes, and insights from content
- 🏥 **Health Observations** - AI vision analysis of video frames for health/wellness content
- ✨ **Prompt Generation** - Generate AI prompts from content for various use cases
- 🏷️ **Auto-Tagging** - Automatic keyword and tag extraction from summaries

### Smart Library & Search
- 📚 **Unified Library** - All your content (videos, PDFs, articles, text) in one place
- 🔎 **Powerful Search** - Full-text search across all content with smart filters
- 🏷️ **Tag Filtering** - Filter by auto-extracted tags and keywords
- 📑 **Content Type Filters** - Filter by technical, educational, news, entertainment, etc.
- 🔖 **Status Badges** - See at-a-glance what's been summarized or analyzed
- 🎨 **Visual Cards** - AI-generated thumbnails for PDFs, YouTube thumbnails for videos
- ⚡ **Recent History** - Quick access to recently viewed content

### User Experience
- 🔐 **User Accounts** - Secure authentication with JWT (OAuth2 support)
- 🌙 **Dark Mode** - Full dark mode support throughout
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- ⚡ **Smart Caching** - Instant retrieval of previously analyzed content
- 📎 **Export Options** - Copy to clipboard or download as files
- 🎯 **Progressive Analysis** - Run only the analysis you need, when you need it

## 📸 Screenshots

### Single Video Download
![Single Download Interface](docs/screenshots/feature-01-single-download.png)
*Download transcripts from individual YouTube videos with optional AI cleaning*

### Bulk Playlist Download
![Bulk Download Interface](docs/screenshots/feature-02-bulk-download.png)
*Select and download multiple transcripts from playlists or channels*

### Mobile Responsive
![Mobile View](docs/screenshots/feature-03-mobile.png)
*Fully responsive design for mobile devices*

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | Modern async Python web framework |
| [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | YouTube transcript extraction |
| [OpenAI GPT-4o-mini](https://platform.openai.com/) | AI-powered transcript cleaning |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Playlist/channel video extraction |

### Frontend
| Technology | Purpose |
|------------|---------|
| [Next.js 14](https://nextjs.org/) | React framework with App Router |
| [React 18](https://react.dev/) | UI component library |
| [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first CSS framework |

## 🚀 Quick Start

### Docker (Recommended)

The easiest way to run the application:

```bash
# 1. Clone the repository
git clone https://github.com/snedea/yt-transcript-downloader.git
cd yt-transcript-downloader

# 2. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start with Docker
./START.sh
```

#### START.sh Commands

| Command | Description |
|---------|-------------|
| `./START.sh` | Start the application (default) |
| `./START.sh stop` | Stop the application |
| `./START.sh restart` | Restart the application |
| `./START.sh logs` | Follow container logs |
| `./START.sh status` | Show container status |
| `./START.sh build` | Rebuild Docker images |
| `./START.sh clean` | Remove containers and volumes |

### Manual Installation (Development)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **OpenAI API Key** - Required for AI cleaning and analysis

#### 1. Clone the Repository

```bash
git clone https://github.com/snedea/yt-transcript-downloader.git
cd yt-transcript-downloader
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

</details>

### Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |

## 📖 Usage

### Downloading a Single Transcript

1. Navigate to the **Single Video** tab
2. Paste a YouTube video URL
3. *(Optional)* Check "Clean with AI" for formatted output
4. Click **Get Transcript**
5. Copy to clipboard or download as `.txt`

### Analyzing Content for Manipulation

1. Fetch a transcript (or select from History)
2. Click **Analyze for Manipulation**
3. Choose analysis mode:
   - **Quick Mode** (~15s) - Single-pass analysis, good for most use cases
   - **Deep Mode** (~60s) - Multi-pass with claim verification
4. Review the analysis report:
   - **Overview** - Overall trust score and grade
   - **Dimensions** - 5-dimension breakdown with explanations
   - **Claims** - Detected claims with verification status
   - **Devices** - Manipulation techniques found

### Bulk Downloading from Playlists

1. Navigate to the **Bulk Download** tab
2. Paste a YouTube playlist or channel URL
3. Select videos using checkboxes (or "Select All")
4. *(Optional)* Enable AI cleaning
5. Click **Download Selected**
6. Download individual transcripts or all as a batch

## 📡 API Documentation

The backend provides a RESTful API with automatic OpenAPI documentation.

### Endpoints

#### Health Check
```http
GET /health
```
Returns API health status.

#### Get Single Transcript
```http
POST /api/transcript/single
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "clean": false
}
```

**Response:**
```json
{
  "transcript": "Full transcript text...",
  "video_title": "Video Title",
  "video_id": "dQw4w9WgXcQ",
  "tokens_used": 0
}
```

#### Get Playlist Videos
```http
POST /api/playlist/videos
Content-Type: application/json

{
  "playlist_url": "https://www.youtube.com/playlist?list=PLxxxxx"
}
```

**Response:**
```json
{
  "videos": [
    {
      "id": "video_id",
      "title": "Video Title",
      "thumbnail": "https://...",
      "duration": "10:30"
    }
  ]
}
```

#### Bulk Download Transcripts
```http
POST /api/transcript/bulk
Content-Type: application/json

{
  "video_ids": ["id1", "id2", "id3"],
  "clean": false
}
```

**Response:**
```json
{
  "results": [
    {
      "video_id": "id1",
      "transcript": "...",
      "status": "success"
    }
  ],
  "total": 3,
  "successful": 3,
  "failed": 0
}
```

#### Clean Transcript with AI
```http
POST /api/transcript/clean
Content-Type: application/json

{
  "transcript": "Raw transcript text..."
}
```

**Response:**
```json
{
  "cleaned_transcript": "Formatted, cleaned transcript...",
  "tokens_used": 150
}
```

### Interactive API Docs

Visit **http://localhost:8000/docs** for Swagger UI with interactive testing.

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app

# Skip integration tests (no OpenAI required)
pytest tests/ -v -m "not integration"
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch
```

## 📁 Project Structure

```
yt-transcript-downloader/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration
│   │   ├── routers/
│   │   │   ├── transcript.py          # Transcript endpoints
│   │   │   ├── playlist.py            # Playlist endpoints
│   │   │   ├── cache.py               # Cache/history endpoints
│   │   │   └── analysis.py            # Analysis endpoints
│   │   ├── services/
│   │   │   ├── youtube.py             # YouTube transcript service
│   │   │   ├── openai_service.py      # AI cleaning service
│   │   │   ├── cache_service.py       # SQLite caching
│   │   │   ├── manipulation_pipeline.py # 5-dimension analysis
│   │   │   └── web_search.py          # Claim verification
│   │   ├── models/                    # Pydantic models
│   │   └── data/
│   │       └── manipulation_toolkit.py # Technique definitions
│   ├── tests/                         # Backend tests
│   ├── Dockerfile                     # Backend container
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   ├── components/
│   │   │   ├── analysis/              # Analysis UI components
│   │   │   ├── SingleDownload.tsx     # Single video UI
│   │   │   ├── BulkDownload.tsx       # Bulk download UI
│   │   │   └── TranscriptHistory.tsx  # History panel
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── services/api.ts            # API client
│   │   └── types/index.ts             # TypeScript definitions
│   ├── Dockerfile                     # Frontend container
│   └── package.json                   # Node.js dependencies
├── docker-compose.yml                 # Container orchestration
├── .env.example                       # Environment template
├── START.sh                           # Docker CLI wrapper
└── README.md                          # This file
```

## ⚙️ Configuration

### Environment Variables

#### Backend (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI cleaning | *(none)* |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `CORS_ORIGINS` | Allowed CORS origins | `localhost:3000` |
| `API_RATE_LIMIT` | Rate limiting | `100/minute` |

#### Frontend (`.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Getting an OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-`)
5. Add to `.env` as `OPENAI_API_KEY=sk-...`

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><strong>Docker won't start</strong></summary>

- Ensure Docker Desktop is running
- Check port availability: `lsof -i :3000` and `lsof -i :8000`
- Stop existing containers: `./START.sh clean`
- Rebuild images: `./START.sh build`
</details>

<details>
<summary><strong>Backend won't start</strong></summary>

- Check Python version: `python --version` (requires 3.11+)
- Verify virtual environment is activated
- Check if port 8000 is available: `lsof -i :8000`
- Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`
</details>

<details>
<summary><strong>Frontend won't start</strong></summary>

- Check Node.js version: `node --version` (requires 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is available: `lsof -i :3000`
</details>

<details>
<summary><strong>Analysis not working</strong></summary>

- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key has credits at [OpenAI Usage](https://platform.openai.com/usage)
- View logs: `./START.sh logs`
</details>

<details>
<summary><strong>CORS errors</strong></summary>

- Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL
- Default development origins (localhost:3000, 3001) are automatically allowed
</details>

<details>
<summary><strong>Transcript not found</strong></summary>

- Some videos don't have transcripts (live streams, private videos)
- Transcripts must be enabled by the video creator
- Try a different video to verify the setup works
</details>

<details>
<summary><strong>OpenAI API errors</strong></summary>

- Verify API key format (should start with `sk-`)
- Check API key has credits at [OpenAI Usage](https://platform.openai.com/usage)
- Transcript cleaning will be skipped if API key is invalid
</details>

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Run tests before submitting PRs
- Follow existing code style and patterns
- Update documentation for new features
- Add tests for new functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - YouTube transcript extraction
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video metadata extraction
- [OpenAI](https://openai.com/) - GPT-4o-mini for transcript cleaning

---

<p align="center">
  🤖 Built autonomously by <a href="https://github.com/context-foundry">Context Foundry</a>
</p>
