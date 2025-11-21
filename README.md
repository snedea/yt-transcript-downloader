# YouTube Transcript Downloader

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

> 🎬 A modern full-stack web application for downloading and AI-cleaning YouTube video transcripts. Supports single videos, playlists, and channels.

![Application Screenshot](docs/screenshots/hero.png)

## ✨ Features

- 📹 **Single Video Downloads** - Fetch transcripts from any YouTube video with available captions
- 📋 **Bulk Downloads** - Download transcripts from entire playlists or channels at once
- 🤖 **AI-Powered Cleaning** - Optional GPT-4o-mini integration to clean and format transcripts
- 📎 **Export Options** - Copy to clipboard or download as `.txt` files
- 🌙 **Modern UI** - Clean, responsive design with dark mode support
- 📊 **Progress Tracking** - Real-time progress indicators for bulk operations
- ⚡ **Fast & Efficient** - Parallelized bulk downloads for optimal performance

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

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **OpenAI API Key** *(optional)* - For AI transcript cleaning

### One-Command Start

```bash
# Make start script executable and run
chmod +x START.sh && ./START.sh
```

Or follow the manual setup below.

### Manual Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/yt-transcript-downloader.git
cd yt-transcript-downloader
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### 4. Configure Environment (Optional)

For AI transcript cleaning, create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

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
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── routers/
│   │   │   ├── transcript.py    # Transcript endpoints
│   │   │   └── playlist.py      # Playlist endpoints
│   │   ├── services/
│   │   │   ├── youtube.py       # YouTube transcript service
│   │   │   ├── openai_service.py # AI cleaning service
│   │   │   └── playlist.py      # Playlist extraction
│   │   └── utils/
│   │       ├── url_parser.py    # URL parsing utilities
│   │       └── validators.py    # Input validation
│   ├── tests/                   # Backend tests
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client
│   │   └── types/               # TypeScript definitions
│   └── package.json             # Node.js dependencies
├── docs/
│   └── screenshots/             # Application screenshots
├── .env.example                 # Environment template
├── START.sh                     # One-command startup
├── STOP.sh                      # Stop all services
└── README.md                    # This file
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
