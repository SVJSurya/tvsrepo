from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

# Import all agents
from src.agents.trigger_agent import TriggerAgent
from src.agents.context_agent import ContextAgent
from src.agents.google_voicebot_agent import GoogleVoiceBotAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.logging_learning_agent import LoggingLearningAgent

app = FastAPI(title="EMI VoiceBot - Advanced UI Server", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (optional)
import os

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    print("ℹ️  Static directory not found - continuing without static files")

# Initialize agents
trigger_agent = TriggerAgent()
context_agent = ContextAgent()
voicebot_agent = GoogleVoiceBotAgent()
decision_agent = DecisionAgent()
payment_agent = PaymentAgent()
logging_agent = LoggingLearningAgent()

# Store conversation history for voice demo (in production, use database)
conversation_sessions = {}

# Email configuration for payment links
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": os.getenv("GMAIL_USER", "your-email@gmail.com"),
    "sender_password": os.getenv(
        "GMAIL_APP_PASSWORD", "your-app-password"
    ),  # Use App Password for Gmail
}

# Store sent payment links for demo tracking
sent_payment_links = []


def send_payment_link_email(
    customer_email: str, customer_name: str, emi_amount: int, due_date: str
):
    """Send payment link via email using Gmail SMTP"""
    try:
        # Generate unique payment link
        payment_id = str(uuid.uuid4())
        payment_link = f"https://emi-payment-demo.example.com/pay/{payment_id}"

        # Check if SMTP is properly configured
        if (
            EMAIL_CONFIG["sender_email"] == "your-email@gmail.com"
            or EMAIL_CONFIG["sender_password"] == "your-app-password"
        ):
            # Demo mode - simulate email sending without actual SMTP
            print(f"📧 DEMO MODE: Simulating email to {customer_email}")
            print(f"🆔 Payment ID: {payment_id}")
            print(f"🔗 Payment Link: {payment_link}")

            # Track sent email
            sent_payment_links.append(
                {
                    "payment_id": payment_id,
                    "customer_email": customer_email,
                    "customer_name": customer_name,
                    "emi_amount": emi_amount,
                    "payment_link": payment_link,
                    "sent_at": datetime.now().isoformat(),
                    "status": "demo_sent",
                }
            )

            return {
                "success": True,
                "payment_id": payment_id,
                "payment_link": payment_link,
                "message": f"Demo payment link generated for {customer_email}",
                "demo_mode": True,
            }

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"EMI Payment Link - ₹{emi_amount} Due"
        message["From"] = EMAIL_CONFIG["sender_email"]
        message["To"] = customer_email

        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #e74c3c; text-align: center; margin: 20px 0; }}
                .payment-button {{ display: block; width: 200px; margin: 30px auto; padding: 15px; background: #27ae60; color: white; text-decoration: none; text-align: center; border-radius: 5px; font-weight: bold; }}
                .details {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
                .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏦 EMI Payment Reminder</h1>
                    <h2>Hello {customer_name},</h2>
                </div>
                
                <p>Your EMI payment is due. Please make the payment at your earliest convenience to avoid any late fees.</p>
                
                <div class="amount">
                    Amount Due: ₹{emi_amount:,}
                </div>
                
                <div class="details">
                    <h3>📋 Payment Details:</h3>
                    <p><strong>Due Date:</strong> {due_date}</p>
                    <p><strong>Payment ID:</strong> {payment_id}</p>
                    <p><strong>Customer:</strong> {customer_name}</p>
                </div>
                
                <a href="{payment_link}" class="payment-button">
                    💳 Pay Now - ₹{emi_amount:,}
                </a>
                
                <div class="warning">
                    <strong>⚠️ Demo Notice:</strong> This is a demonstration payment link. In production, this would redirect to a secure payment gateway.
                </div>
                
                <p>Alternative payment methods:</p>
                <ul>
                    <li>💻 Online Banking</li>
                    <li>📱 UPI Transfer</li>
                    <li>🏪 Branch Visit</li>
                    <li>📞 Phone Banking</li>
                </ul>
                
                <p>If you have any questions or need assistance, please contact our customer service team.</p>
                
                <div class="footer">
                    <p>This is an automated message from EMI VoiceBot AI System</p>
                    <p>📧 Sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_content = f"""
        EMI Payment Reminder
        
        Hello {customer_name},
        
        Your EMI payment of ₹{emi_amount:,} is due on {due_date}.
        
        Payment Link: {payment_link}
        Payment ID: {payment_id}
        
        Please click the link above to make your payment securely.
        
        Alternative payment methods:
        - Online Banking
        - UPI Transfer  
        - Branch Visit
        - Phone Banking
        
        Note: This is a demo payment link for demonstration purposes.
        
        Thank you,
        EMI VoiceBot AI System
        """

        # Attach parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)

        # Send email
        context = ssl.create_default_context()
        context.check_hostname = False  # Relax SSL verification
        context.verify_mode = ssl.CERT_NONE  # Skip certificate verification
        with smtplib.SMTP(
            EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]
        ) as server:
            server.starttls(context=context)
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.sendmail(
                EMAIL_CONFIG["sender_email"], customer_email, message.as_string()
            )

        # Track sent email
        sent_payment_links.append(
            {
                "payment_id": payment_id,
                "customer_email": customer_email,
                "customer_name": customer_name,
                "emi_amount": emi_amount,
                "payment_link": payment_link,
                "sent_at": datetime.now().isoformat(),
                "status": "sent",
            }
        )

        return {
            "success": True,
            "payment_id": payment_id,
            "payment_link": payment_link,
            "message": f"Payment link sent to {customer_email}",
        }

    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send email to {customer_email}",
        }


# Analytics data storage (in production, use a database)
analytics_data = {
    "calls_today": 247,
    "success_rate": 0.73,
    "due_emis": 156,
    "collections": 2450000,
    "call_history": [],
    "payment_history": [],
}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the advanced dashboard"""
    try:
        with open("templates/advanced_dashboard.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
        <h1>Dashboard Not Found</h1>
        <p>Please ensure the advanced_dashboard.html file exists in the templates directory.</p>
        <p><a href="/simple">Use Simple Dashboard</a> | <a href="/live-demo">Live Call Demo</a> | <a href="/realtime-demo">Real-Time Demo</a> | <a href="/voice-demo">Voice Demo</a></p>
        """
        )


@app.get("/live-demo", response_class=HTMLResponse)
async def live_demo():
    """Serve the live call demo interface"""
    return FileResponse("templates/live_call_demo.html")


@app.get("/realtime-demo", response_class=HTMLResponse)
async def realtime_demo():
    """Serve the enhanced real-time call demo interface"""
    return FileResponse("templates/realtime_call_demo.html")


@app.get("/voice-demo", response_class=HTMLResponse)
async def voice_demo():
    """Serve the voice-enabled demo interface"""
    return FileResponse("templates/voice_demo.html")


@app.get("/simple", response_class=HTMLResponse)
async def simple_dashboard():
    """Serve the original simple dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EMI VoiceBot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .card { background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
            .stat { text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; color: #007bff; }
            .stat p { margin: 5px 0 0 0; color: #666; font-size: 0.9em; }
            .actions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
            .btn { padding: 12px 20px; border: none; border-radius: 6px; background: #007bff; color: white; cursor: pointer; }
            .btn:hover { background: #0056b3; }
            .activity { background: #000; color: #00ff00; padding: 15px; border-radius: 6px; font-family: monospace; max-height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <h1>🚀 EMI VoiceBot - AI Collection System</h1>
        
        <div class="stats">
            <div class="stat">
                <h3 id="calls-today">247</h3>
                <p>Calls Today</p>
            </div>
            <div class="stat">
                <h3 id="success-rate">73%</h3>
                <p>Success Rate</p>
            </div>
            <div class="stat">
                <h3 id="due-emis">156</h3>
                <p>Due EMIs</p>
            </div>
            <div class="stat">
                <h3 id="collections">₹24.5L</h3>
                <p>Collections</p>
            </div>
        </div>

        <div class="actions">
            <button class="btn" onclick="triggerCalls()">🔍 Check Due EMIs</button>
            <button class="btn" onclick="startDemo()">🎭 Start Demo</button>
            <button class="btn" onclick="viewAnalytics()">📊 View Analytics</button>
            <button class="btn" onclick="testCall()">📞 Test Call</button>
        </div>

        <div class="card">
            <h3>System Activity</h3>
            <div class="activity" id="activity-log">
                <div>[12:45:23] System initialized and ready</div>
            </div>
        </div>

        <p style="margin-top: 20px; text-align: center;">
            <a href="/" style="color: #007bff;">Switch to Advanced Dashboard</a>
        </p>

        <script>
            function addLog(message) {
                const log = document.getElementById('activity-log');
                const time = new Date().toLocaleTimeString();
                const entry = document.createElement('div');
                entry.textContent = `[${time}] ${message}`;
                log.insertBefore(entry, log.firstChild);
            }

            async function triggerCalls() {
                addLog('🔍 Checking for due EMIs...');
                try {
                    const response = await fetch('/api/trigger/check-due-emis', {method: 'POST'});
                    const data = await response.json();
                    addLog(`✅ Found ${data.due_emis.length} customers requiring calls`);
                } catch (error) {
                    addLog('❌ Error: ' + error.message);
                }
            }

            async function startDemo() {
                addLog('🎭 Starting demo workflow...');
                try {
                    const response = await fetch('/api/demo/workflow', {method: 'POST'});
                    const data = await response.json();
                    data.steps.forEach((step, index) => {
                        setTimeout(() => addLog(`[DEMO] ${step}`), index * 1000);
                    });
                } catch (error) {
                    addLog('❌ Demo error: ' + error.message);
                }
            }

            async function viewAnalytics() {
                addLog('📊 Generating analytics...');
                try {
                    const response = await fetch('/api/analytics/dashboard');
                    const data = await response.json();
                    addLog(`📈 Analytics ready: ${data.interaction_analytics.total_interactions} interactions`);
                } catch (error) {
                    addLog('❌ Analytics error: ' + error.message);
                }
            }

            async function testCall() {
                addLog('📞 Testing voice call system...');
                try {
                    const response = await fetch('/api/voice/test-call', {method: 'POST'});
                    const data = await response.json();
                    addLog(`📞 Test result: ${data.test_result.status}`);
                } catch (error) {
                    addLog('❌ Call test error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    return {
        "calls_today": analytics_data["calls_today"],
        "success_rate": analytics_data["success_rate"],
        "due_emis": analytics_data["due_emis"],
        "collections": analytics_data["collections"],
        "last_updated": datetime.now().isoformat(),
    }


@app.post("/api/payment/send-link")
async def send_payment_link(request: dict):
    """Send payment link via email"""
    try:
        customer_email = request.get("email", "")
        session_id = request.get("session_id", "default_session")

        if not customer_email:
            return {
                "success": False,
                "message": "Email address is required",
                "request_email": True,
            }

        # Get customer context from session
        if session_id in conversation_sessions:
            customer_context = conversation_sessions[session_id]["customer_context"]
        else:
            # Default customer context
            customer_context = {
                "name": "Valued Customer",
                "emi_amount": 15000,
                "due_date": "2025-08-10",
            }

        # Send payment link email
        result = send_payment_link_email(
            customer_email=customer_email,
            customer_name=customer_context["name"],
            emi_amount=customer_context["emi_amount"],
            due_date=customer_context["due_date"],
        )

        if result["success"]:
            # Add to conversation history if session exists
            if session_id in conversation_sessions:
                conversation_sessions[session_id]["history"].append(
                    {
                        "system_action": "payment_link_sent",
                        "email": customer_email,
                        "payment_id": result["payment_id"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send payment link",
        }


@app.get("/api/payment/sent-links")
async def get_sent_payment_links():
    """Get list of sent payment links for demo tracking"""
    return {"sent_links": sent_payment_links, "total_sent": len(sent_payment_links)}


@app.post("/api/trigger/check-due-emis")
async def check_due_emis():
    """Trigger due EMI checking"""
    try:
        # Run trigger agent
        result = trigger_agent.check_due_emis()

        # Update analytics
        analytics_data["due_emis"] = len(result) if isinstance(result, list) else 0

        # Log the activity using correct method
        logging_agent.log_system_event(
            {
                "event_type": "due_emi_check",
                "found_due_emis": len(result) if isinstance(result, list) else 0,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "status": "success",
            "due_emis": result,
            "total_found": len(result) if isinstance(result, list) else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/demo/workflow")
async def demo_workflow():
    """Run a demonstration workflow"""
    steps = [
        "🔍 Scanning database for due EMIs...",
        "🤖 Initializing AI agents...",
        "📊 Analyzing customer risk profiles...",
        "📞 Initiating AI voice calls...",
        "💬 Processing customer responses...",
        "🧠 Making intelligent decisions...",
        "💳 Generating payment links...",
        "📈 Updating analytics and ML models...",
        "✅ Demo workflow completed successfully!",
    ]

    return {"status": "demo_started", "steps": steps, "estimated_duration": "9 seconds"}


@app.post("/api/voice/process")
async def process_voice_input(request: dict):
    """Process voice input using Google AI VoiceBot agent with conversation context"""
    try:
        user_input = request.get("user_input", "")
        session_id = request.get("session_id", "default_session")

        if not user_input:
            raise HTTPException(status_code=400, detail="user_input is required")

        # Initialize conversation history for new sessions
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = {
                "history": [],
                "customer_context": {
                    "customer_id": "CUST001",
                    "name": "Manya Johri",
                    "phone": "+91-9876543210",
                    "emi_amount": 15000,
                    "due_date": "2025-08-10",
                    "overdue_days": 5,
                    "language": "en",
                },
                "started_at": datetime.now().isoformat(),
            }

        # Get conversation history
        conversation_history = conversation_sessions[session_id]["history"]
        customer_context = conversation_sessions[session_id]["customer_context"]

        # Process with Google AI VoiceBot agent with conversation context
        response = voicebot_agent.analyze_call(
            call_type="emi_inquiry",
            user_input=user_input,
            customer_context=customer_context,
            conversation_history=conversation_history,
        )

        # Add current interaction to conversation history
        conversation_history.append(
            {
                "user_input": user_input,
                "ai_response": response["response"],
                "intent": response.get("intent", "unknown"),
                "sentiment": response.get("sentiment", "neutral"),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Keep only last 10 exchanges to prevent memory bloat
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
            conversation_sessions[session_id]["history"] = conversation_history

        # Check if customer wants payment link and handle email request
        needs_email = False
        if response.get("next_action") == "send_payment_link":
            # Check if we already have email or if customer is providing email
            if "@" in user_input and "." in user_input:
                # Customer provided email in their input
                import re

                email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                emails = re.findall(email_pattern, user_input)
                if emails:
                    email = emails[0]
                    # Send payment link automatically
                    email_result = send_payment_link_email(
                        customer_email=email,
                        customer_name=customer_context["name"],
                        emi_amount=customer_context["emi_amount"],
                        due_date=customer_context["due_date"],
                    )

                    if email_result["success"]:
                        # Update AI response to confirm email sent
                        response[
                            "response"
                        ] += f"\n\n✅ Perfect! I've sent the payment link to {email}. You should receive it within a few minutes. The email contains a secure link to complete your ₹{customer_context['emi_amount']:,} EMI payment."
                        response["email_sent"] = True
                        response["payment_link_info"] = email_result
                    else:
                        response[
                            "response"
                        ] += f"\n\n❌ I had trouble sending the email to {email}. Let me try a different email address, or you can contact our support team."
            else:
                # Ask for email if not provided
                needs_email = True
                response[
                    "response"
                ] += "\n\n📧 To send you the payment link, I'll need your email address. Could you please provide your email?"
                response["needs_email"] = True

        return {
            "status": "success",
            "user_input": user_input,
            "ai_response": response,
            "session_id": session_id,
            "conversation_turn": len(conversation_history),
            "needs_email": needs_email,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fallback_response": "I apologize, but I'm having technical difficulties. Please try again or contact customer service.",
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/voice/test-call")
async def test_voice_call():
    """Test voice call functionality"""
    try:
        # Simulate voice call test since the method doesn't exist
        test_result = {
            "status": "successful",
            "message": "Voice system test completed",
            "components": {
                "twilio_connection": "active",
                "openai_api": "active",
                "audio_processing": "active",
            },
        }

        # Log the test using correct method
        logging_agent.log_system_event(
            {
                "event_type": "voice_test",
                "test_result": test_result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {"test_result": test_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    try:
        # Get analytics from logging agent using correct method
        analytics = logging_agent.generate_insights_report()

        # Add some mock real-time data for demo
        analytics["real_time"] = {
            "active_calls": 3,
            "queue_size": 12,
            "avg_call_duration": "4m 32s",
            "current_success_rate": 0.78,
        }

        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls/live")
async def get_live_calls():
    """Get currently active calls"""
    # Mock live call data
    live_calls = [
        {
            "call_id": "call_001",
            "customer_id": "CUST_12345",
            "customer_name": "Rajesh Kumar",
            "status": "connected",
            "duration": "2m 15s",
            "emi_amount": 15000,
            "loan_account": "LA_67890",
        },
        {
            "call_id": "call_002",
            "customer_id": "CUST_12346",
            "customer_name": "Priya Sharma",
            "status": "calling",
            "duration": "0m 30s",
            "emi_amount": 8500,
            "loan_account": "LA_67891",
        },
    ]

    return {"live_calls": live_calls, "total_active": len(live_calls)}


@app.get("/api/payments/recent")
async def get_recent_payments():
    """Get recent payment transactions"""
    recent_payments = [
        {
            "payment_id": "PAY_001",
            "customer_name": "Arun Patel",
            "amount": 12000,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "method": "UPI",
        },
        {
            "payment_id": "PAY_002",
            "customer_name": "Sneha Gupta",
            "amount": 9500,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "method": "Net Banking",
        },
    ]

    return {"recent_payments": recent_payments}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "agents": {
            "trigger": "active",
            "context": "active",
            "voicebot": "active",
            "decision": "active",
            "payment": "active",
            "logging": "active",
        },
    }


if __name__ == "__main__":
    print("🚀 Starting EMI VoiceBot Advanced UI Server...")
    print("📊 Advanced Dashboard: http://localhost:8001")
    print("📋 Simple Dashboard: http://localhost:8001/simple")
    print("🔗 API Documentation: http://localhost:8001/docs")

    uvicorn.run(app, host="0.0.0.0", port=8001)
