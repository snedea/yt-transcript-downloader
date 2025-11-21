#!/bin/bash

# YouTube Transcript Downloader - Startup Script
# This script starts both backend and frontend servers

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  YouTube Transcript Downloader - Starting Application...      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to check if port is in use
check_port() {
    lsof -i:$1 >/dev/null 2>&1
    return $?
}

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use (backend may already be running)"
    echo "   Use 'lsof -i:8000' to check what's using it"
    echo ""
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use (frontend may already be running)"
    echo "   Use 'lsof -i:3000' to check what's using it"
    echo ""
fi

# Start backend in background
echo "🔧 Starting backend server on port 8000..."
cd backend
source venv/bin/activate 2>/dev/null || {
    echo "❌ Virtual environment not found. Run setup first:"
    echo "   cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
}

uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
cd ..

# Wait for backend to start
echo "   Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if check_port 8000; then
    echo "   ✅ Backend started successfully"
else
    echo "   ❌ Backend failed to start. Check backend.log for errors."
    cat backend.log
    exit 1
fi

# Start frontend in background
echo ""
echo "🎨 Starting frontend server on port 3000..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed. Run setup first:"
    echo "   cd frontend && npm install"
    exit 1
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

# Wait for frontend to start
echo "   Waiting for frontend to initialize..."
sleep 5

# Check if frontend is running
if check_port 3000; then
    echo "   ✅ Frontend started successfully"
else
    echo "   ❌ Frontend failed to start. Check frontend.log for errors."
    cat frontend.log
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Application started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Process IDs:"
echo "   Backend:   $BACKEND_PID"
echo "   Frontend:  $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:   tail -f backend.log"
echo "   Frontend:  tail -f frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or run: ./STOP.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Save PIDs to file for easy stopping
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo ""
echo "Press Ctrl+C to see logs in real-time (servers will keep running)"
echo ""

# Follow logs
tail -f backend.log frontend.log
