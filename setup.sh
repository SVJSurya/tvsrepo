#!/bin/bash

# EMI VoiceBot - Setup Script for Other Machines
# This script sets up the complete environment for the EMI VoiceBot system

echo "🚀 EMI VoiceBot - Environment Setup"
echo "====================================="

# Check if Python 3.8+ is installed
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing Python packages from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements."
    exit 1
fi

# Create .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env template file..."
    cat > .env << EOL
# EMI VoiceBot Configuration
# Copy this file and update with your actual credentials

# Google AI API Key (Free tier: 15 requests/min, 1M tokens/month)
GOOGLE_API_KEY=your_google_ai_api_key_here

# Gmail SMTP Configuration (for payment link emails)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# Twilio Configuration (Optional - for SMS/Voice calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Database Configuration (Optional - for production)
DATABASE_URL=postgresql://user:password@localhost:5432/emi_voicebot

# Redis Configuration (Optional - for caching)
REDIS_URL=redis://localhost:6379/0

# OpenAI API Key (Optional - fallback AI)
OPENAI_API_KEY=your_openai_api_key_here

# Razorpay Configuration (Optional - payment processing)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
DEBUG_MODE=True
EOL
    echo "✅ .env template created. Please update it with your credentials."
else
    echo "ℹ️ .env file already exists."
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Create temp directory for audio files
echo "📁 Creating temp directory..."
mkdir -p temp

# Check if all agent files exist
echo "🔍 Checking agent files..."
required_files=(
    "src/agents/trigger_agent.py"
    "src/agents/context_agent.py"
    "src/agents/google_voicebot_agent.py"
    "src/agents/decision_agent.py"
    "src/agents/payment_agent.py"
    "src/agents/logging_learning_agent.py"
    "templates/live_call_demo.html"
    "templates/voice_demo.html"
    "templates/advanced_dashboard.html"
    "advanced_ui_server.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ All required files found."
else
    echo "⚠️ Missing files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
fi

# Test Google AI connection
echo "🧪 Testing Google AI connection..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY', '')
if api_key and api_key != 'your_google_ai_api_key_here':
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content('Hello, test connection')
        print('✅ Google AI connection successful')
    except Exception as e:
        print(f'❌ Google AI connection failed: {e}')
else:
    print('⚠️ Google AI API key not configured')
"

echo ""
echo "🎉 Setup Complete!"
echo "==================="
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your actual credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Start server: python advanced_ui_server.py"
echo "4. Open browser: http://localhost:8001"
echo ""
echo "🌐 Available Interfaces:"
echo "   • Advanced Dashboard: http://localhost:8001"
echo "   • Live Call Demo: http://localhost:8001/live-demo"
echo "   • Voice Demo: http://localhost:8001/voice-demo"
echo "   • API Documentation: http://localhost:8001/docs"
echo ""
echo "📚 Documentation:"
echo "   • Architecture: ARCHITECTURE_WORKFLOW.md"
echo "   • Implementation: IMPLEMENTATION_SUMMARY.md"
echo "   • Demo Guide: DEMO_PRESENTATION_GUIDE.md"
echo "   • Quick Reference: DEMO_QUICK_REFERENCE.md"
echo ""
echo "🔑 Required Credentials:"
echo "   • Google AI API Key (Free): https://makersuite.google.com/app/apikey"
echo "   • Gmail App Password: https://support.google.com/accounts/answer/185833"
echo ""
echo "✨ Happy coding!"
