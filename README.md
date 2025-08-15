# EMI VoiceBot System - Complete Implementation

## 🚀 Overview

This is a complete, working implementation of an **Agentic VoiceBot System for EMI Collections/Payments**. The system uses multiple AI agents working together to automate EMI collection calls, process payments, and learn from interactions.

## 🏗️ Architecture

The system consists of 6 intelligent agents:

### 🔹 1. Trigger Agent

- **Function**: Monitors EMI due dates and initiates workflow
- **Features**:
  - Scheduled EMI checks (configurable times)
  - Priority-based customer targeting
  - Manual trigger support for testing

### 🔹 2. Context Agent

- **Function**: Gathers comprehensive customer context
- **Features**:
  - Customer profile & risk scoring
  - Payment history analysis
  - Language preference detection
  - Communication preference learning

### 🔹 3. VoiceBot Agent

- **Function**: Conducts multilingual, dynamic conversations
- **Features**:
  - Multi-language support (English, Hindi)
  - AI-powered conversation simulation
  - Sentiment analysis
  - Intent recognition

### 🔹 4. Decision Agent

- **Function**: Determines next steps based on interactions
- **Features**:
  - Rule-based decision engine
  - Escalation logic
  - Priority management
  - Channel recommendation

### 🔹 5. Payment Agent

- **Function**: Manages payment links and transactions
- **Features**:
  - Secure payment link generation
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
