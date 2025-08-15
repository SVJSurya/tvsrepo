#!/bin/bash

# EMI VoiceBot Complete Demo Startup Script
# This script starts both the main UI server and the live call demo system

echo "🚀 Starting EMI VoiceBot Complete Demo System..."
echo "=================================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "
import fastapi, uvicorn, pygame, gtts, twilio
print('✅ All required packages are available')
" || {
    echo "❌ Missing dependencies. Installing..."
    pip install fastapi uvicorn pygame gtts twilio SpeechRecognition websockets
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:8003 | xargs kill -9 2>/dev/null || true

echo "🎯 Starting servers..."

# Start the main UI server
echo "🌐 Starting Main UI Server (port 8001)..."
python advanced_ui_server.py &
MAIN_UI_PID=$!

# Wait a moment for the main server to start
sleep 3

# Start the live call demo server
echo "📞 Starting Live Call Demo Server (port 8002)..."
python live_call_demo.py &
LIVE_DEMO_PID=$!

# Wait for servers to start
sleep 5

echo ""
echo "🎉 EMI VoiceBot Demo System is Ready!"
echo "=================================================="
echo "📊 Main Dashboard:     http://localhost:8001"
echo "📋 Simple Dashboard:   http://localhost:8001/simple"
echo "🎭 Live Call Demo:     http://localhost:8001/live-demo"
echo "📞 Direct Live Demo:   http://localhost:8002"
echo "🔗 API Documentation:  http://localhost:8001/docs"
echo ""
echo "🎯 Demo Flow:"
echo "1. Open Main Dashboard to see system overview"
echo "2. Click 'Live Call Demo' for real-time call simulation"
echo "3. Use the demo interface to simulate customer calls"
echo "4. Watch real-time analytics and agent responses"
echo ""
echo "⚠️  To stop all servers: Press Ctrl+C or run 'pkill -f \"python.*server.py\"'"
echo ""
echo "📝 Process IDs:"
echo "   Main UI Server: $MAIN_UI_PID"
echo "   Live Demo Server: $LIVE_DEMO_PID"

# Keep the script running and monitor processes
wait
