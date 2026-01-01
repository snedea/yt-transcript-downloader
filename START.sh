#!/bin/bash

# YouTube Transcript Downloader - Docker CLI
# This script manages the application using Docker

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  YouTube Transcript Downloader (Docker)                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "🚀 Starting application..."
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Application started successfully!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo ""
    echo "📝 Tailing logs (Ctrl+C to exit logs, app will keep running)..."
    echo ""
    docker-compose logs -f
else
    echo "❌ Failed to start application."
    exit 1
fi
