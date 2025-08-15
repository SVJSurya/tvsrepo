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
