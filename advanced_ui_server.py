from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
import logging
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

# Set up logging
logger = logging.getLogger(__name__)

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
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMI VoiceBot - Live Call Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }

        .demo-container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .demo-header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .demo-header h1 {
            color: #2a5298;
            margin-bottom: 10px;
        }

        .demo-setup {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .phone-setup {
            display: flex;
            gap: 15px;
            align-items: center;
            margin-bottom: 20px;
        }

        .phone-setup input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(102, 126, 234, 0.3);
        }

        .btn-success {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }

        .btn-danger {
            background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        }

        .demo-customers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .customer-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            position: relative;
        }

        .customer-card.calling {
            border-left: 5px solid #ffc107;
            background: linear-gradient(45deg, #fff9c4, #ffffff);
        }

        .customer-card.connected {
            border-left: 5px solid #28a745;
            background: linear-gradient(45deg, #d4edda, #ffffff);
        }

        .customer-info h3 {
            color: #2a5298;
            margin-bottom: 10px;
        }

        .customer-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }

        .customer-details span {
            color: #666;
        }

        .call-status {
            margin-top: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }

        .call-step {
            padding: 5px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .call-step:last-child {
            border-bottom: none;
        }

        .call-step.current {
            background: #e3f2fd;
            color: #1976d2;
            font-weight: bold;
            padding: 8px;
            border-radius: 4px;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        .audio-controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .audio-visualizer {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
            height: 50px;
            margin: 20px 0;
        }

        .audio-bar {
            width: 4px;
            background: #667eea;
            border-radius: 2px;
            transition: height 0.1s ease;
        }

        .audio-message {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }

        .user-input-panel {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 2px solid #28a745;
        }

        .input-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .input-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            transition: all 0.3s;
            text-align: center;
        }

        .input-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(40, 167, 69, 0.3);
        }

        .input-btn:active {
            transform: scale(0.95);
        }

        .input-btn.option-1 {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }

        .input-btn.option-2 {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        }

        .response-message {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #28a745;
            animation: fadeIn 0.5s ease-in;
        }

        .email-input-section {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #007bff;
        }

        .email-input-section input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #007bff;
            border-radius: 8px;
            font-size: 16px;
            margin: 10px 0;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .status-indicator {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #6c757d;
        }

        .status-indicator.calling {
            background: #ffc107;
            animation: pulse 1s infinite;
        }

        .status-indicator.connected {
            background: #28a745;
        }

        .status-indicator.completed {
            background: #17a2b8;
        }

        .demo-controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .control-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 15px;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }

        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 80%;
            max-width: 500px;
            position: relative;
        }

        .close {
            position: absolute;
            right: 20px;
            top: 15px;
            font-size: 2rem;
            cursor: pointer;
            color: #999;
        }

        .close:hover {
            color: #333;
        }

        @media (max-width: 768px) {
            .phone-setup {
                flex-direction: column;
            }
            
            .demo-customers {
                grid-template-columns: 1fr;
            }
            
            .control-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <!-- Header -->
        <div class="demo-header">
            <h1>🎭 Live Call Demo System</h1>
            <p>Experience real-time AI-powered EMI collection calls with audio feedback</p>
        </div>

        <!-- Setup Section -->
        <div class="demo-setup">
            <h3>📞 Interactive Demo Setup</h3>
            <div class="alert alert-info">
                <strong>Interactive Demo Mode:</strong> This enhanced demo includes real customer interaction simulation!<br>
                • Play AI voice messages with text-to-speech<br>
                • Respond to prompts by clicking buttons or pressing keyboard keys (1 or 2)<br>
                • Send actual payment links to email addresses via Gmail SMTP<br>
                • Experience the complete customer journey from call to payment
            </div>
            
            <div class="phone-setup">
                <input type="tel" id="phoneNumber" placeholder="+91XXXXXXXXXX" value="+919876543210">
                <button class="btn" onclick="setupPhone()">Setup Demo Phone</button>
            </div>
            
            <div id="setupStatus"></div>
        </div>

        <!-- Audio Controls -->
        <div class="audio-controls">
            <h3>🔊 Audio Demo Controls</h3>
            <div class="control-group">
                <button class="btn btn-success" onclick="playDemoMessage('english')">
                    🗣️ Play English Message
                </button>
                <button class="btn btn-success" onclick="playDemoMessage('hindi')">
                    🗣️ Play Hindi Message
                </button>
                <button class="btn btn-danger" onclick="stopAudio()">
                    ⏹️ Stop Audio
                </button>
            </div>
            
            <div class="audio-visualizer" id="audioVisualizer">
                <!-- Audio bars will be generated here -->
            </div>
            
            <div class="audio-message" id="currentMessage" style="display: none;">
                <strong>Currently Playing:</strong> <span id="messageText"></span>
            </div>

            <!-- Interactive User Input Panel -->
            <div class="user-input-panel" id="userInputPanel" style="display: none;">
                <h4>🎯 Customer Response Required</h4>
                <p><strong>AI Voice:</strong> "Would you like to make the payment now? Press 1 for Yes, 2 for callback."</p>
                
                <div class="input-options">
                    <button class="input-btn option-1" onclick="handleUserInput(1)">
                        <div>Press 1</div>
                        <small>Yes, I'll pay now</small>
                    </button>
                    <button class="input-btn option-2" onclick="handleUserInput(2)">
                        <div>Press 2</div>
                        <small>Request callback</small>
                    </button>
                </div>

                <div id="userResponseMessage" style="display: none;"></div>
                
                <div class="email-input-section" id="emailInputSection" style="display: none;">
                    <p><strong>📧 Enter your email to receive the payment link:</strong></p>
                    <input type="email" id="customerEmail" placeholder="Enter your email address" value="customer@example.com">
                    <button class="btn btn-success" onclick="sendPaymentLink()">
                        📤 Send Payment Link
                    </button>
                </div>
            </div>
        </div>

        <!-- Demo Customers -->
        <div class="demo-customers" id="customerCards">
            <!-- Customer cards will be populated here -->
        </div>

        <!-- Demo Controls -->
        <div class="demo-controls">
            <h3>🎮 Demo Controls</h3>
            <div class="control-group">
                <button class="btn" onclick="startSequentialDemo()">
                    🚀 Start Sequential Demo
                </button>
                <button class="btn" onclick="resetDemo()">
                    🔄 Reset Demo
                </button>
                <a href="/" class="btn" style="background: #6c757d;">
                    ← Back to Dashboard
                </a>
            </div>
        </div>
    </div>

    <!-- Audio Modal -->
    <div id="audioModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAudioModal()">&times;</span>
            <h2>🎵 Audio Demo</h2>
            <p>Playing AI-generated voice message...</p>
            <audio id="demoAudio" controls style="width: 100%; margin: 20px 0;">
                Your browser does not support the audio element.
            </audio>
        </div>
    </div>

    <script>
        // Demo data
        const demoCustomers = [
            {
                id: "CUST_001",
                name: "Manya Johri",
                phone: "+919876543210",
                emi_amount: 15000,
                due_date: "2025-08-10",
                loan_account: "LA_67890",
                risk_score: "Medium",
                preferred_language: "English"
            },
            {
                id: "CUST_002",
                name: "Demo Customer",
                phone: "+919876543210",
                emi_amount: 8500,
                due_date: "2025-08-12",
                loan_account: "LA_67891",
                risk_score: "High",
                preferred_language: "Hindi"
            }
        ];

        // Demo messages
        const demoMessages = {
            english: "Hello, this is an automated call from your loan provider. Your EMI payment of rupees 15,000 was due on August 10th. Please make the payment immediately to avoid penalties. Would you like to make the payment now? Press 1 for Yes, 2 for callback.",
            hindi: "नमस्ते, यह आपके लोन प्रदाता की ओर से एक स्वचालित कॉल है। आपकी ईएमआई 15,000 रुपये की 10 अगस्त को देय थी। कृपया जुर्माने से बचने के लिए तुरंत भुगतान करें। क्या आप अभी भुगतान करना चाहेंगे?"
        };

        // Call tracking
        let activeCalls = {};
        let audioContext = null;
        let currentAudio = null;
        let currentCallContext = null; // Track current call for user input

        // Initialize demo
        document.addEventListener('DOMContentLoaded', function() {
            renderCustomerCards();
            createAudioVisualizer();
            
            // Add keyboard event listener for user input
            document.addEventListener('keydown', function(event) {
                if (event.key === '1') {
                    handleUserInput(1);
                } else if (event.key === '2') {
                    handleUserInput(2);
                }
            });
        });

        function setupPhone() {
            const phoneNumber = document.getElementById('phoneNumber').value;
            if (!phoneNumber) {
                alert('Please enter a phone number');
                return;
            }

            // Update demo customers with the phone number
            demoCustomers.forEach(customer => {
                customer.phone = phoneNumber;
            });

            document.getElementById('setupStatus').innerHTML = '<div class="alert alert-success">✅ Demo phone number set to: ' + phoneNumber + '<br>Ready to start demo calls!</div>';

            renderCustomerCards();
        }

        function renderCustomerCards() {
            const container = document.getElementById('customerCards');
            container.innerHTML = '';

            demoCustomers.forEach(customer => {
                const card = document.createElement('div');
                card.className = 'customer-card';
                card.id = 'customer-' + customer.id;
                
                card.innerHTML = '<div class="status-indicator" id="status-' + customer.id + '"></div><div class="customer-info"><h3>' + customer.name + '</h3><div class="customer-details"><span><strong>Phone:</strong> ' + customer.phone + '</span><span><strong>EMI:</strong> ₹' + customer.emi_amount + '</span><span><strong>Due Date:</strong> ' + customer.due_date + '</span><span><strong>Risk:</strong> ' + customer.risk_score + '</span><span><strong>Language:</strong> ' + customer.preferred_language + '</span><span><strong>Account:</strong> ' + customer.loan_account + '</span></div><button class="btn" onclick="startDemoCall(\'' + customer.id + '\')">📞 Start Demo Call</button><div class="call-status" id="call-status-' + customer.id + '" style="display: none;"><div><strong>Call Progress:</strong></div><div id="call-steps-' + customer.id + '"></div></div></div>';
                
                container.appendChild(card);
            });
        }

        async function startDemoCall(customerId) {
            const customer = demoCustomers.find(c => c.id === customerId);
            if (!customer) return;

            const callId = 'call_' + Date.now();
            activeCalls[callId] = {
                customerId,
                customer,
                steps: [],
                status: 'initiating'
            };

            // Show call status
            document.getElementById('call-status-' + customerId).style.display = 'block';
            updateCustomerStatus(customerId, 'calling');

            // Demo call sequence
            await simulateDemoCall(callId, customer);
        }

        async function simulateDemoCall(callId, customer) {
            const steps = [
                { text: "📞 Dialing customer number...", delay: 2000 },
                { text: "📶 Connecting to network...", delay: 1500 },
                { text: "✅ Call connected successfully", delay: 1000 },
                { text: "🤖 Playing AI-generated voice message...", delay: 2000, action: 'playAudio' },
                { text: "👂 Waiting for customer response...", delay: 1000, action: 'waitForInput' },
                // Dynamic steps will be added based on user input
            ];

            const customerId = customer.id;
            const stepsContainer = document.getElementById('call-steps-' + customerId);
            currentCallContext = { callId, customer, customerId, stepsContainer };

            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                
                // Add step to UI
                const stepDiv = document.createElement('div');
                stepDiv.className = 'call-step current';
                stepDiv.textContent = (i + 1) + '. ' + step.text;
                stepsContainer.appendChild(stepDiv);

                // Update status
                if (step.action === 'playAudio') {
                    updateCustomerStatus(customerId, 'connected');
                    playDemoMessage(customer.preferred_language.toLowerCase());
                } else if (step.action === 'waitForInput') {
                    // Show user input panel
                    document.getElementById('userInputPanel').style.display = 'block';
                    document.getElementById('userInputPanel').scrollIntoView({ behavior: 'smooth' });
                    
                    // Wait for user input - the flow will continue from handleUserInput()
                    return; // Exit the function here, will be resumed by user input
                }

                // Remove current class from previous step
                if (i > 0) {
                    stepsContainer.children[i - 1].classList.remove('current');
                }

                await new Promise(resolve => setTimeout(resolve, step.delay));
            }
        }

        function updateCustomerStatus(customerId, status) {
            const statusIndicator = document.getElementById('status-' + customerId);
            const customerCard = document.getElementById('customer-' + customerId);
            
            statusIndicator.className = 'status-indicator ' + status;
            customerCard.className = 'customer-card ' + status;
        }

        function playDemoMessage(language) {
            const message = demoMessages[language] || demoMessages.english;
            
            // Show current message
            document.getElementById('currentMessage').style.display = 'block';
            document.getElementById('messageText').textContent = message;

            // Use Web Speech API for text-to-speech
            if ('speechSynthesis' in window) {
                // Stop any current speech
                speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(message);
                utterance.lang = language === 'hindi' ? 'hi-IN' : 'en-IN';
                utterance.rate = 0.8;
                utterance.pitch = 1;
                
                utterance.onstart = () => {
                    startAudioVisualization();
                };
                
                utterance.onend = () => {
                    stopAudioVisualization();
                    document.getElementById('currentMessage').style.display = 'none';
                };
                
                speechSynthesis.speak(utterance);
            } else {
                // Fallback: show modal with text
                document.getElementById('audioModal').style.display = 'block';
            }
        }

        function stopAudio() {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
            }
            stopAudioVisualization();
            document.getElementById('currentMessage').style.display = 'none';
        }

        async function handleUserInput(option) {
            if (!currentCallContext) {
                alert('No active call to respond to!');
                return;
            }

            const { callId, customer, customerId, stepsContainer } = currentCallContext;
            
            // Hide user input panel
            document.getElementById('userInputPanel').style.display = 'none';
            
            // Remove current class from last step
            const currentSteps = stepsContainer.querySelectorAll('.call-step');
            if (currentSteps.length > 0) {
                currentSteps[currentSteps.length - 1].classList.remove('current');
            }

            if (option === 1) {
                // Customer wants to pay now
                await continueCallWithPayment(customer, customerId, stepsContainer);
            } else if (option === 2) {
                // Customer wants callback
                await continueCallWithCallback(customer, customerId, stepsContainer);
            }
        }

        async function continueCallWithPayment(customer, customerId, stepsContainer) {
            const paymentSteps = [
                { text: "📱 Customer pressed: 1 (Will pay now)", delay: 1000 },
                { text: "🧠 AI analyzing payment request...", delay: 1500 },
                { text: "✅ Payment intent confirmed", delay: 1000 },
                { text: "📧 Requesting email for payment link...", delay: 2000, action: 'requestEmail' }
            ];

            await executeSteps(paymentSteps, stepsContainer);
        }

        async function continueCallWithCallback(customer, customerId, stepsContainer) {
            const callbackSteps = [
                { text: "📱 Customer pressed: 2 (Request callback)", delay: 1000 },
                { text: "🧠 AI processing callback request...", delay: 1500 },
                { text: "📅 Scheduling callback for preferred time", delay: 2000 },
                { text: "✅ Callback scheduled successfully", delay: 1000 },
                { text: "🔔 SMS notification sent", delay: 1000 },
                { text: "📞 Call completed - callback scheduled", delay: 1000, action: 'complete' }
            ];

            await executeSteps(callbackSteps, stepsContainer);
        }

        async function executeSteps(steps, stepsContainer) {
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                
                // Add step to UI
                const stepDiv = document.createElement('div');
                stepDiv.className = 'call-step current';
                stepDiv.textContent = (stepsContainer.children.length + 1) + '. ' + step.text;
                stepsContainer.appendChild(stepDiv);

                if (step.action === 'requestEmail') {
                    // Show email input section
                    const responseDiv = document.getElementById('userResponseMessage');
                    responseDiv.innerHTML = '<div class="response-message"><strong>AI Response:</strong> "Great! I\'ll send you a secure payment link. Please provide your email address."</div>';
                    responseDiv.style.display = 'block';
                    
                    document.getElementById('emailInputSection').style.display = 'block';
                    document.getElementById('userInputPanel').style.display = 'block';
                    document.getElementById('userInputPanel').scrollIntoView({ behavior: 'smooth' });
                    
                    return; // Wait for email input
                } else if (step.action === 'complete') {
                    updateCustomerStatus(currentCallContext.customerId, 'completed');
                    currentCallContext = null; // Clear current call
                }

                // Remove current class from previous step
                if (i > 0) {
                    stepsContainer.children[stepsContainer.children.length - 2].classList.remove('current');
                }

                await new Promise(resolve => setTimeout(resolve, step.delay));
            }

            // Mark call as completed if not already done
            if (currentCallContext) {
                delete activeCalls[currentCallContext.callId];
                currentCallContext = null;
            }
        }

        async function sendPaymentLink() {
            const email = document.getElementById('customerEmail').value;
            if (!email || !email.includes('@')) {
                alert('Please enter a valid email address');
                return;
            }

            if (!currentCallContext) {
                alert('No active call context');
                return;
            }

            const { customer, customerId, stepsContainer } = currentCallContext;

            try {
                // Show sending status
                const responseDiv = document.getElementById('userResponseMessage');
                responseDiv.innerHTML = '<div class="response-message"><strong>📧 Sending payment link to:</strong> ' + email + '<div style="margin-top: 10px;"><div style="display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div> Processing...</div></div>';

                // Call the backend API to send payment link
                const response = await fetch('/api/payment/send-link', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        session_id: 'live_demo_' + Date.now()
                    })
                });

                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }

                const result = await response.json();

                if (result.success) {
                    // Check if it's demo mode
                    const isDemoMode = result.demo_mode || false;
                    const modeText = isDemoMode ? ' (Demo Mode)' : '';
                    
                    // Update UI with success message
                    responseDiv.innerHTML = '<div class="response-message"><strong>✅ Payment Link Generated Successfully!' + modeText + '</strong><br>📧 <strong>Email:</strong> ' + email + '<br>🆔 <strong>Payment ID:</strong> ' + result.payment_id + '<br>🔗 <strong>Payment Link:</strong> <a href="' + result.payment_link + '" target="_blank" style="color: #007bff;">' + result.payment_link + '</a><br>📝 <strong>Status:</strong> ' + result.message + (isDemoMode ? '<br><br><strong>🎭 Demo Mode:</strong> Payment link generated for demonstration. Check server console for details.' : '') + '</div>';

                    // Continue with final steps
                    const finalSteps = [
                        { text: "📧 Payment link generated for " + email, delay: 1000 },
                        { text: "✅ Demo call completed successfully", delay: 1000, action: 'complete' }
                    ];

                    // Hide input sections
                    document.getElementById('emailInputSection').style.display = 'none';
                    setTimeout(() => {
                        document.getElementById('userInputPanel').style.display = 'none';
                    }, 3000);

                    await executeSteps(finalSteps, stepsContainer);

                } else {
                    // Show error message
                    responseDiv.innerHTML = '<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;"><strong>❌ Failed to send payment link</strong><br><strong>Error:</strong> ' + (result.message || result.error) + '<br><small>Please try again or contact support.</small></div>';
                }

            } catch (error) {
                console.error('Error sending payment link:', error);
                const responseDiv = document.getElementById('userResponseMessage');
                responseDiv.innerHTML = '<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;"><strong>❌ Network Error</strong><br><strong>Details:</strong> ' + error.message + '<br><small>Unable to send payment link. Please check your connection and try again.</small><br><small><strong>Debug:</strong> Check browser console for more details.</small></div>';
            }
        }

        function createAudioVisualizer() {
            const visualizer = document.getElementById('audioVisualizer');
            visualizer.innerHTML = '';
            
            for (let i = 0; i < 20; i++) {
                const bar = document.createElement('div');
                bar.className = 'audio-bar';
                bar.style.height = '5px';
                visualizer.appendChild(bar);
            }
        }

        function startAudioVisualization() {
            const bars = document.querySelectorAll('.audio-bar');
            
            const animate = () => {
                bars.forEach(bar => {
                    const height = Math.random() * 40 + 5;
                    bar.style.height = height + 'px';
                });
            };
            
            const interval = setInterval(animate, 100);
            
            // Store interval for cleanup
            window.audioVisualizationInterval = interval;
        }

        function stopAudioVisualization() {
            if (window.audioVisualizationInterval) {
                clearInterval(window.audioVisualizationInterval);
            }
            
            const bars = document.querySelectorAll('.audio-bar');
            bars.forEach(bar => {
                bar.style.height = '5px';
            });
        }

        async function startSequentialDemo() {
            for (const customer of demoCustomers) {
                await startDemoCall(customer.id);
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        function resetDemo() {
            // Reset all call statuses
            activeCalls = {};
            currentCallContext = null;
            
            demoCustomers.forEach(customer => {
                const statusDiv = document.getElementById('call-status-' + customer.id);
                if (statusDiv) {
                    statusDiv.style.display = 'none';
                    statusDiv.querySelector('#call-steps-' + customer.id).innerHTML = '';
                }
                
                updateCustomerStatus(customer.id, '');
            });
            
            // Hide user input panel
            document.getElementById('userInputPanel').style.display = 'none';
            document.getElementById('emailInputSection').style.display = 'none';
            document.getElementById('userResponseMessage').style.display = 'none';
            
            stopAudio();
            
            alert('Demo reset complete! Ready for new interactive demo.');
        }

        function closeAudioModal() {
            document.getElementById('audioModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('audioModal');
            if (event.target === modal) {
                closeAudioModal();
            }
        }
    </script>
</body>
</html>'''
    return HTMLResponse(content=html_content)


@app.get("/realtime-demo", response_class=HTMLResponse)
async def realtime_demo():
    """Serve the enhanced real-time call demo interface"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMI VoiceBot - Real-Time Call Simulator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .call-interface {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        .customer-panel, .agent-panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
        }
        .phone-display {
            background: #000;
            border-radius: 25px;
            padding: 20px;
            margin: 10px 0;
            min-height: 400px;
            position: relative;
            border: 3px solid #333;
        }
        .call-controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-call {
            background: #4CAF50;
            color: white;
        }
        .btn-call:hover {
            background: #45a049;
            transform: scale(1.05);
        }
        .btn-hangup {
            background: #f44336;
            color: white;
        }
        .btn-hangup:hover {
            background: #da190b;
            transform: scale(1.05);
        }
        .status-display {
            text-align: center;
            margin: 10px 0;
            font-weight: bold;
        }
        .conversation {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            margin: 10px 0;
        }
        .message {
            margin: 10px 0;
            padding: 8px 12px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        /* Customer panel styling */
        #customerConversation .customer-msg {
            background: #2196F3;
            margin-left: auto;
            text-align: right;
            color: white;
        }
        
        #customerConversation .agent-msg {
            background: #4CAF50;
            margin-right: auto;
            text-align: left;
            color: white;
        }
        
        /* Agent panel styling */
        #agentConversation .customer-msg {
            background: #2196F3;
            margin-right: auto;
            text-align: left;
            color: white;
        }
        
        #agentConversation .agent-msg {
            background: #4CAF50;
            margin-left: auto;
            text-align: right;
            color: white;
        }
        .typing-indicator {
            display: none;
            font-style: italic;
            color: #ccc;
        }
        .audio-controls {
            text-align: center;
            margin: 15px 0;
        }
        .audio-btn {
            background: #9C27B0;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 0 5px;
            cursor: pointer;
        }
        .metrics-panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .calling {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 EMI VoiceBot - Real-Time Call Simulator</h1>
            <p>Experience live AI-powered customer interactions with realistic call simulation</p>
        </div>

        <div class="call-interface">
            <!-- Customer Side -->
            <div class="customer-panel">
                <h3>📱 Customer: Manya Johri</h3>
                <div class="phone-display">
                    <div class="status-display" id="customerStatus">Ready to Call</div>
                    <div class="conversation" id="customerConversation"></div>
                    <div class="audio-controls">
                        <button class="audio-btn" onclick="playCustomerAudio()">🔊 Play Audio</button>
                        <button class="audio-btn" onclick="toggleMic()">🎤 Mic</button>
                    </div>
                </div>
                <div class="call-controls">
                    <button class="btn btn-call" onclick="startCall()">📞 Start Call</button>
                    <button class="btn btn-hangup" onclick="endCall()">📵 End Call</button>
                </div>
            </div>

            <!-- Agent Side -->
            <div class="agent-panel">
                <h3>🤖 AI VoiceBot Agent</h3>
                <div class="phone-display">
                    <div class="status-display" id="agentStatus">Waiting for Call</div>
                    <div class="conversation" id="agentConversation"></div>
                    <div class="audio-controls">
                        <button class="audio-btn" onclick="playAgentAudio()">🔊 Play Response</button>
                        <button class="audio-btn" onclick="toggleSpeaker()">📢 Speaker</button>
                    </div>
                </div>
                <div class="call-controls">
                    <button class="btn btn-call" onclick="simulateResponse()">🎯 Generate Response</button>
                    <button class="btn btn-hangup" onclick="escalateCall()">👥 Escalate</button>
                </div>
            </div>
        </div>

        <!-- Real-time Metrics -->
        <div class="metrics-panel">
            <h3>📊 Real-Time Call Analytics</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="callDuration">00:00</div>
                    <div>Call Duration</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="responseTime">0ms</div>
                    <div>AI Response Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="sentiment">Neutral</div>
                    <div>Customer Sentiment</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="confidence">85%</div>
                    <div>AI Confidence</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let callActive = false;
        let callStartTime = null;
        let callTimer = null;
        let ws = null;
        let messageCount = 0;

        // Real-time conversation scenarios
        const conversationScenarios = [
            {
                customer: "Hello, I received a call about my EMI payment?",
                agent: "Hello Rahul! Yes, this is a reminder that your EMI of ₹15,000 is due on August 10th. Would you like to make the payment now?",
                sentiment: "Neutral",
                confidence: "92%"
            },
            {
                customer: "I'm having some financial difficulties this month...",
                agent: "I understand your situation, Rahul. Let me check what payment options we can offer you. We have a 7-day grace period available.",
                sentiment: "Concerned",
                confidence: "88%"
            },
            {
                customer: "Can I get an extension or pay in installments?",
                agent: "Absolutely! I can offer you a 15-day extension with a small fee, or split this into 2 payments. Which would work better for you?",
                sentiment: "Hopeful",
                confidence: "95%"
            },
            {
                customer: "The extension sounds good. How much is the fee?",
                agent: "The extension fee is just ₹150. I can process this right now and send you a confirmation. Shall I go ahead?",
                sentiment: "Positive",
                confidence: "97%"
            },
            {
                customer: "Yes, please process the extension. Thank you!",
                agent: "Perfect! I've processed your 15-day extension. Your new due date is August 25th. You'll receive an SMS confirmation shortly. Is there anything else I can help you with?",
                sentiment: "Satisfied",
                confidence: "99%"
            }
        ];

        function startCall() {
            if (callActive) return;
            
            callActive = true;
            callStartTime = Date.now();
            messageCount = 0;
            
            document.getElementById('customerStatus').textContent = 'Calling...';
            document.getElementById('agentStatus').textContent = 'Incoming Call...';
            
            // Clear conversations
            document.getElementById('customerConversation').innerHTML = '';
            document.getElementById('agentConversation').innerHTML = '';
            
            // Start call timer
            callTimer = setInterval(updateCallTimer, 1000);
            
            // Simulate call connection
            setTimeout(() => {
                if (callActive) {
                    document.getElementById('customerStatus').textContent = 'Connected';
                    document.getElementById('agentStatus').textContent = 'Call Active';
                    
                    // Start conversation simulation
                    simulateConversation();
                }
            }, 2000);
            
            // Connect to WebSocket for real-time updates
            connectWebSocket();
        }

        function endCall() {
            if (!callActive) return;
            
            callActive = false;
            clearInterval(callTimer);
            
            document.getElementById('customerStatus').textContent = 'Call Ended';
            document.getElementById('agentStatus').textContent = 'Available';
            
            if (ws) {
                ws.close();
            }
        }

        function simulateConversation() {
            if (!callActive || messageCount >= conversationScenarios.length) {
                return;
            }
            
            const scenario = conversationScenarios[messageCount];
            
            // Customer message first
            setTimeout(() => {
                addMessage('customer', scenario.customer);
                updateMetrics(scenario);
            }, 1000);
            
            // Agent response with realistic delay
            setTimeout(() => {
                showTypingIndicator('agent');
                setTimeout(() => {
                    hideTypingIndicator('agent');
                    addMessage('agent', scenario.agent);
                    updateMetrics(scenario);
                    messageCount++;
                    
                    // Continue conversation
                    if (callActive && messageCount < conversationScenarios.length) {
                        setTimeout(simulateConversation, 3000);
                    }
                }, 2000 + Math.random() * 1000); // Realistic AI response time
            }, 2000);
        }

        function addMessage(sender, text) {
            if (sender === 'customer') {
                // Customer message - show on customer side as outgoing, agent side as incoming
                addMessageToSide('customerConversation', text, 'customer-msg');
                addMessageToSide('agentConversation', text, 'customer-msg');
            } else if (sender === 'agent') {
                // Agent message - show on agent side as outgoing, customer side as incoming
                addMessageToSide('agentConversation', text, 'agent-msg');
                addMessageToSide('customerConversation', text, 'agent-msg');
            }
        }

        function addMessageToSide(conversationId, text, messageClass) {
            const conversation = document.getElementById(conversationId);
            const message = document.createElement('div');
            message.className = `message ${messageClass}`;
            message.textContent = text;
            conversation.appendChild(message);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function showTypingIndicator(side) {
            const conversation = document.getElementById(side + 'Conversation');
            const indicator = document.createElement('div');
            indicator.className = 'typing-indicator';
            indicator.id = 'typing-' + side;
            indicator.textContent = 'AI is thinking...';
            indicator.style.display = 'block';
            conversation.appendChild(indicator);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function hideTypingIndicator(side) {
            const indicator = document.getElementById('typing-' + side);
            if (indicator) {
                indicator.remove();
            }
        }

        function updateCallTimer() {
            if (!callStartTime) return;
            
            const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            document.getElementById('callDuration').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        function updateMetrics(scenario) {
            document.getElementById('responseTime').textContent = (500 + Math.random() * 1000).toFixed(0) + 'ms';
            document.getElementById('sentiment').textContent = scenario.sentiment;
            document.getElementById('confidence').textContent = scenario.confidence;
        }

        function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8002/ws');
                
                ws.onopen = function() {
                    console.log('Connected to live demo WebSocket');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    console.log('Real-time update:', data);
                    // Handle real-time updates from the backend
                };
                
                ws.onerror = function(error) {
                    console.log('WebSocket error:', error);
                };
            } catch (error) {
                console.log('WebSocket connection failed:', error);
            }
        }

        // Audio simulation functions
        function playCustomerAudio() {
            // Simulate audio feedback
            alert('🔊 Playing customer audio (simulated)');
        }

        function playAgentAudio() {
            // This could integrate with the actual TTS system
            fetch('http://localhost:8002/api/demo/status')
                .then(response => response.json())
                .then(data => {
                    if (data.audio_available) {
                        alert('🔊 Playing AI-generated voice response (TTS enabled)');
                    } else {
                        alert('🔊 Audio simulation (install gTTS for real audio)');
                    }
                })
                .catch(() => {
                    alert('🔊 Audio simulation mode');
                });
        }

        function toggleMic() {
            alert('🎤 Microphone toggled (speech recognition simulation)');
        }

        function toggleSpeaker() {
            alert('📢 Speaker mode toggled');
        }

        function simulateResponse() {
            if (callActive) {
                alert('🤖 Generating AI response...');
                // This could trigger actual AI processing
            }
        }

        function escalateCall() {
            if (callActive) {
                alert('👥 Call escalated to human agent');
                endCall();
            }
        }

        // Auto-start demo on page load
        window.onload = function() {
            setTimeout(() => {
                if (confirm('🎭 Start live call demo automatically?')) {
                    startCall();
                }
            }, 1000);
        };
    </script>
</body>
</html>'''
    return HTMLResponse(content=html_content)


@app.get("/voice-demo", response_class=HTMLResponse)
async def voice_demo():
    """Serve the voice-enabled demo interface"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice-Enabled Live Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a2e;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #16213e;
            border-radius: 10px;
            padding: 30px;
        }
        .voice-controls {
            text-align: center;
            margin: 20px 0;
        }
        .voice-btn {
            background: #e94560;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            margin: 10px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .voice-btn:hover {
            background: #d63447;
            transform: scale(1.05);
        }
        .voice-btn.listening {
            background: #27ae60;
            animation: pulse 1s infinite;
        }
        .transcript {
            background: #0f3460;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            min-height: 100px;
        }
        .ai-response {
            background: #0d7377;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            min-height: 100px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Voice-Enabled Live Call Demo</h1>
        <p>Use your browser's microphone and speech synthesis for real-time interaction!</p>
        
        <div class="voice-controls">
            <button class="voice-btn" id="startBtn" onclick="startListening()">🎤 Start Speaking</button>
            <button class="voice-btn" id="stopBtn" onclick="stopListening()" disabled>⏹️ Stop</button>
            <button class="voice-btn" onclick="simulateAICall()">🤖 Simulate AI Call</button>
        </div>
        
        <div class="transcript">
            <h3>📝 What you said:</h3>
            <div id="transcript"></div>
        </div>
        
        <div class="ai-response">
            <h3>🤖 AI Agent Response:</h3>
            <div id="aiResponse"></div>
            <button class="voice-btn" onclick="speakResponse()">🔊 Play Response</button>
        </div>
    </div>

    <script>
        let recognition;
        let isListening = false;
        let isConversationMode = false;
        let silenceTimer;
        let isProcessingAI = false;
        
        // Generate unique session ID for this conversation
        const sessionId = 'voice_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            recognition = new SpeechRecognition();
        }
        
        if (recognition) {
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                let transcript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        transcript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                
                // Show live transcript
                document.getElementById('transcript').textContent = transcript + interimTranscript;
                
                // Process final results automatically in conversation mode
                if (transcript && event.results[event.results.length - 1].isFinal && isConversationMode && !isProcessingAI) {
                    clearTimeout(silenceTimer);
                    
                    // Brief pause before processing to allow for additional speech
                    silenceTimer = setTimeout(() => {
                        if (transcript.trim() && !isProcessingAI) {
                            processWithAI(transcript.trim());
                        }
                    }, 1000); // 1 second pause after final speech
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                if (event.error === 'no-speech' && isConversationMode) {
                    // Automatically restart in conversation mode
                    setTimeout(restartListening, 1000);
                } else {
                    stopListening();
                }
            };
            
            recognition.onend = function() {
                if (isConversationMode && !isProcessingAI) {
                    // Automatically restart listening in conversation mode
                    setTimeout(restartListening, 500);
                }
            };
        }
        
        function startConversation() {
            isConversationMode = true;
            startListening();
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('pauseBtn').disabled = false;
            document.getElementById('endBtn').disabled = false;
            document.getElementById('transcript').textContent = 'Conversation started - you can speak naturally...';
            document.getElementById('aiResponse').textContent = 'Hello! I\'m ready to help you with your EMI. What would you like to know?';
            
            // Welcome message
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance('Hello! I\'m ready to help you with your EMI. What would you like to know?');
                utterance.rate = 0.9;
                speechSynthesis.speak(utterance);
            }
        }
        
        function pauseConversation() {
            isConversationMode = false;
            stopListening();
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('transcript').textContent = 'Conversation paused - click "Start Conversation" to resume';
        }
        
        function endConversation() {
            isConversationMode = false;
            stopListening();
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('endBtn').disabled = true;
            document.getElementById('transcript').textContent = 'Conversation ended';
            document.getElementById('aiResponse').textContent = 'Thank you for using our EMI service. Have a great day!';
        }
        
        function startListening() {
            if (recognition && !isListening) {
                try {
                    recognition.start();
                    isListening = true;
                } catch (e) {
                    console.log('Recognition already started');
                }
            }
        }
        
        function stopListening() {
            if (recognition && isListening) {
                recognition.stop();
                isListening = false;
            }
        }
        
        function restartListening() {
            if (isConversationMode && !isProcessingAI) {
                stopListening();
                setTimeout(() => {
                    startListening();
                }, 100);
            }
        }
        
        async function processWithAI(userInput) {
            isProcessingAI = true;
            document.getElementById('aiResponse').textContent = '🤖 AI is processing your request...';
            
            // Stop listening while processing
            if (isConversationMode) {
                stopListening();
            }
            
            try {
                // Call the actual Google AI backend
                const response = await fetch('/api/voice/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_input: userInput,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Extract the AI response - it's already parsed by the backend
                    let aiText = '';
                    if (data.ai_response && data.ai_response.response) {
                        // The response is already clean text from the backend
                        aiText = data.ai_response.response;
                    } else {
                        aiText = 'I can help you with your EMI payment. How can I assist you today?';
                    }
                    
                    document.getElementById('aiResponse').textContent = aiText;
                    
                    // Auto-speak the response and then restart listening
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(aiText);
                        utterance.rate = 0.9;
                        utterance.pitch = 1;
                        utterance.volume = 0.8;
                        
                        utterance.onend = function() {
                            // Restart listening after AI finishes speaking
                            if (isConversationMode) {
                                isProcessingAI = false;
                                setTimeout(() => {
                                    document.getElementById('transcript').textContent = 'Listening for your response...';
                                    restartListening();
                                }, 1000); // 1 second pause after AI speaks
                            }
                        };
                        
                        speechSynthesis.speak(utterance);
                    } else {
                        // If no speech synthesis, restart listening immediately
                        if (isConversationMode) {
                            isProcessingAI = false;
                            setTimeout(() => {
                                document.getElementById('transcript').textContent = 'Listening for your response...';
                                restartListening();
                            }, 2000); // 2 second pause to read response
                        }
                    }
                } else {
                    // Handle error case
                    const fallbackText = data.fallback_response || 'I apologize, but I\'m having technical difficulties. Please try again.';
                    document.getElementById('aiResponse').textContent = fallbackText;
                    
                    // Restart listening after error
                    if (isConversationMode) {
                        isProcessingAI = false;
                        setTimeout(restartListening, 2000);
                    }
                }
                
            } catch (error) {
                console.error('Error calling AI API:', error);
                const fallbackText = 'I\'m sorry, I\'m having trouble connecting right now. Please try again in a moment.';
                document.getElementById('aiResponse').textContent = fallbackText;
                
                // Restart listening after error
                if (isConversationMode) {
                    isProcessingAI = false;
                    setTimeout(restartListening, 2000);
                }
            }
        }
        
        function speakResponse() {
            const text = document.getElementById('aiResponse').textContent;
            if ('speechSynthesis' in window && text) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                utterance.volume = 0.8;
                speechSynthesis.speak(utterance);
            }
        }
        
        function simulateAICall() {
            const scenarios = [
                "Hello, I received a call about my EMI payment",
                "I'm having financial difficulties this month",
                "Can I get an extension on my payment?",
                "How much is the extension fee?",
                "Please process the extension for me"
            ];
            
            const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
            document.getElementById('transcript').textContent = randomScenario;
            processWithAI(randomScenario);
        }
        
        // Check for browser support
        window.onload = function() {
            if (!recognition) {
                alert('Speech recognition not supported in this browser. Try Chrome or Edge for full voice features.');
            }
            
            if (!('speechSynthesis' in window)) {
                alert('Speech synthesis not supported in this browser.');
            }
        };
    </script>
</body>
</html>'''
    return HTMLResponse(content=html_content)


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
                    
                    if (data.status === 'success' && data.due_emis && data.due_emis.length > 0) {
                        addLog(`✅ Found ${data.due_emis.length} customers requiring calls`);
                        
                        // Display detailed EMI information
                        data.due_emis.forEach((emi, index) => {
                            setTimeout(() => {
                                addLog(`📋 Customer ${index + 1}: ${emi.name} (${emi.customer_id})`);
                                addLog(`   📞 Phone: ${emi.phone} | Amount: ₹${emi.emi_amount.toLocaleString()}`);
                                addLog(`   📅 Due: ${emi.due_date} | Overdue: ${emi.overdue_days} days | Risk: ${emi.risk_score}`);
                                addLog(`   🌐 Language: ${emi.preferred_language}`);
                                addLog('   ---');
                            }, (index + 1) * 500);
                        });
                        
                        // Update the due EMIs counter
                        setTimeout(() => {
                            document.getElementById('due-emis').textContent = data.total_found;
                        }, (data.due_emis.length + 1) * 500);
                        
                    } else {
                        addLog('ℹ️ No due EMIs found');
                    }
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
                    
                    if (data.interaction_analytics) {
                        addLog(`📈 Total Interactions: ${data.interaction_analytics.total_interactions}`);
                        addLog(`📞 Call Analytics: Success Rate ${data.call_analytics.success_rate}, Avg Duration ${data.call_analytics.average_duration}s`);
                        addLog(`💰 Payment Analytics: Total ₹${data.payment_analytics.total_collected.toLocaleString()}, Links Sent: ${data.payment_analytics.links_sent}`);
                        addLog(`🎯 Conversion Rate: ${data.interaction_analytics.conversion_rate}, Resolution Rate: ${data.interaction_analytics.resolution_rate}`);
                        
                        // Update dashboard stats
                        document.getElementById('success-rate').textContent = data.call_analytics.success_rate;
                        document.getElementById('collections').textContent = `₹${(data.payment_analytics.total_collected / 100000).toFixed(1)}L`;
                        
                        addLog('✅ Analytics dashboard updated successfully');
                    } else {
                        addLog('ℹ️ No analytics data available');
                    }
                } catch (error) {
                    addLog('❌ Analytics error: ' + error.message);
                }
            }

            async function testCall() {
                addLog('📞 Testing voice call system...');
                try {
                    const response = await fetch('/api/voice/test-call', {method: 'POST'});
                    const data = await response.json();
                    
                    if (data.test_result) {
                        addLog(`📞 Test Call ID: ${data.test_result.call_id}`);
                        addLog(`⏱️ Duration: ${data.test_result.duration}s | Status: ${data.test_result.status}`);
                        
                        if (data.test_result.components) {
                            addLog(`🤖 AI Agent: ${data.test_result.components.ai_agent}`);
                            addLog(`🗣️ Voice Engine: ${data.test_result.components.voice_engine}`);
                            addLog(`📊 Analytics: ${data.test_result.components.analytics}`);
                        }
                        
                        if (data.test_result.test_metrics) {
                            addLog(`📈 Quality Score: ${data.test_result.test_metrics.audio_quality}/10`);
                            addLog(`⚡ Response Time: ${data.test_result.test_metrics.response_time}ms`);
                            addLog(`🎯 Understanding: ${data.test_result.test_metrics.understanding_accuracy}%`);
                        }
                        
                        addLog('✅ Voice call test completed successfully');
                    } else {
                        addLog('ℹ️ Test result not available');
                    }
                } catch (error) {
                    addLog('❌ Call test error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/customers", response_class=HTMLResponse)
async def customers_page():
    """Serve customers management page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Management - EMI VoiceBot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; margin-bottom: 30px; color: #2a5298; }
            .customer-card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }
            .status-badge { padding: 4px 8px; border-radius: 12px; color: white; font-size: 12px; }
            .status-active { background: #28a745; }
            .status-overdue { background: #dc3545; }
            .status-current { background: #007bff; }
            .back-btn { background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 Customer Management</h1>
                <a href="/" class="back-btn">← Back to Dashboard</a>
            </div>
            <div id="customers"></div>
        </div>
        <script>
            async function loadCustomers() {
                try {
                    const response = await fetch('/api/customers/list');
                    const data = await response.json();
                    
                    const container = document.getElementById('customers');
                    container.innerHTML = data.customers.map(customer => `
                        <div class="customer-card">
                            <h3>${customer.name}</h3>
                            <p><strong>Phone:</strong> ${customer.phone}</p>
                            <p><strong>EMI Amount:</strong> ₹${customer.emi_amount}</p>
                            <p><strong>Last Payment:</strong> ${customer.last_payment}</p>
                            <p><strong>Risk Score:</strong> ${customer.risk_score}</p>
                            <span class="status-badge status-${customer.status}">${customer.status.toUpperCase()}</span>
                        </div>
                    `).join('');
                } catch (error) {
                    document.getElementById('customers').innerHTML = '<p>Error loading customers</p>';
                }
            }
            loadCustomers();
        </script>
    </body>
    </html>
    """


@app.get("/reports", response_class=HTMLResponse)
async def reports_page():
    """Serve reports page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reports - EMI VoiceBot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; margin-bottom: 30px; color: #2a5298; }
            .report-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
            .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
            .back-btn { background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
            .generate-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Reports & Analytics</h1>
                <a href="/" class="back-btn">← Back to Dashboard</a>
                <button class="generate-btn" onclick="generateReports()">Generate Fresh Reports</button>
            </div>
            <div id="reports"></div>
        </div>
        <script>
            async function generateReports() {
                try {
                    const response = await fetch('/api/reports/generate');
                    const data = await response.json();
                    
                    document.getElementById('reports').innerHTML = `
                        <div class="report-section">
                            <h3>💰 Collection Report</h3>
                            <div class="metric">Total Collected: ₹${data.collection_report.total_collected.toLocaleString()}</div>
                            <div class="metric">Target: ₹${data.collection_report.target.toLocaleString()}</div>
                            <div class="metric">Success Rate: ${data.collection_report.success_rate}%</div>
                            <div class="metric">Pending: ₹${data.collection_report.pending_amount.toLocaleString()}</div>
                        </div>
                        <div class="report-section">
                            <h3>📞 Call Analytics</h3>
                            <div class="metric">Total Calls: ${data.call_analytics.total_calls}</div>
                            <div class="metric">Successful: ${data.call_analytics.successful_calls}</div>
                            <div class="metric">Success Rate: ${data.call_analytics.success_rate}%</div>
                            <div class="metric">Avg Duration: ${data.call_analytics.avg_call_duration}s</div>
                        </div>
                        <div class="report-section">
                            <h3>👥 Customer Insights</h3>
                            <div class="metric">High Risk: ${data.customer_insights.high_risk_customers}</div>
                            <div class="metric">Medium Risk: ${data.customer_insights.medium_risk_customers}</div>
                            <div class="metric">Low Risk: ${data.customer_insights.low_risk_customers}</div>
                            <div class="metric">New Customers: ${data.customer_insights.new_customers}</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('reports').innerHTML = '<p>Error generating reports</p>';
                }
            }
            generateReports();
        </script>
    </body>
    </html>
    """


@app.get("/payments", response_class=HTMLResponse)
async def payments_page():
    """Serve payments management page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Management - EMI VoiceBot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; margin-bottom: 30px; color: #2a5298; }
            .payment-card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; background: #f9f9f9; }
            .status-badge { padding: 4px 8px; border-radius: 12px; color: white; font-size: 12px; margin-left: 10px; }
            .status-sent { background: #007bff; }
            .status-paid { background: #28a745; }
            .status-pending { background: #ffc107; color: #000; }
            .status-failed { background: #dc3545; }
            .back-btn { background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }
            .send-link-btn { background: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
            .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #2a5298; }
            .payment-actions { margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💳 Payment Management System</h1>
                <p>Track and manage EMI payment links and transactions</p>
            </div>
            
            <a href="/" class="back-btn">← Back to Dashboard</a>
            
            <div class="stats-grid" id="payment-stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-links">0</div>
                    <div>Total Links Sent</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="successful-payments">0</div>
                    <div>Successful Payments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="pending-payments">0</div>
                    <div>Pending Payments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="total-amount">₹0</div>
                    <div>Total Collected</div>
                </div>
            </div>
            
            <h3>📋 Recent Payment Links</h3>
            <div id="payment-links">
                <p>Loading payment data...</p>
            </div>
        </div>
        
        <script>
            async function loadPaymentData() {
                try {
                    // Load sent payment links
                    const linksResponse = await fetch('/api/payment/sent-links');
                    const linksData = await linksResponse.json();
                    
                    // Load recent payments
                    const paymentsResponse = await fetch('/api/payments/recent');
                    const paymentsData = await paymentsResponse.json();
                    
                    // Update statistics
                    document.getElementById('total-links').textContent = linksData.total_sent || 0;
                    document.getElementById('successful-payments').textContent = paymentsData.payments?.filter(p => p.status === 'paid').length || 0;
                    document.getElementById('pending-payments').textContent = paymentsData.payments?.filter(p => p.status === 'pending').length || 0;
                    
                    const totalAmount = paymentsData.payments?.filter(p => p.status === 'paid').reduce((sum, p) => sum + p.amount, 0) || 0;
                    document.getElementById('total-amount').textContent = '₹' + totalAmount.toLocaleString();
                    
                    // Display payment links
                    const linksContainer = document.getElementById('payment-links');
                    if (linksData.sent_links && linksData.sent_links.length > 0) {
                        linksContainer.innerHTML = linksData.sent_links.map(link => `
                            <div class="payment-card">
                                <div style="display: flex; justify-content: between; align-items: center;">
                                    <div>
                                        <strong>Customer:</strong> ${link.customer_name} <br>
                                        <strong>Phone:</strong> ${link.phone} <br>
                                        <strong>Amount:</strong> ₹${link.amount?.toLocaleString() || 'N/A'} <br>
                                        <strong>Sent:</strong> ${link.sent_at ? new Date(link.sent_at).toLocaleString() : 'N/A'}
                                        <span class="status-badge status-sent">Link Sent</span>
                                    </div>
                                    <div class="payment-actions">
                                        <button class="send-link-btn" onclick="resendLink('${link.payment_id}')">Resend Link</button>
                                    </div>
                                </div>
                                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                                    <strong>Payment ID:</strong> ${link.payment_id}<br>
                                    <strong>Link:</strong> <code style="background: #f1f1f1; padding: 2px 4px;">${link.payment_link || 'N/A'}</code>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        linksContainer.innerHTML = '<p>No payment links sent yet.</p>';
                    }
                    
                } catch (error) {
                    console.error('Error loading payment data:', error);
                    document.getElementById('payment-links').innerHTML = '<p>Error loading payment data</p>';
                }
            }
            
            function resendLink(paymentId) {
                alert('Resend functionality would be implemented here for payment ID: ' + paymentId);
            }
            
            // Load data when page loads
            loadPaymentData();
            
            // Refresh every 30 seconds
            setInterval(loadPaymentData, 30000);
        </script>
    </body>
    </html>
    """


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
        # Return demo data without database dependency
        demo_due_emis = [
            {
                "customer_id": "CUST001",
                "name": "Manya Johri",
                "phone": "+91-9876543210",
                "emi_amount": 15000,
                "due_date": "2025-08-10",
                "overdue_days": 5,
                "risk_score": "Medium",
                "preferred_language": "English",
            },
            {
                "customer_id": "CUST002",
                "name": "Rahul Kumar",
                "phone": "+91-9876543211",
                "emi_amount": 22000,
                "due_date": "2025-08-08",
                "overdue_days": 7,
                "risk_score": "High",
                "preferred_language": "Hindi",
            },
            {
                "customer_id": "CUST003",
                "name": "Priya Singh",
                "phone": "+91-9876543212",
                "emi_amount": 18500,
                "due_date": "2025-08-12",
                "overdue_days": 3,
                "risk_score": "Low",
                "preferred_language": "English",
            },
        ]

        # Update analytics
        analytics_data["due_emis"] = len(demo_due_emis)

        # Log the activity
        logging_agent.log_system_event(
            {
                "event_type": "due_emi_check",
                "found_due_emis": len(demo_due_emis),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "status": "success",
            "due_emis": demo_due_emis,
            "total_found": len(demo_due_emis),
        }
    except Exception as e:
        logger.error(f"Error in check_due_emis: {e}")
        return {"status": "error", "due_emis": [], "total_found": 0, "error": str(e)}


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
        import random

        # Simulate a realistic test call with random results
        test_statuses = ["successful", "completed", "connected"]
        status = random.choice(test_statuses)

        test_result = {
            "status": status,
            "message": f"Voice system test {status}",
            "call_id": f"TEST_{random.randint(1000, 9999)}",
            "duration": random.randint(30, 180),
            "components": {
                "twilio_connection": "active",
                "google_ai": "active",
                "audio_processing": "active",
                "speech_synthesis": "active",
            },
            "test_metrics": {
                "response_time": f"{random.randint(50, 200)}ms",
                "audio_quality": "excellent",
                "ai_confidence": f"{random.uniform(0.85, 0.99):.2f}",
            },
        }

        # Log the test
        logging_agent.log_system_event(
            {
                "event_type": "voice_test",
                "test_result": test_result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {"test_result": test_result}
    except Exception as e:
        logger.error(f"Error in voice test: {e}")
        return {
            "test_result": {
                "status": "failed",
                "message": f"Voice test failed: {str(e)}",
                "error": str(e),
            }
        }


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    try:
        # Get analytics from logging agent
        base_analytics = logging_agent.get_learning_insights()

        # Structure the response to match frontend expectations
        analytics = {
            "interaction_analytics": {
                "total_interactions": 287,
                "success_rate": 0.854,
                "avg_resolution_time": 145.5,
                "peak_hours": ["10:00-11:00", "14:00-15:00"],
                "customer_satisfaction": 0.78,
            },
            "call_analytics": {
                "total_calls": 287,
                "successful_calls": 245,
                "success_rate": 0.854,
                "avg_call_duration": 125.3,
                "callback_success_rate": 0.82,
            },
            "payment_analytics": {
                "total_payments": 198,
                "successful_payments": 185,
                "payment_success_rate": 0.934,
                "avg_payment_amount": 16750,
                "total_collected": 3098750,
            },
            "customer_insights": base_analytics.get("insights", {}),
            "recommendations": base_analytics.get("recommendations", []),
            "real_time": {
                "active_calls": 3,
                "queue_size": 12,
                "avg_call_duration": "4m 32s",
                "current_success_rate": 0.78,
            },
        }

        return analytics
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {e}")
        # Return fallback data if there's an error
        return {
            "interaction_analytics": {
                "total_interactions": 0,
                "success_rate": 0.0,
                "avg_resolution_time": 0.0,
                "peak_hours": [],
                "customer_satisfaction": 0.0,
            },
            "call_analytics": {
                "total_calls": 0,
                "successful_calls": 0,
                "success_rate": 0.0,
                "avg_call_duration": 0.0,
                "callback_success_rate": 0.0,
            },
            "real_time": {
                "active_calls": 0,
                "queue_size": 0,
                "avg_call_duration": "0m 0s",
                "current_success_rate": 0.0,
            },
            "error": str(e),
        }


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


@app.get("/api/customers/list")
async def get_customers():
    """Get list of all customers"""
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Manya Johri",
            "phone": "+91-9876543210",
            "email": "manya.johri@example.com",
            "loan_amount": 500000,
            "emi_amount": 15000,
            "remaining_emis": 28,
            "last_payment": "2025-07-10",
            "risk_score": "Medium",
            "preferred_language": "English",
            "status": "active",
        },
        {
            "customer_id": "CUST002",
            "name": "Rahul Kumar",
            "phone": "+91-9876543211",
            "email": "rahul.kumar@example.com",
            "loan_amount": 750000,
            "emi_amount": 22000,
            "remaining_emis": 31,
            "last_payment": "2025-07-08",
            "risk_score": "High",
            "preferred_language": "Hindi",
            "status": "overdue",
        },
        {
            "customer_id": "CUST003",
            "name": "Priya Singh",
            "phone": "+91-9876543212",
            "email": "priya.singh@example.com",
            "loan_amount": 600000,
            "emi_amount": 18500,
            "remaining_emis": 25,
            "last_payment": "2025-07-12",
            "risk_score": "Low",
            "preferred_language": "English",
            "status": "current",
        },
        {
            "customer_id": "CUST004",
            "name": "Amit Sharma",
            "phone": "+91-9876543213",
            "email": "amit.sharma@example.com",
            "loan_amount": 400000,
            "emi_amount": 12500,
            "remaining_emis": 20,
            "last_payment": "2025-08-05",
            "risk_score": "Low",
            "preferred_language": "Hindi",
            "status": "current",
        },
    ]

    return {
        "customers": customers,
        "total_count": len(customers),
        "active_count": sum(
            1 for c in customers if c["status"] in ["active", "current"]
        ),
        "overdue_count": sum(1 for c in customers if c["status"] == "overdue"),
    }


@app.get("/api/reports/generate")
async def generate_reports():
    """Generate various reports"""
    return {
        "collection_report": {
            "total_collected": 2850000,
            "target": 3000000,
            "success_rate": 95.0,
            "pending_amount": 150000,
        },
        "call_analytics": {
            "total_calls": 287,
            "successful_calls": 245,
            "success_rate": 85.4,
            "avg_call_duration": 125,
        },
        "customer_insights": {
            "high_risk_customers": 12,
            "medium_risk_customers": 45,
            "low_risk_customers": 78,
            "new_customers": 23,
        },
    }


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
