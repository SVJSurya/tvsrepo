# 🎯 EMI VoiceBot Complete Demo Guide

## 🚀 Quick Start (One Command)

```bash
cd /Users/rsaxena/Downloads/Manya-TVS-Project
./start_full_demo.sh
```

This single command will start everything you need!

## 📋 Step-by-Step Demo Instructions

### 1. Start the Complete System

```bash
# Navigate to project directory
cd /Users/rsaxena/Downloads/Manya-TVS-Project

# Start everything at once
./start_full_demo.sh
```

### 2. Access the Demo Interfaces

Once servers are running, you'll have access to:

| Interface             | URL                             | Purpose                           |
| --------------------- | ------------------------------- | --------------------------------- |
| **Main Dashboard**    | http://localhost:8001           | Professional analytics & overview |
| **Simple Dashboard**  | http://localhost:8001/simple    | Clean, minimal interface          |
| **Live Call Demo**    | http://localhost:8001/live-demo | Integrated live call simulation   |
| **Direct Live Demo**  | http://localhost:8002           | Standalone live demo system       |
| **API Documentation** | http://localhost:8001/docs      | Interactive API explorer          |

### 3. Demo Flow for Presentations

#### Phase 1: System Overview (Main Dashboard)

1. Open http://localhost:8001
2. Show real-time system stats
3. Demonstrate agent performance metrics
4. Highlight success rates and call volumes

#### Phase 2: Live Call Simulation

1. Click "Live Call Demo" button
2. Set up demo phone number (optional)
3. Select a customer (CUST_001 or CUST_002)
4. Start live call simulation
5. Watch real-time agent interactions
6. Show WebSocket live updates

#### Phase 3: Audio Features (Enhanced Demo)

1. Enable audio in live demo
2. Hear AI-generated voice responses
3. Demonstrate speech recognition (if enabled)
4. Show multi-language support

### 4. Demo Scenarios Available

#### Scenario A: Standard EMI Reminder

- Customer: Manya Johri (CUST_001)
- Amount: ₹15,000 EMI due
- Risk Level: Medium
- Language: English

#### Scenario B: High-Risk Customer

- Customer: Demo Customer (CUST_002)
- Amount: ₹8,500 EMI due
- Risk Level: High
- Language: Hindi

### 5. Real-Time Features to Highlight

✅ **Live WebSocket Updates**: Show instant communication  
✅ **AI Agent Responses**: Demonstrate intelligent conversation  
✅ **Multi-language Support**: Switch between English/Hindi  
✅ **Audio Integration**: Text-to-speech and voice generation  
✅ **Analytics Dashboard**: Real-time metrics and charts  
✅ **Customer Data Integration**: Live customer information

### 6. Technical Features for Stakeholders

- **6 Intelligent Agents**: Trigger, Context, VoiceBot, Decision, Payment, Learning
- **Real-time Processing**: WebSocket-based live updates
- **Audio Capabilities**: TTS, speech recognition, voice calls
- **Scalable Architecture**: FastAPI, SQLAlchemy, async processing
- **Production Ready**: Database integration, error handling, logging

## 🔧 Advanced Setup (Optional)

### For Real Phone Calls (Twilio Integration)

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="your_twilio_number"
```

### For Enhanced Audio

All audio dependencies are already installed:

- ✅ gTTS (Text-to-speech)
- ✅ pygame (Audio playback)
- ✅ SpeechRecognition (Voice input)

## 🛑 Stopping the Demo

```bash
# Stop all servers
pkill -f "python.*server.py"

# Or press Ctrl+C in the terminal running start_full_demo.sh
```

## 🎭 Presentation Tips

1. **Start with Main Dashboard**: Show professional system overview
2. **Move to Live Demo**: Demonstrate real-time capabilities
3. **Highlight Audio Features**: Play actual voice responses
4. **Show WebSocket Updates**: Real-time communication in action
5. **Demonstrate Different Scenarios**: Multiple customer types
6. **End with Analytics**: Show business intelligence capabilities

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Kill existing processes
lsof -ti:8001 | xargs kill -9
lsof -ti:8002 | xargs kill -9
```

### Missing Dependencies

```bash
# Install all requirements
pip install -r requirements.txt
pip install -r requirements-audio-demo.txt
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Your EMI VoiceBot system is now ready for professional presentations! 🎉
