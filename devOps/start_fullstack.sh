#!/bin/bash

# Star Wars Full Stack Startup Script
# This script starts both the Flask backend and React frontend

echo "🌟 Starting Star Wars Full Stack Application..."
echo ""

# Function to start backend
start_backend() {
    echo "🚀 Starting Flask Backend..."
    cd "$(dirname "$0")/backend"
    if [ ! -f "app.py" ]; then
        echo "❌ Error: app.py not found in backend directory"
        exit 1
    fi
    ../.venv/bin/python app.py &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID) at http://127.0.0.1:3000"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React Frontend..."
    cd "$(dirname "$0")/frontend"
    if [ ! -f "package.json" ]; then
        echo "❌ Error: package.json not found in frontend directory"
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing npm dependencies..."
        npm install
    fi
    
    npm start &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID) at http://localhost:3001"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   Stopped backend (PID: $BACKEND_PID)"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   Stopped frontend (PID: $FRONTEND_PID)"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both servers
start_backend
sleep 3  # Give backend time to start
start_frontend

echo ""
echo "🌐 Application URLs:"
echo "   - Backend API: http://127.0.0.1:3000"
echo "   - Admin Panel: http://127.0.0.1:3000/admin/"
echo "   - Frontend:    http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "May the Force be with you! 🌟"

# Wait for user to stop
wait
