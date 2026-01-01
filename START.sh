#!/bin/bash

# YouTube Content Analyzer - Docker CLI
# This script manages the application using Docker

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

show_header() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  YouTube Content Analyzer (Docker)                            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

show_help() {
    show_header
    echo "Usage: ./START.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start the application (default)"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  logs      Show logs (follow mode)"
    echo "  status    Show container status"
    echo "  build     Rebuild images"
    echo "  clean     Stop and remove containers/volumes"
    echo "  help      Show this help message"
    echo ""
}

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running!"
        echo "   Please start Docker Desktop and try again."
        exit 1
    fi
}

start_app() {
    show_header
    check_docker
    echo "🚀 Starting application..."
    docker-compose up -d

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
}

stop_app() {
    show_header
    check_docker
    echo "🛑 Stopping application..."
    docker-compose down
    echo "✅ Application stopped."
}

restart_app() {
    show_header
    check_docker
    echo "🔄 Restarting application..."
    docker-compose restart
    echo "✅ Application restarted."
    echo ""
    docker-compose logs -f
}

show_logs() {
    check_docker
    docker-compose logs -f
}

show_status() {
    show_header
    check_docker
    docker-compose ps
}

build_app() {
    show_header
    check_docker
    echo "🔨 Building images..."
    docker-compose build
    echo "✅ Build complete."
}

clean_app() {
    show_header
    check_docker
    echo "🧹 Cleaning up..."
    docker-compose down -v
    echo "✅ Containers and volumes removed."
}

# Parse command
case "${1:-start}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_app
        ;;
    clean)
        clean_app
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
