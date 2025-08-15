from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
from datetime import datetime
import random

app = FastAPI(title="EMI VoiceBot - Advanced UI Server", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        <p><a href="/simple">Use Simple Dashboard</a></p>
        """
        )


@app.get("/simple", response_class=HTMLResponse)
async def simple_dashboard():
    """Serve the original simple dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EMI VoiceBot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
            .stat { text-align: center; padding: 25px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; color: #667eea; font-size: 2.5rem; }
            .stat p { margin: 5px 0 0 0; color: #666; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
            .actions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }
            .btn { padding: 15px 20px; border: none; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; cursor: pointer; font-size: 1rem; transition: all 0.3s; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
            .activity { background: #1a1a1a; color: #00ff00; padding: 20px; border-radius: 10px; font-family: monospace; max-height: 300px; overflow-y: auto; }
            .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .nav-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; transition: all 0.3s; }
            .nav-link:hover { background: #5a67d8; transform: translateY(-1px); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EMI VoiceBot - AI Collection System</h1>
                <p>Professional dashboard for stakeholder presentations</p>
            </div>
            
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

            <a href="/" class="nav-link">Switch to Advanced Dashboard</a>
        </div>

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
                    updateStats();
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
                        setTimeout(() => addLog(`[DEMO] ${step}`), index * 1500);
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
                    addLog(`📈 Analytics ready: ${data.interaction_analytics?.total_interactions || 150} interactions`);
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

            async function updateStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    document.getElementById('calls-today').textContent = data.calls_today || 247;
                    document.getElementById('success-rate').textContent = Math.round((data.success_rate || 0.73) * 100) + '%';
                    document.getElementById('due-emis').textContent = data.due_emis || 156;
                    document.getElementById('collections').textContent = '₹' + ((data.collections || 2450000) / 100000).toFixed(1) + 'L';
                } catch (error) {
                    console.error('Error updating stats:', error);
                }
            }

            // Auto-update stats every 30 seconds
            setInterval(updateStats, 30000);
            
            // Add demo activity
            setInterval(() => {
                const activities = [
                    '📞 Call completed successfully',
                    '💳 Payment link generated', 
                    '📊 Customer risk score updated',
                    '🤖 AI model learning from interaction',
                    '📈 Analytics refreshed'
                ];
                const randomActivity = activities[Math.floor(Math.random() * activities.length)];
                addLog(randomActivity);
            }, 8000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    # Simulate some variance in stats
    analytics_data["calls_today"] += random.randint(0, 2)
    analytics_data["success_rate"] = min(
        1.0, analytics_data["success_rate"] + random.uniform(-0.02, 0.02)
    )
    analytics_data["collections"] += random.randint(0, 50000)

    return {
        "calls_today": analytics_data["calls_today"],
        "success_rate": analytics_data["success_rate"],
        "due_emis": analytics_data["due_emis"],
        "collections": analytics_data["collections"],
        "last_updated": datetime.now().isoformat(),
    }


@app.post("/api/trigger/check-due-emis")
async def check_due_emis():
    """Trigger due EMI checking"""
    # Simulate finding due EMIs
    due_emis = [
        {
            "customer_id": f"CUST_{1000 + i}",
            "customer_name": f"Customer {i+1}",
            "loan_info": {"emi_amount": random.randint(5000, 25000)},
            "priority": random.choice(["high", "medium", "low"]),
        }
        for i in range(random.randint(50, 200))
    ]

    analytics_data["due_emis"] = len(due_emis)

    return {
        "status": "success",
        "due_emis": due_emis,
        "total_found": len(due_emis),
        "timestamp": datetime.now().isoformat(),
    }


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

    return {
        "status": "demo_started",
        "steps": steps,
        "estimated_duration": "13 seconds",
    }


@app.post("/api/voice/test-call")
async def test_voice_call():
    """Test voice call functionality"""
    test_results = [
        {"status": "successful", "message": "Voice system operational"},
        {"status": "successful", "message": "Test call completed"},
        {"status": "successful", "message": "AI responses working"},
        {"status": "successful", "message": "Call quality excellent"},
    ]

    result = random.choice(test_results)

    return {"test_result": result, "timestamp": datetime.now().isoformat()}


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    analytics = {
        "interaction_analytics": {
            "total_interactions": random.randint(1200, 1500),
            "success_rate": analytics_data["success_rate"],
            "avg_call_duration": "4m 32s",
            "customer_satisfaction": 0.86,
        },
        "real_time": {
            "active_calls": random.randint(1, 5),
            "queue_size": random.randint(5, 20),
            "avg_call_duration": "4m 32s",
            "current_success_rate": analytics_data["success_rate"],
        },
        "daily_stats": {
            "calls_completed": analytics_data["calls_today"],
            "payments_received": random.randint(80, 120),
            "collection_amount": analytics_data["collections"],
        },
    }

    return analytics


@app.get("/api/calls/live")
async def get_live_calls():
    """Get currently active calls"""
    names = [
        "Rajesh Kumar",
        "Priya Sharma",
        "Arun Patel",
        "Sneha Gupta",
        "Vikram Singh",
    ]
    statuses = ["connected", "calling", "completed"]

    live_calls = [
        {
            "call_id": f"call_{str(i).zfill(3)}",
            "customer_id": f"CUST_{12345 + i}",
            "customer_name": random.choice(names),
            "status": random.choice(statuses),
            "duration": f"{random.randint(1, 8)}m {random.randint(10, 59)}s",
            "emi_amount": random.randint(5000, 25000),
            "loan_account": f"LA_{67890 + i}",
        }
        for i in range(random.randint(2, 6))
    ]

    return {"live_calls": live_calls, "total_active": len(live_calls)}


@app.get("/api/payments/recent")
async def get_recent_payments():
    """Get recent payment transactions"""
    names = ["Arun Patel", "Sneha Gupta", "Rajesh Kumar", "Priya Sharma"]
    methods = ["UPI", "Net Banking", "Credit Card", "Debit Card"]
    statuses = ["completed", "pending", "processing"]

    recent_payments = [
        {
            "payment_id": f"PAY_{str(i).zfill(3)}",
            "customer_name": random.choice(names),
            "amount": random.randint(5000, 25000),
            "status": random.choice(statuses),
            "timestamp": datetime.now().isoformat(),
            "method": random.choice(methods),
        }
        for i in range(random.randint(3, 8))
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
    print("")
    print("🎯 For presentations:")
    print("   • Use Advanced Dashboard for professional look")
    print("   • Use Simple Dashboard as fallback")
    print("   • Both include live demo capabilities")

    uvicorn.run(app, host="0.0.0.0", port=8001)
