# 🚀 EMI VoiceBot - Deployment Guide

## Quick Setup for Other Machines

### Prerequisites
- **Python 3.8+** installed
- **Git** (to clone the repository)
- **Internet connection** (for package installation)

### 🔧 One-Command Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Manya-TVS-Project

# Run the automated setup script
./setup.sh
```

### 📋 Manual Setup (Alternative)

If you prefer manual setup or the automated script doesn't work:

#### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Environment
Copy `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
# Edit .env with your actual API keys and credentials
```

#### 4. Start the Server
```bash
python advanced_ui_server.py
```

### 🔑 Required API Keys & Credentials

#### 1. Google AI API Key (FREE)
- Visit: https://makersuite.google.com/app/apikey
- Create new API key
- Add to `.env` file: `GOOGLE_API_KEY=your_api_key_here`
- **Free Tier**: 15 requests/minute, 1M tokens/month

#### 2. Gmail SMTP (For Email Features)
- Enable 2-Factor Authentication on Gmail
- Generate App Password: https://support.google.com/accounts/answer/185833
- Add to `.env` file:
  ```
  GMAIL_USER=your_email@gmail.com
  GMAIL_APP_PASSWORD=your_16_character_app_password
  ```

#### 3. Optional Credentials
- **Twilio**: For SMS/Voice (if needed)
- **OpenAI**: Fallback AI service
- **Razorpay**: Payment processing
- **Database**: PostgreSQL/MySQL for production

### 🌐 Access Points

After successful setup:

| Interface | URL | Description |
|-----------|-----|-------------|
| **Advanced Dashboard** | http://localhost:8001 | Main admin interface |
| **Live Call Demo** | http://localhost:8001/live-demo | Interactive voice demo |
| **Voice Demo** | http://localhost:8001/voice-demo | Voice conversation interface |
| **API Documentation** | http://localhost:8001/docs | FastAPI auto-generated docs |
| **Health Check** | http://localhost:8001/health | System status |

### 📁 Project Structure

```
Manya-TVS-Project/
├── 📄 advanced_ui_server.py          # Main FastAPI server
├── 📄 requirements.txt               # Python dependencies
├── 📄 setup.sh                      # Automated setup script
├── 📄 .env                          # Environment configuration
├── 📁 src/agents/                   # AI Agent modules
│   ├── trigger_agent.py
│   ├── context_agent.py
│   ├── google_voicebot_agent.py
│   ├── decision_agent.py
│   ├── payment_agent.py
│   └── logging_learning_agent.py
├── 📁 templates/                    # HTML interfaces
│   ├── advanced_dashboard.html
│   ├── live_call_demo.html
│   └── voice_demo.html
├── 📁 logs/                        # Application logs
├── 📁 temp/                        # Temporary files
└── 📁 docs/                        # Documentation
    ├── ARCHITECTURE_WORKFLOW.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── DEMO_PRESENTATION_GUIDE.md
    └── DEMO_QUICK_REFERENCE.md
```

### ⚡ Quick Start Commands

```bash
# Activate environment
source venv/bin/activate

# Start development server
python advanced_ui_server.py

# Test Google AI connection
python test_google_ai.py

# Test email functionality
python test_gmail_smtp.py

# Run health check
curl http://localhost:8001/health
```

### 🔧 Production Deployment

#### Docker Setup (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "advanced_ui_server.py"]
```

#### Environment Variables for Production
```bash
# Production settings
DEBUG_MODE=False
SERVER_HOST=0.0.0.0
SERVER_PORT=8001

# Database (Required for production)
DATABASE_URL=postgresql://user:password@db:5432/emi_voicebot

# Redis Cache (Recommended)
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_super_secret_key_here
```

### 🛠️ Troubleshooting

#### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Google AI API Errors**
   ```bash
   # Check API key configuration
   python test_google_ai.py
   ```

3. **Email Not Sending**
   ```bash
   # Test SMTP configuration
   python test_gmail_smtp.py
   ```

4. **Port Already in Use**
   ```bash
   # Check what's using port 8001
   lsof -i :8001
   # Kill the process or change port in .env
   ```

#### System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space
- **OS**: Linux, macOS, Windows (WSL recommended)
- **Python**: 3.8, 3.9, 3.10, or 3.11

### 📊 Monitoring & Logs

#### Log Files
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

#### Health Monitoring
```bash
# Check system health
curl http://localhost:8001/health

# Check API status
curl http://localhost:8001/api/stats
```

### 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` file to version control
2. **API Keys**: Use environment variables, not hardcoded values
3. **HTTPS**: Use SSL certificates in production
4. **Firewall**: Restrict access to necessary ports only
5. **Updates**: Keep dependencies updated regularly

### 📚 Additional Resources

- **Architecture Documentation**: `ARCHITECTURE_WORKFLOW.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Demo Instructions**: `DEMO_PRESENTATION_GUIDE.md`
- **Quick Reference**: `DEMO_QUICK_REFERENCE.md`

### 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files in `logs/` directory
3. Verify all credentials in `.env` file
4. Test individual components using test scripts
5. Ensure all required files are present

### 🎯 Success Validation

After setup, verify everything works:

✅ **Server starts without errors**
✅ **Dashboard loads at http://localhost:8001**
✅ **Google AI responds to test queries**
✅ **Email functionality works (if configured)**
✅ **Voice demo interface loads**
✅ **Health check returns "healthy" status**

---

**Happy deploying! 🚀**
