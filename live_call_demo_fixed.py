#!/usr/bin/env python3
"""
Live Call Demo System with Audio Integration (Simplified)
Enhanced demo for stakeholder presentations
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
import tempfile
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from threading import Thread
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveCallDemoSystem:
    def __init__(self):
        # Demo phone number
        self.demo_phone_number = None

        # Demo data
        self.demo_customers = [
            {
                "id": "CUST_001",
                "name": "Manya Johri",
                "phone": "+91XXXXXXXXXX",
                "emi_amount": 15000,
                "due_date": "2025-08-10",
                "loan_account": "LA_67890",
                "risk_score": "Medium",
                "preferred_language": "English",
            },
            {
                "id": "CUST_002",
                "name": "Demo Customer",
                "phone": "+91XXXXXXXXXX",
                "emi_amount": 8500,
                "due_date": "2025-08-12",
                "loan_account": "LA_67891",
                "risk_score": "High",
                "preferred_language": "Hindi",
            },
        ]

        # Call status tracking
        self.active_calls = {}
        self.call_history = []

        # WebSocket connections for real-time updates
        self.websocket_connections = []

    async def setup_demo_phone_number(self, phone_number: str):
        """Set up your personal phone number for the demo"""
        self.demo_phone_number = phone_number
        # Update demo customers with your number
        for customer in self.demo_customers:
            customer["phone"] = phone_number
        logger.info(f"Demo phone number set to: {phone_number}")

    def generate_ai_voice_message(
        self, customer_data: Dict, language: str = "en"
    ) -> str:
        """Generate AI voice message for the customer"""
        messages = {
            "en": f"""Hello {customer_data['name']}, this is an automated call from your loan provider. 
                     Your EMI payment of ₹{customer_data['emi_amount']} was due on {customer_data['due_date']}. 
                     Please make the payment immediately to avoid penalties. 
                     Would you like to make the payment now? Press 1 for Yes, 2 for callback.""",
            "hi": f"""नमस्ते {customer_data['name']}, यह आपके लोन प्रदाता की ओर से एक स्वचालित कॉल है। 
                     आपकी ईएमआई ₹{customer_data['emi_amount']} की {customer_data['due_date']} को देय थी। 
                     कृपया जुर्माने से बचने के लिए तुरंत भुगतान करें। 
                     क्या आप अभी भुगतान करना चाहेंगे? हाँ के लिए 1, कॉलबैक के लिए 2 दबाएं।""",
        }

        return messages.get(language.lower()[:2], messages["en"])

    async def initiate_live_call(
        self, customer_id: str, demo_mode: bool = True
    ) -> Dict:
        """Initiate a live call to demonstrate the system"""
        customer = next(
            (c for c in self.demo_customers if c["id"] == customer_id), None
        )
        if not customer:
            return {"error": "Customer not found"}

        call_id = f"call_{int(time.time())}"

        # Demo mode - simulate call with visual feedback
        return await self.simulate_demo_call(customer, call_id)

    async def simulate_demo_call(self, customer: Dict, call_id: str) -> Dict:
        """Simulate a demo call with visual feedback"""
        logger.info(f"Starting demo call for {customer['name']}")

        # Update call status
        call_data = {
            "call_id": call_id,
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "status": "initiating",
            "start_time": datetime.now().isoformat(),
            "steps": [],
        }

        self.active_calls[call_id] = call_data
        await self.broadcast_call_update(call_data)

        # Step 1: Dialing
        call_data["status"] = "dialing"
        call_data["steps"].append("📞 Dialing customer number...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        # Step 2: Connected
        call_data["status"] = "connected"
        call_data["steps"].append("✅ Call connected successfully")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(1)

        # Step 3: AI Voice Message
        call_data["steps"].append("🤖 Playing AI-generated voice message...")
        await self.broadcast_call_update(call_data)

        # Generate message
        language = "en" if customer["preferred_language"] == "English" else "hi"
        message = self.generate_ai_voice_message(customer, language)

        call_data["steps"].append(f"🔊 Playing: '{message[:50]}...'")
        await self.broadcast_call_update(call_data)

        # Simulate playback time
        await asyncio.sleep(8)

        # Step 4: Customer Response Simulation
        call_data["steps"].append("👂 Listening for customer response...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(3)

        # Simulate customer response
        call_data["steps"].append("📱 Customer pressed: 1 (Will pay now)")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        # Step 5: AI Decision Making
        call_data["steps"].append("🧠 AI analyzing response and making decision...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        # Step 6: Action Execution
        call_data["steps"].append("💳 Generating secure payment link...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        payment_link = f"https://pay.example.com/emi/{customer['id']}/{call_id}"
        call_data["steps"].append(f"📲 SMS sent with payment link: {payment_link}")
        await self.broadcast_call_update(call_data)

        # Step 7: Call Completion
        call_data["status"] = "completed"
        call_data["end_time"] = datetime.now().isoformat()
        call_data["steps"].append("✅ Call completed successfully")
        call_data["outcome"] = {
            "result": "Payment commitment received",
            "payment_link_sent": True,
            "next_action": "Monitor payment within 24 hours",
        }

        await self.broadcast_call_update(call_data)

        # Move to call history
        self.call_history.append(call_data)
        del self.active_calls[call_id]

        return call_data

    async def broadcast_call_update(self, call_data: Dict):
        """Broadcast call updates to all connected WebSocket clients"""
        message = {
            "type": "call_update",
            "data": call_data,
            "timestamp": datetime.now().isoformat(),
        }

        # Remove disconnected connections
        active_connections = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(json.dumps(message))
                active_connections.append(websocket)
            except:
                pass  # Connection closed

        self.websocket_connections = active_connections

    def get_demo_status(self) -> Dict:
        """Get current demo status"""
        return {
            "active_calls": len(self.active_calls),
            "completed_calls": len(self.call_history),
            "demo_customers": self.demo_customers,
            "phone_number_set": self.demo_phone_number is not None,
        }


# FastAPI app for WebSocket connections
app = FastAPI(title="Live Call Demo System")
demo_system = LiveCallDemoSystem()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    demo_system.websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        if websocket in demo_system.websocket_connections:
            demo_system.websocket_connections.remove(websocket)


@app.post("/api/demo/setup-phone")
async def setup_phone(phone_data: dict):
    """Setup phone number for demo"""
    phone_number = phone_data.get("phone_number")
    if phone_number:
        await demo_system.setup_demo_phone_number(phone_number)
        return {"status": "success", "phone_number": phone_number}
    else:
        return {"status": "error", "message": "Phone number required"}


@app.post("/api/demo/start-call/{customer_id}")
async def start_demo_call(customer_id: str, call_type: str = "demo"):
    """Start a demo call"""
    result = await demo_system.initiate_live_call(customer_id, True)
    return result


@app.get("/api/demo/status")
async def get_demo_status():
    """Get demo system status"""
    return demo_system.get_demo_status()


@app.get("/api/demo/customers")
async def get_demo_customers():
    """Get demo customers list"""
    return {"customers": demo_system.demo_customers}


if __name__ == "__main__":
    print("🎭 Starting Live Call Demo System...")
    print("📞 WebSocket endpoint: ws://localhost:8002/ws")
    print("🔗 API endpoint: http://localhost:8002")
    print("")
    print("🎯 Setup Instructions:")
    print("1. Set your phone number: POST /api/demo/setup-phone")
    print("2. Start demo call: POST /api/demo/start-call/CUST_001")
    print("3. Watch real-time updates via WebSocket")

    uvicorn.run(app, host="0.0.0.0", port=8002)
