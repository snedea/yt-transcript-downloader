# Installation Guide

This guide provides detailed instructions for setting up the YouTube Transcript Downloader on your local machine.

## Prerequisites

Before installing, ensure you have the following:

### Required Software

| Software | Minimum Version | Download Link |
|----------|-----------------|---------------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| npm | 9+ | Included with Node.js |
| Git | 2.0+ | [git-scm.com](https://git-scm.com/) |

### Optional

- **OpenAI API Key** - Required only for AI-powered transcript cleaning

## Quick Installation

For the fastest setup, use the provided start script:

```bash
chmod +x START.sh
./START.sh
```

This script will:
1. Set up the Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Start both servers

## Manual Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/yt-transcript-downloader.git
cd yt-transcript-downloader
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory

```bash
cd backend
```

#### 2.2 Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 2.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.4 Verify Installation

```bash
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('YouTube Transcript API: OK')"
```

### Step 3: Frontend Setup

Open a new terminal window.

#### 3.1 Navigate to Frontend Directory

```bash
cd frontend
```

#### 3.2 Install Dependencies

```bash
npm install
```

#### 3.3 Verify Installation

```bash
npm run build
```

### Step 4: Environment Configuration

#### 4.1 Create Environment File

```bash
# From project root
cp .env.example .env
```

#### 4.2 Configure Variables

Edit `.env` with your settings:

```env
# Required for AI cleaning (optional otherwise)
OPENAI_API_KEY=sk-your-api-key-here

# Environment (development/production)
ENVIRONMENT=development

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate limiting
API_RATE_LIMIT=100/minute
```

### Step 5: Start the Application

#### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # Linux/macOS
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 6: Verify Setup

1. **Backend Health Check:** http://localhost:8000/health
2. **API Documentation:** http://localhost:8000/docs
3. **Frontend Application:** http://localhost:3000

## Platform-Specific Notes

### macOS

If you encounter SSL certificate errors:
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Windows

- Use PowerShell or Git Bash for best compatibility
- If `venv\Scripts\activate` fails, try: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux

Install Python development headers if needed:
```bash
# Ubuntu/Debian
sudo apt-get install python3.11-dev python3.11-venv

# Fedora
sudo dnf install python3.11-devel
```

## Troubleshooting

### "Python command not found"

Ensure Python is in your PATH:
```bash
# Check installation
which python3
python3 --version
```

### "npm command not found"

Install Node.js from [nodejs.org](https://nodejs.org/) or use a version manager like `nvm`:
```bash
# Using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### "Port already in use"

Find and kill the process using the port:
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### "Module not found" errors

Ensure virtual environment is activated and dependencies are installed:
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

### CORS Errors

Ensure your frontend URL is in the `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

## Next Steps

- [Usage Guide](USAGE.md) - Learn how to use the application
- [API Documentation](API.md) - Explore the REST API
- [Architecture](ARCHITECTURE.md) - Understand the system design
