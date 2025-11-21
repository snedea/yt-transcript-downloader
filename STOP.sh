#!/bin/bash

# YouTube Transcript Downloader - Stop Script

echo "🛑 Stopping YouTube Transcript Downloader..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Read PIDs from files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "   ✅ Backend stopped"
    else
        echo "   ⚠️  Backend process not found (may have already stopped)"
    fi
    rm .backend.pid
else
    echo "   ⚠️  No backend PID file found"
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "   ✅ Frontend stopped"
    else
        echo "   ⚠️  Frontend process not found (may have already stopped)"
    fi
    rm .frontend.pid
else
    echo "   ⚠️  No frontend PID file found"
fi

# Also kill any remaining processes on these ports
echo ""
echo "Checking for remaining processes on ports..."

if lsof -i:8000 >/dev/null 2>&1; then
    echo "   Found process on port 8000, killing..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

if lsof -i:3000 >/dev/null 2>&1; then
    echo "   Found process on port 3000, killing..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
fi

echo ""
echo "✅ All servers stopped"
