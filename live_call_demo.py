#!/usr/bin/env python3
"""
Live Call Demo System with Real Audio Integration

This module provides a comprehensive live call demonstration system with real-time audio,
WebSocket updates, and optional Twilio integration for actual phone calls.

Optional Dependencies (install via requirements-audio-demo.txt):
- gtts: Text-to-speech audio generation
- pygame: Audio playback capabilities
- speech_recognition: Speech-to-text conversion
- twilio: Real phone call functionality

The system gracefully handles missing optional dependencies and provides fallback functionality.
Import warnings for optional packages are expected and can be safely ignored.

Enhanced demo for stakeholder presentations with actual voice calls
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Optional imports - gracefully handle missing dependencies
TWILIO_AVAILABLE = False
PYGAME_AVAILABLE = False
GTTS_AVAILABLE = False
SR_AVAILABLE = False

try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.voice_response import VoiceResponse as TwilioVoiceResponse

    TWILIO_AVAILABLE = True
except ImportError:
    TwilioClient = None
    TwilioVoiceResponse = None

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    gTTS = None

try:
    import speech_recognition as sr

    SR_AVAILABLE = True
except ImportError:
    sr = None

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
        # Twilio configuration (you'll need to set these)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

        # Your personal number for demo
        self.demo_phone_number = None  # Will be set during demo

        # Initialize Twilio client
        if TWILIO_AVAILABLE and TwilioClient:
            try:
                self.twilio_client = TwilioClient(
                    self.twilio_account_sid, self.twilio_auth_token
                )
            except Exception as e:
                logger.warning(f"Twilio not configured: {e}")
                self.twilio_client = None
        else:
            logger.warning("Twilio not available")
            self.twilio_client = None
            self.twilio_client = None

        # Initialize audio system
        if PYGAME_AVAILABLE and pygame:
            try:
                pygame.mixer.init()
            except Exception as e:
                logger.warning(f"Audio system not available: {e}")
        else:
            logger.warning("Pygame not available")  # Demo data
        self.demo_customers = [
            {
                "id": "CUST_001",
                "name": "Manya Johri",
                "phone": "+91XXXXXXXXXX",  # Will use your number
                "emi_amount": 15000,
                "due_date": "2025-08-10",
                "loan_account": "LA_67890",
                "risk_score": "Medium",
                "preferred_language": "English",
            },
            {
                "id": "CUST_002",
                "name": "Demo Customer",
                "phone": "+91XXXXXXXXXX",  # Will use your number
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

    def create_audio_file(self, text: str, language: str = "en") -> Optional[str]:
        """Create audio file from text using TTS"""
        if not GTTS_AVAILABLE or not gTTS:
            logger.warning("gTTS not available")
            return None

        try:
            tts = gTTS(text=text, lang=language, slow=False)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            return temp_file.name
        except Exception as e:
            logger.error(f"Error creating audio file: {e}")
            return None

    def play_audio_file(self, audio_file: str):
        """Play audio file locally for demo"""
        if not PYGAME_AVAILABLE or not pygame:
            logger.warning("Audio playback not available")
            return

        try:
            if audio_file and os.path.exists(audio_file):
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                # Clean up
                os.unlink(audio_file)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

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

        if demo_mode:
            # Demo mode - simulate call with audio playback
            return await self.simulate_demo_call(customer, call_id)
        else:
            # Real call mode using Twilio
            return await self.make_real_call(customer, call_id)

    async def simulate_demo_call(self, customer: Dict, call_id: str) -> Dict:
        """Simulate a demo call with audio feedback"""
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

        # Generate and play audio message
        language = "en" if customer["preferred_language"] == "English" else "hi"
        message = self.generate_ai_voice_message(customer, language)

        # Create audio file and play it
        audio_file = self.create_audio_file(message, language)
        if audio_file:
            call_data["steps"].append(f"🔊 Playing: '{message[:50]}...'")
            await self.broadcast_call_update(call_data)

            # Play audio in a separate thread to not block
            audio_thread = Thread(target=self.play_audio_file, args=(audio_file,))
            audio_thread.start()

            # Simulate playback time
            await asyncio.sleep(8)

        # Step 4: Customer Response Simulation
        call_data["steps"].append("👂 Listening for customer response...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(3)

        # Simulate different customer responses
        responses = [
            {"dtmf": "1", "meaning": "Will pay now", "action": "generate_payment_link"},
            {"dtmf": "2", "meaning": "Request callback", "action": "schedule_callback"},
            {
                "voice": "I'll pay tomorrow",
                "meaning": "Promise to pay",
                "action": "schedule_followup",
            },
        ]

        simulated_response = responses[0]  # Default to payment
        call_data["steps"].append(
            f"📱 Customer pressed: {simulated_response['dtmf']} ({simulated_response['meaning']})"
        )
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        # Step 5: AI Decision Making
        call_data["steps"].append("🧠 AI analyzing response and making decision...")
        await self.broadcast_call_update(call_data)
        await asyncio.sleep(2)

        # Step 6: Action Execution
        if simulated_response["action"] == "generate_payment_link":
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

    async def make_real_call(self, customer: Dict, call_id: str) -> Dict:
        """Make a real call using Twilio (requires setup)"""
        if not TWILIO_AVAILABLE or not self.twilio_client:
            return {"error": "Twilio not configured"}

        try:
            # Create TwiML for the call
            if not TWILIO_AVAILABLE or not TwilioVoiceResponse:
                return {"error": "Twilio not available"}

            twiml = TwilioVoiceResponse()
            message = self.generate_ai_voice_message(customer)
            twiml.say(message, voice="alice", language="en-IN")

            # Add gather for DTMF input
            gather = twiml.gather(
                input="dtmf speech", timeout=10, num_digits=1, action="/handle-response"
            )
            gather.say("Press 1 to pay now, or 2 for a callback.")

            # Make the call
            call = self.twilio_client.calls.create(
                twiml=str(twiml), to=customer["phone"], from_=self.twilio_phone_number
            )

            call_data = {
                "call_id": call_id,
                "twilio_call_sid": call.sid,
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "status": "initiated",
                "start_time": datetime.now().isoformat(),
            }

            self.active_calls[call_id] = call_data
            return call_data

        except Exception as e:
            logger.error(f"Error making real call: {e}")
            return {"error": str(e)}

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
        audio_status = False
        if PYGAME_AVAILABLE:
            try:
                import pygame as pg

                audio_status = pg.mixer.get_init() is not None
            except:
                audio_status = False

        return {
            "active_calls": len(self.active_calls),
            "completed_calls": len(self.call_history),
            "demo_customers": self.demo_customers,
            "twilio_configured": self.twilio_client is not None,
            "audio_available": audio_status,
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
        demo_system.websocket_connections.remove(websocket)


@app.post("/api/demo/setup-phone")
async def setup_phone(phone_data: dict):
    """Setup phone number for demo"""
    phone_number = phone_data.get("phone_number")
    if not phone_number:
        return {"error": "Phone number is required"}

    await demo_system.setup_demo_phone_number(str(phone_number))
    return {"status": "success", "phone_number": phone_number}


@app.post("/api/demo/start-call/{customer_id}")
async def start_demo_call(customer_id: str, call_type: str = "demo"):
    """Start a demo call"""
    demo_mode = call_type == "demo"
    result = await demo_system.initiate_live_call(customer_id, demo_mode)
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
    print("")
    print("🔧 Optional Twilio Setup (for real calls):")
    print("   export TWILIO_ACCOUNT_SID='your_sid'")
    print("   export TWILIO_AUTH_TOKEN='your_token'")
    print("   export TWILIO_PHONE_NUMBER='your_twilio_number'")

    uvicorn.run(app, host="0.0.0.0", port=8002)
