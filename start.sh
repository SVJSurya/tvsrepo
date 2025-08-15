#!/bin/bash

# EMI VoiceBot System Startup Script
echo "🚀 Starting EMI VoiceBot System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if packages are installed
python -c "import fastapi" 2>/dev/null || {
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
}

# Create necessary directories
mkdir -p data/logs
mkdir -p data/models
mkdir -p data/reports

# Set environment variables for demo
export DATABASE_URL="sqlite:///./emi_voicebot.db"
export REDIS_URL="redis://localhost:6379"
export DEBUG="True"

echo "✅ Environment setup complete!"
echo ""
echo "Choose startup option:"
echo "1. Run Complete Demo (Recommended for first time)"
echo "2. Start API Server with Dashboard"
echo "3. Run Interactive Live Demo"
echo "4. Quick Production Setup"
echo "5. Simple Testing Demo"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🎯 Running Complete Demo..."
        python demo.py
        ;;
    2)
        echo "🌐 Starting API Server with Interactive Dashboard..."
        echo "📊 Dashboard will be available at: http://localhost:8000"
        echo "📚 API Documentation: http://localhost:8000/docs"
        python api_server.py
        ;;
    3)
        echo "🎭 Starting Interactive Live Demo..."
        python live_demo.py
        ;;
    4)
        echo "🚀 Running Production Setup..."
        python production_setup.py
        ;;
    5)
        echo "🧪 Running Simple Testing Demo..."
        python simple_demo.py
        ;;
    5)
        echo "🧪 Running Simple Testing Demo..."
        python simple_demo.py
        ;;
    *)
        echo "❌ Invalid choice! Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Thank you for using EMI VoiceBot System!"
    *)
        echo "Invalid choice. Starting API server..."
        python src/main.py
        ;;
esac
