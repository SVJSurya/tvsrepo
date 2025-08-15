# 🤖 EMI VoiceBot - AI-Powered Collection System

An intelligent voice-based EMI collection system that uses AI to handle customer interactions, process payments, and manage collections automatically.

## 🚀 Features

- **AI-Powered Voice Conversations**: Natural language processing using Google AI (Gemini)
- **Real-time Voice Interface**: Browser-based voice interaction with speech recognition
- **Contextual Conversations**: Maintains conversation history and context across interactions
- **Automated Email Integration**: Sends payment links via Gmail SMTP
- **Interactive Demos**: Multiple demo interfaces for different use cases
- **Analytics Dashboard**: Real-time statistics and performance tracking
- **Multi-Agent Architecture**: Specialized AI agents for different tasks

## 🎯 Demo Interfaces

1. **Live Call Demo** (`/live-demo`) - Interactive voice conversation with user input
2. **Voice Demo** (`/voice-demo`) - Seamless voice interaction experience
3. **Real-time Demo** (`/realtime-demo`) - Enhanced real-time call interface
4. **Advanced Dashboard** (`/`) - Complete analytics and control panel

## �️ Technologies Used

- **Backend**: FastAPI (Python)
- **AI/ML**: Google AI (Gemini 1.5 Flash)
- **Voice**: Web Speech API, Speech Synthesis
- **Email**: Gmail SMTP with SSL/TLS
- **Frontend**: HTML5, JavaScript, CSS3
- **Data**: JSON-based session storage

## 📋 Prerequisites

- Python 3.8 or higher
- Gmail account with App Password enabled
- Google AI API key (free tier available)
- Modern web browser with microphone access

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Manya104/tvsrepo.git
cd tvsrepo
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the template
cp .env.template .env

# Edit .env with your actual credentials
nano .env
```

**Required Configuration:**

- `GOOGLE_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Generate from [Google Account Settings](https://support.google.com/accounts/answer/185833)

### 4. Run the Application

```bash
python advanced_ui_server.py
```

### 5. Access the Application

- Open http://localhost:8000 in your browser
- Allow microphone access when prompted
- Try the different demo interfaces

## 📖 Configuration Guide

### Gmail SMTP Setup

1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings → Security → App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password in your `.env` file

### Google AI API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file

## 🎮 Usage Examples

### Basic Voice Interaction

1. Navigate to `/voice-demo`
2. Click "Start Conversation"
3. Speak naturally about EMI payments
4. The AI will respond contextually

### Email Payment Links

1. Use `/live-demo` interface
2. Follow the conversation flow
3. Provide email when requested
4. Receive payment link via email

### Analytics Dashboard

1. Visit the main dashboard at `/`
2. View real-time statistics
3. Monitor call success rates
4. Track payment collections

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│   FastAPI       │────│   Google AI     │
│   (Speech API)  │    │   Server        │    │   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │             │
                ┌─────────────┐ ┌─────────────┐
                │   Gmail     │ │ Session     │
                │   SMTP      │ │ Storage     │
                └─────────────┘ └─────────────┘
```

## 🤖 AI Agents

- **VoiceBot Agent**: Handles natural language conversations
- **Trigger Agent**: Manages EMI due date checks
- **Analytics Agent**: Processes performance data
- **Logging Agent**: Tracks system events

## 📊 API Endpoints

### Voice Processing

- `POST /api/voice/process` - Process voice input with AI
- `POST /api/voice/test-call` - Test voice functionality

### Payment & Email

- `POST /api/payment/send-link` - Send payment link via email
- `GET /api/payment/sent-links` - Get sent payment history

### Analytics

- `GET /api/stats` - Get dashboard statistics
- `GET /api/analytics/dashboard` - Get detailed analytics

### Demo & Testing

- `POST /api/demo/workflow` - Run demonstration workflow
- `POST /api/trigger/check-due-emis` - Check for due EMIs

## � Security Features

- Environment variable protection
- SSL/TLS email encryption
- Session-based conversation storage
- Input validation and sanitization

## 📱 Browser Compatibility

- Chrome 70+ (Recommended)
- Firefox 75+
- Safari 14+
- Edge 79+

_Note: Microphone access required for voice features_

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Microphone not working:**

- Ensure browser permissions are granted
- Check system microphone settings
- Try different browsers

**Email not sending:**

- Verify Gmail App Password is correct
- Check internet connection
- Ensure 2FA is enabled on Gmail

**AI responses not working:**

- Verify Google AI API key is valid
- Check API quota limits
- Ensure network connectivity

### Getting Help

- Check the [Documentation](ARCHITECTURE_WORKFLOW.md)
- Review [Implementation Details](IMPLEMENTATION_SUMMARY.md)
- See [Demo Guide](DEMO_PRESENTATION_GUIDE.md)

## 📈 Performance

- **Response Time**: < 2 seconds for AI processing
- **Email Delivery**: < 30 seconds via Gmail SMTP
- **Voice Recognition**: Real-time with Web Speech API
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🎯 Use Cases

- EMI collection automation
- Customer service voice bots
- Payment reminder systems
- Financial service automation
- Customer interaction analytics

---

**Made with ❤️ for intelligent customer service automation**

- Multi-channel messaging (SMS, WhatsApp)
- Payment verification
- Transaction tracking

### 🔹 6. Logging & Learning Agent

- **Function**: Logs interactions and learns from outcomes
- **Features**:
  - Comprehensive interaction logging
  - ML-based outcome prediction
  - Analytics & insights generation
  - Performance optimization

## 🛠️ Technologies Used

| Layer     | Technologies                           |
| --------- | -------------------------------------- |
| Backend   | Python, FastAPI, SQLAlchemy            |
| AI/ML     | OpenAI GPT, scikit-learn, pandas       |
| Database  | SQLite (demo), PostgreSQL (production) |
| Messaging | Twilio (simulated)                     |
| Payment   | Razorpay (simulated)                   |
| API       | RESTful APIs with OpenAPI docs         |

## 📁 Project Structure

```
Manya-TVS-Project/
├── src/
│   ├── agents/                 # All AI agents
│   │   ├── trigger_agent.py
│   │   ├── context_agent.py
│   │   ├── voicebot_agent.py
│   │   ├── decision_agent.py
│   │   ├── payment_agent.py
│   │   └── logging_learning_agent.py
│   ├── models/                 # Database models
│   ├── services/               # External service integrations
│   ├── utils/                  # Utilities and helpers
│   └── main.py                 # FastAPI application
├── config/                     # Configuration files
├── data/                       # Data storage (logs, models, reports)
├── tests/                      # Unit tests
├── demo.py                     # Complete demo script
├── start.sh                    # Startup script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation & Setup

1. **Clone and Navigate**

   ```bash
   cd Manya-TVS-Project
   ```

2. **Install Dependencies**

   ```bash
   # Virtual environment should already be activated
   pip install -r requirements.txt
   ```

3. **Run the Demo**

   ```bash
   # Option 1: Use the startup script (Recommended)
   ./start.sh

   # Option 2: Run demo directly
   python demo.py

   # Option 3: Start API server
   python src/main.py
   ```

### Demo Options

The system provides multiple ways to explore:

1. **Complete Workflow Demo** - Shows all agents working together
2. **API Server** - Interactive API documentation at `http://localhost:8000/docs`
3. **Interactive Demo** - Python shell with demo objects loaded

## 🎯 Working Demo Flow

### 1. Trigger Agent Demo

```python
# Check for due EMIs
due_emis = trigger_agent.check_due_emis()
# Output: List of customers requiring calls with priority scores
```

### 2. Context Agent Demo

```python
# Get comprehensive customer context
context = context_agent.get_customer_context(customer_id)
# Output: Risk score, payment history, preferences, conversation context
```

### 3. VoiceBot Agent Demo

```python
# Initiate AI-powered conversation
call_result = voicebot_agent.initiate_call(customer_context, emi_info)
# Output: Conversation log, outcome, sentiment analysis
```

### 4. Decision Agent Demo

```python
# Make intelligent decisions based on conversation
decision = decision_agent.make_decision(call_result, customer_context)
# Output: Next action, priority, escalation needs, recommendations
```

### 5. Payment Agent Demo

```python
# Create and send payment links
payment_link = payment_agent.create_payment_link(customer_context, loan_info)
sms_result = payment_agent.send_payment_link_sms(customer_context, payment_link)
# Output: Secure payment link, SMS confirmation
```

### 6. Learning Agent Demo

```python
# Generate insights and analytics
analytics = logging_agent.analyze_interaction_patterns(30)
insights = logging_agent.generate_insights_report(30)
# Output: Performance metrics, recommendations, ML predictions
```

## 🌐 API Endpoints

### Core Endpoints

- `POST /demo/setup-sample-data` - Setup demo customers and loans
- `GET /demo/test-workflow` - Run complete workflow test
- `POST /calls/initiate` - Initiate voice call to customer
- `POST /payments/create-link` - Create payment link
- `GET /analytics/insights` - Get comprehensive analytics

### Management Endpoints

- `GET /health` - System health check
- `GET /admin/system-status` - Overall system status
- `GET /customers/{id}/context` - Get customer context
- `POST /ml/train-predictor` - Train ML models

### Full API Documentation

Visit `http://localhost:8000/docs` when server is running for interactive API documentation.

## 📊 Features Demonstrated

### ✅ Multi-Agent Coordination

- All 6 agents working together seamlessly
- Data flow between agents
- Coordinated decision making

### ✅ AI-Powered Conversations

- Multi-language support (English, Hindi)
- Context-aware responses
- Sentiment analysis
- Intent recognition

### ✅ Intelligent Decision Making

- Risk-based prioritization
- Rule-based escalation
- Channel optimization
- Follow-up scheduling

### ✅ Payment Processing

- Secure payment link generation
- Multi-channel notifications
- Transaction verification
- Payment analytics

### ✅ Learning & Analytics

- Interaction pattern analysis
- ML-based predictions
- Performance optimization
- Business insights generation

### ✅ Production-Ready Features

- Comprehensive logging
- Error handling
- API documentation
- Scalable architecture

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/emi_voicebot

# API Keys (Replace with actual keys for production)
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
RAZORPAY_KEY_ID=your_razorpay_key

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key
```

### Business Rules Configuration

- Payment reminder days: [7, 3, 1, 0] days before due
- Maximum call attempts: 3 per customer
- Risk score thresholds: Low (<40), Medium (40-70), High (>70)
- Escalation triggers: Risk >85, Negative sentiment, Multiple failures

## 📈 Analytics & Insights

The system provides comprehensive analytics:

### Interaction Analytics

- Total interactions and outcomes
- Success rates by customer segment
- Best call times and days
- Sentiment trends

### Payment Analytics

- Collection rates and amounts
- Payment method preferences
- Time-to-payment analysis
- Failed payment analysis

### Business Insights

- Customer segmentation performance
- Agent effectiveness metrics
- Optimization recommendations
- Predictive modeling results

## 🔮 ML & Learning Features

### Outcome Prediction Model

- Predicts conversation success probability
- Uses customer features and historical data
- Continuously learns from new interactions
- Feature importance analysis

### Pattern Recognition

- Identifies optimal call timing
- Detects customer behavior patterns
- Optimizes conversation strategies
- Recommends process improvements

## 🚀 Production Deployment

### Scaling Considerations

- Replace SQLite with PostgreSQL for production
- Implement Redis for caching and session management
- Use actual Twilio/Razorpay APIs instead of simulations
- Deploy with Docker/Kubernetes for scalability

### Integration Points

- CRM system integration for customer data
- Core banking system for loan information
- Payment gateway APIs for real transactions
- Monitoring and alerting systems

## 🤝 Contributing

This is a complete, working implementation ready for:

- Further customization for specific business needs
- Integration with existing systems
- Enhancement with additional AI capabilities
- Production deployment

## 📝 License

This project is available for demonstration and educational purposes.

---

## 🎉 Summary

This EMI VoiceBot System demonstrates a complete, working implementation of an AI-powered collection system with:

- **6 Intelligent Agents** working in coordination
- **Multi-language Support** for diverse customer base
- **AI-Powered Conversations** with sentiment analysis
- **Intelligent Decision Making** with escalation logic
- **Secure Payment Processing** with multiple channels
- **Machine Learning** for continuous improvement
- **Comprehensive Analytics** for business insights
- **Production-Ready Architecture** with proper logging and error handling

The system is fully functional and ready for demonstration, customization, and production deployment.

**Ready to see it in action? Run `./start.sh` and choose option 1 for the complete demo!** 🚀

End-to-End Architecture Overview
🔹 1. Trigger Agent
• Function: Monitors EMI due dates and initiates workflow.
• Code Needs:
o Scheduler (e.g., cron job or event-driven trigger)
o API to fetch EMI data from Loan Management System
🔹 2. Context Agent
• Function: Gathers customer profile, payment history, language preference, risk score.
• Code Needs:
o REST API integrations (CRM, risk scoring service)
o Caching layer (Redis or in-memory store)
🔹 3. VoiceBot Agent
• Function: Conducts multilingual, dynamic conversations.
• Code Needs:
o TTS/STT integration (Google Dialogflow, AWS Lex, Twilio Voice)
o Conversation flow logic (state machine or intent-based)
o Language model (LLM or fine-tuned NLU model)
🔹 4. Decision Agent
• Function: Determines next steps based on interaction.
• Code Needs:
o Rule engine or ML model (e.g., XGBoost or decision tree)
o Escalation logic (to human agent or rescheduling)
🔹 5. Payment Agent
• Function: Sends secure payment links and confirms transactions.
• Code Needs:
o Integration with Razorpay/PayU/PhonePe APIs
o SMS/WhatsApp API (Twilio, Gupshup)
🔹 6. Logging & Learning Agent
• Function: Logs interactions, learns from outcomes.
• Code Needs:
o Logging system (ELK stack or cloud logging)
o Feedback loop (simple reinforcement learning or analytics dashboard)

🧑‍💻 Technologies & Tools
Layer Tools
Backend Python (FastAPI/Flask), Node.js
VoiceBot Twilio, Google Dialogflow, AWS Lex
AI/ML HuggingFace Transformers, scikit-learn, LangChain
Database PostgreSQL, MongoDB
Cache Redis
Payment Razorpay, PayU
Messaging Twilio, WhatsApp Business API
Deployment Docker, Kubernetes, AWS/GCP

✅ Next Steps
If you're ready, I can start coding each module step-by-step. You can choose:

1. Start with Trigger + Context Agent
2. Jump directly to VoiceBot Agent
3. Build the entire pipeline in one go
   Let me know your preference, and I’ll begin coding accordingly.
