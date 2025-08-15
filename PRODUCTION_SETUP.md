# 🚀 Production Setup Guide for EMI VoiceBot System

## Overview

This guide explains how to transition from demo mode to production with real data for presentations and live environments.

## 🔧 1. Environment Configuration

### Step 1: Update API Keys in `config/settings.py`

```python
# Required API Keys for Production
OPENAI_API_KEY = "sk-your-actual-openai-key"
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_PHONE_NUMBER = "+1234567890"  # Your Twilio number
RAZORPAY_KEY_ID = "rzp_live_your-key-id"
RAZORPAY_SECRET_KEY = "your-razorpay-secret"
```

### Step 2: Database Configuration

#### Option A: PostgreSQL (Recommended for Production)

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/emi_production"
```

#### Option B: MySQL

```python
DATABASE_URL = "mysql://username:password@localhost:3306/emi_production"
```

#### Option C: SQLite (for presentations/demos)

```python
DATABASE_URL = "sqlite:///emi_production.db"
```

## 📊 2. Real Data Integration

### A. Customer Data Import

Create a CSV file with your customer data:

```csv
customer_id,name,phone_number,email,language_preference,status
1001,John Doe,+919876543210,john@example.com,en,active
1002,राज कुमार,+919876543211,raj@example.com,hi,active
1003,Priya Sharma,+919876543212,priya@example.com,hi,active
```

### B. Loan Data Import

```csv
loan_id,customer_id,loan_amount,outstanding_amount,emi_amount,due_date,status
2001,1001,500000,450000,15000,2025-08-20,active
2002,1002,300000,280000,12000,2025-08-18,active
2003,1003,200000,180000,8000,2025-08-25,active
```

## 🎯 3. Production Deployment Options

### Option 1: API Server Mode (for Presentations)

```bash
# Start the API server
./start.sh
# Choose option 2: Start API Server
```

Then use API endpoints:

- `POST /api/trigger/check-due-emis` - Check due EMIs
- `POST /api/voice/initiate-call` - Start voice calls
- `GET /api/analytics/dashboard` - View analytics

### Option 2: Scheduled Production Mode

```python
# Add to crontab for automated execution
0 9 * * * cd /path/to/project && python production_runner.py
```

### Option 3: Interactive Presentation Mode

```bash
./start.sh
# Choose option 3: Run Interactive Demo
```

## 📱 4. Real Communication Channels

### A. Voice Calls (Twilio)

- Configure your Twilio webhook URLs
- Set up call recording and transcription
- Configure international calling if needed

### B. SMS Integration

- Set up SMS templates in multiple languages
- Configure delivery reports
- Set up opt-out handling

### C. WhatsApp Business API

- Configure WhatsApp Business account
- Set up message templates
- Handle media messages

## 💳 5. Payment Integration

### A. Razorpay Setup

1. Create Razorpay account
2. Configure payment methods (UPI, Cards, Net Banking)
3. Set up webhooks for payment status
4. Configure settlement accounts

### B. Payment Flow

1. Generate secure payment links
2. Send via SMS/WhatsApp
3. Handle payment confirmations
4. Update loan records automatically

## 📈 6. Analytics & Monitoring

### A. Dashboard Setup

- Real-time call statistics
- Payment conversion rates
- Customer response analytics
- Agent performance metrics

### B. Monitoring

- Set up application monitoring
- Configure error alerting
- Track API performance
- Monitor database health

## 🎭 7. Presentation Demo Setup

### For Live Presentations:

1. **Quick Demo Data Setup:**

```bash
python setup_demo_data.py --mode=presentation
```

2. **Real-time Demo:**

```bash
python live_demo.py --customers=5 --show-ui
```

3. **Interactive Dashboard:**

- Open browser to `http://localhost:8000/dashboard`
- Show real-time call progress
- Display analytics in real-time

## 🔐 8. Security Configuration

### A. Environment Variables

```bash
export OPENAI_API_KEY="your-key"
export TWILIO_AUTH_TOKEN="your-token"
export DATABASE_URL="your-db-url"
```

### B. SSL/HTTPS

- Configure SSL certificates
- Set up secure webhooks
- Enable encryption for sensitive data

## 🎯 9. Business Configuration

### A. Calling Rules

```python
# Configure calling windows
CALLING_HOURS = {
    "start": "09:00",
    "end": "18:00",
    "timezone": "Asia/Kolkata"
}

# Configure retry logic
MAX_CALL_ATTEMPTS = 3
RETRY_INTERVALS = [1, 3, 7]  # days
```

### B. Payment Terms

```python
# Configure payment reminders
REMINDER_SCHEDULE = [7, 3, 1, 0]  # days before due
GRACE_PERIOD = 3  # days after due date
```

## 📊 10. Data Migration

### From Existing Systems:

```python
# Migration script example
python migrate_data.py \
    --source="legacy_db" \
    --target="production_db" \
    --validate \
    --dry-run
```

## 🚀 Quick Start for Presentations

### 1. Minimum Setup (5 minutes):

```bash
# Set OpenAI key only
export OPENAI_API_KEY="your-key"

# Use SQLite for quick demo
python quick_demo.py --real-conversations
```

### 2. Full Demo Setup (15 minutes):

```bash
# Configure all services
./configure_production.py --mode=demo

# Import sample real data
python import_data.py --file=sample_customers.csv

# Start presentation mode
./start.sh --mode=presentation
```

### 3. Live Call Demo:

```bash
# Make actual calls to test numbers
python live_call_demo.py --phone="+919876543210" --test-mode
```

## 📞 Support and Troubleshooting

### Common Issues:

1. **API Key Errors**: Verify all keys are correctly set
2. **Database Connection**: Check database URL and credentials
3. **Call Failures**: Verify Twilio configuration
4. **Payment Issues**: Check Razorpay webhook setup

### Logs Location:

- Application logs: `logs/application.log`
- Call logs: `logs/calls/`
- Payment logs: `logs/payments/`
- Error logs: `logs/errors.log`

## 🎯 Next Steps

1. **Start with SQLite** for presentations
2. **Add OpenAI key** for real conversations
3. **Configure Twilio** for actual calls
4. **Set up payment gateway** for real transactions
5. **Import your customer data**
6. **Run live demo** for stakeholders

This system is designed to scale from demo to production seamlessly!
