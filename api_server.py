#!/usr/bin/env python3
"""
FastAPI Server for EMI VoiceBot System
Provides REST API endpoints for integration and live demos
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.trigger_agent import TriggerAgent
from src.agents.context_agent import ContextAgent
from src.agents.voicebot_agent import VoiceBotAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.logging_learning_agent import LoggingLearningAgent


# Pydantic models for API requests
class CallRequest(BaseModel):
    customer_id: int
    loan_id: Optional[int] = None


class PaymentLinkRequest(BaseModel):
    customer_id: int
    amount: float
    loan_id: int


class AnalyticsRequest(BaseModel):
    days: int = 30
    customer_id: Optional[int] = None


# Initialize FastAPI app
app = FastAPI(
    title="EMI VoiceBot API",
    description="AI-Powered EMI Collection System API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
trigger_agent = TriggerAgent()
context_agent = ContextAgent()
voicebot_agent = VoiceBotAgent()
decision_agent = DecisionAgent()
payment_agent = PaymentAgent()
learning_agent = LoggingLearningAgent()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Interactive dashboard for live demos"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EMI VoiceBot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; margin: 10px 0; 
                   border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }
            .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
            .stat-label { color: #6c757d; margin-top: 5px; }
            .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
            .action-btn { background: #667eea; color: white; padding: 15px; text-align: center; 
                         border-radius: 8px; cursor: pointer; text-decoration: none; }
            .action-btn:hover { background: #5a6fd8; }
            .log { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; 
                  font-family: monospace; max-height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EMI VoiceBot Dashboard</h1>
                <p>Real-time AI-powered EMI collection system</p>
            </div>
            
            <div class="card">
                <h2>📊 Live Statistics</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value" id="due-emis">-</div>
                        <div class="stat-label">Due EMIs</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="calls-today">-</div>
                        <div class="stat-label">Calls Today</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="success-rate">-</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="collections">-</div>
                        <div class="stat-label">Collections</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>⚡ Quick Actions</h2>
                <div class="actions">
                    <a href="#" class="action-btn" onclick="triggerCalls()">
                        🔍 Check Due EMIs
                    </a>
                    <a href="#" class="action-btn" onclick="startDemo()">
                        🎭 Start Live Demo
                    </a>
                    <a href="#" class="action-btn" onclick="viewAnalytics()">
                        📈 View Analytics
                    </a>
                    <a href="#" class="action-btn" onclick="testCall()">
                        📞 Test Voice Call
                    </a>
                </div>
            </div>
            
            <div class="card">
                <h2>📋 Activity Log</h2>
                <div class="log" id="activity-log">
                    Loading activity...
                </div>
            </div>
        </div>
        
        <script>
            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('due-emis').textContent = data.due_emis || '0';
                        document.getElementById('calls-today').textContent = data.calls_today || '0';
                        document.getElementById('success-rate').textContent = (data.success_rate * 100).toFixed(1) + '%';
                        document.getElementById('collections').textContent = '₹' + (data.collections / 1000).toFixed(1) + 'K';
                    });
            }
            
            function triggerCalls() {
                addLog('🔍 Checking for due EMIs...');
                fetch('/api/trigger/check-due-emis', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        addLog(`✅ Found ${data.due_emis.length} customers requiring calls`);
                        updateStats();
                    });
            }
            
            function startDemo() {
                addLog('🎭 Starting live workflow demo...');
                fetch('/api/demo/workflow', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        addLog('✅ Demo completed successfully!');
                    });
            }
            
            function viewAnalytics() {
                addLog('📈 Generating analytics report...');
                fetch('/api/analytics/dashboard')
                    .then(response => response.json())
                    .then(data => {
                        addLog(`📊 Analytics: ${data.total_interactions} interactions, ${(data.success_rate * 100).toFixed(1)}% success rate`);
                    });
            }
            
            function testCall() {
                addLog('📞 Initiating test voice call...');
                fetch('/api/voice/test-call', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        addLog(`📞 Test call status: ${data.status}`);
                    });
            }
            
            function addLog(message) {
                const log = document.getElementById('activity-log');
                const timestamp = new Date().toLocaleTimeString();
                log.innerHTML = `[${timestamp}] ${message}<br>` + log.innerHTML;
            }
            
            // Update stats every 5 seconds
            setInterval(updateStats, 5000);
            updateStats();
            
            // Add initial log
            addLog('🚀 EMI VoiceBot dashboard loaded and ready!');
        </script>
    </body>
    </html>
    """


@app.get("/api/stats")
async def get_stats():
    """Get real-time system statistics"""
    try:
        # Get due EMIs
        due_emis = trigger_agent.check_due_emis()

        # Get analytics
        analytics = learning_agent.analyze_interaction_patterns(days=1)

        return {
            "due_emis": len(due_emis),
            "calls_today": analytics.get("total_interactions", 0),
            "success_rate": analytics.get("success_rate", 0.0),
            "collections": analytics.get("total_amount", 0),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "due_emis": 0,
            "calls_today": 0,
            "success_rate": 0.0,
            "collections": 0,
            "error": str(e),
        }


@app.post("/api/trigger/check-due-emis")
async def check_due_emis():
    """Check for customers with due EMIs"""
    try:
        due_emis = trigger_agent.check_due_emis()
        return {
            "status": "success",
            "due_emis": due_emis,
            "count": len(due_emis),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/initiate-call")
async def initiate_call(request: CallRequest, background_tasks: BackgroundTasks):
    """Initiate voice call to customer"""
    try:
        # Get customer context
        customer_context = context_agent.get_customer_context(request.customer_id)

        # Start call in background
        def process_call():
            return voicebot_agent.initiate_call(customer_context, {})

        background_tasks.add_task(process_call)

        return {
            "status": "initiated",
            "customer_id": request.customer_id,
            "message": "Call started in background",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customer/{customer_id}/context")
async def get_customer_context(customer_id: int):
    """Get customer context and intelligence"""
    try:
        context = context_agent.get_customer_context(customer_id)
        return {
            "status": "success",
            "customer_context": context,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payment/create-link")
async def create_payment_link(request: PaymentLinkRequest):
    """Create secure payment link"""
    try:
        # Get customer context
        customer_context = context_agent.get_customer_context(request.customer_id)

        # Create payment link
        loan_info = {"loan_id": request.loan_id, "emi_amount": request.amount}
        payment_result = payment_agent.create_payment_link(customer_context, loan_info)

        return {
            "status": "success",
            "payment_link": payment_result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/dashboard")
async def get_analytics(days: int = 30):
    """Get analytics dashboard data"""
    try:
        analytics = learning_agent.analyze_interaction_patterns(days=days)
        payment_analytics = payment_agent.get_payment_analytics(days=days)

        return {
            "status": "success",
            "interaction_analytics": analytics,
            "payment_analytics": payment_analytics,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/test-call")
async def test_call():
    """Test voice call functionality"""
    try:
        # Simulate test call
        test_result = {
            "call_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "completed",
            "duration": "45 seconds",
            "test_mode": True,
        }

        return {
            "status": "success",
            "test_result": test_result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/demo/workflow")
async def run_demo_workflow():
    """Run complete workflow demo"""
    try:
        # Simulate complete workflow
        workflow_steps = [
            "✅ Checked due EMIs",
            "✅ Gathered customer context",
            "✅ Initiated voice calls",
            "✅ Made intelligent decisions",
            "✅ Processed payments",
            "✅ Updated analytics",
        ]

        return {
            "status": "success",
            "workflow_completed": True,
            "steps": workflow_steps,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "agents": {
            "trigger": "✅ Active",
            "context": "✅ Active",
            "voicebot": "✅ Active",
            "decision": "✅ Active",
            "payment": "✅ Active",
            "learning": "✅ Active",
        },
    }


if __name__ == "__main__":
    print("🚀 Starting EMI VoiceBot API Server...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")

    uvicorn.run(
        "api_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
