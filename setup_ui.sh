#!/bin/bash

echo "🎨 Starting EMI VoiceBot Enhanced UI Setup..."

# Check if templates directory exists
if [ ! -d "templates" ]; then
    mkdir templates
    echo "📁 Created templates directory"
fi

# Make advanced_ui_server.py executable if it exists
if [ -f "advanced_ui_server.py" ]; then
    chmod +x advanced_ui_server.py
    echo "✅ Made advanced_ui_server.py executable"
fi

echo ""
echo "🚀 UI Enhancement Options:"
echo ""
echo "1. Advanced HTML Dashboard (Recommended for immediate use):"
echo "   python advanced_ui_server.py"
echo "   Then open: http://localhost:8001"
echo ""
echo "2. React Dashboard (For advanced customization):"
echo "   cd react-dashboard"
echo "   npm install"
echo "   npm start"
echo ""
echo "3. Simple Dashboard (Fallback option):"
echo "   python advanced_ui_server.py"
echo "   Then open: http://localhost:8001/simple"
echo ""
echo "📊 Features available:"
echo "   ✅ Real-time charts and analytics"
echo "   ✅ Interactive live demo system"
echo "   ✅ Professional animations and styling"
echo "   ✅ Responsive design for all devices"
echo "   ✅ Live call monitoring"
echo "   ✅ Payment tracking"
echo ""
echo "🎯 For presentations, use Option 1 (Advanced HTML Dashboard)"
echo "   It's production-ready and looks professional!"
echo ""

# Try to install Python dependencies if requirements exist
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
    echo "📦 Installing Python dependencies with pip..."
    pip install fastapi uvicorn
else
    echo "⚠️  Consider creating requirements.txt with: fastapi uvicorn"
fi

echo ""
echo "🎉 UI Enhancement setup complete!"
echo "💡 Tip: Start with 'python advanced_ui_server.py' for immediate results"
