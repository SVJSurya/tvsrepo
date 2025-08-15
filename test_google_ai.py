#!/usr/bin/env python3
"""
Test script for Google Gemini AI integration
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.google_voicebot_agent import GoogleVoiceBotAgent


def test_google_ai():
    print("🤖 Testing Google Gemini AI Integration...")

    # Initialize the Google VoiceBot agent
    agent = GoogleVoiceBotAgent()

    # Test customer data
    customer_data = {
        "customer_id": "CUST001",
        "name": "Manya Johri",
        "phone": "+91-9876543210",
        "emi_amount": 15000,
        "due_date": "2025-08-10",
        "overdue_days": 5,
        "language": "en",
    }

    # Test conversation
    print(f"💼 Customer: {customer_data['name']}")
    print(f"💰 EMI Amount: ₹{customer_data['emi_amount']}")
    print(f"📅 Due Date: {customer_data['due_date']}")
    print(f"⏰ Overdue Days: {customer_data['overdue_days']}")
    print("\n" + "=" * 50)

    # Test with AI available
    if agent.gemini_available:
        print("✅ Google Gemini AI is available")
        try:
            # Test analyze_call method
            response = agent.analyze_call(
                call_type="emi_inquiry",
                user_input="Hello, I want to know about my EMI payment",
                customer_context=customer_data,
            )

            print("🎯 AI Response:")
            print(f"Action: {response.get('action', 'N/A')}")
            print(f"Response: {response.get('response', 'N/A')}")
            print(f"Sentiment: {response.get('sentiment', 'N/A')}")
            print(f"Language: {response.get('language', 'N/A')}")

        except Exception as e:
            print(f"❌ Error testing AI: {e}")
    else:
        print("⚠️ Google Gemini AI not available - testing rule-based responses")

        # Test rule-based response
        response = agent.analyze_call(
            call_type="emi_inquiry",
            user_input="Hello, I want to know about my EMI payment",
            customer_context=customer_data,
        )

        print("🎯 Rule-based Response:")
        print(f"Action: {response.get('action', 'N/A')}")
        print(f"Response: {response.get('response', 'N/A')}")
        print(f"Sentiment: {response.get('sentiment', 'N/A')}")
        print(f"Language: {response.get('language', 'N/A')}")

    print("\n" + "=" * 50)
    print("✅ Google AI Integration Test Complete!")


if __name__ == "__main__":
    test_google_ai()
