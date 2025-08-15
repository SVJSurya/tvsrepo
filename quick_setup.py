#!/usr/bin/env python3
"""
Quick Setup Script for Presentations
Sets up the EMI VoiceBot system in 2 minutes for live demos
"""

import os
import sys
import subprocess


def run_command(cmd, description):
    """Run command with progress display"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed!")
        else:
            print(f"⚠️  {description} had warnings: {result.stderr[:100]}")
    except Exception as e:
        print(f"❌ {description} failed: {e}")


def main():
    print("🚀 EMI VoiceBot Quick Setup for Presentations")
    print("=" * 60)
    print("⏱️  This will set up everything in 2 minutes!")

    # Step 1: Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")

    # Step 2: Set up database
    run_command("python production_setup.py --quick", "Setting up database")

    # Step 3: Create sample data
    print("📊 Creating presentation-ready sample data...")
    from production_setup import ProductionSetup

    setup = ProductionSetup()
    setup.setup_database()
    setup.create_sample_data(15)  # 15 customers for demo

    # Step 4: Verify setup
    print("🏥 Running system verification...")
    setup.run_health_check()

    print("\n" + "=" * 60)
    print("🎉 QUICK SETUP COMPLETE!")
    print("=" * 60)

    print(
        """
📋 PRESENTATION OPTIONS:

1️⃣  LIVE WORKFLOW DEMO:
   python live_demo.py
   
2️⃣  INTERACTIVE API DASHBOARD:
   python api_server.py
   Then open: http://localhost:8000
   
3️⃣  SIMPLE COMMAND-LINE DEMO:
   ./start.sh
   
4️⃣  CUSTOM DEMO:
   python simple_demo.py

💡 TIPS FOR PRESENTATIONS:
   • Use option 2 for interactive dashboards
   • Use option 1 for step-by-step workflow demos
   • Set OPENAI_API_KEY for real AI conversations
   • Have backup data ready in case of API issues

🔑 TO ADD REAL API KEYS:
   export OPENAI_API_KEY="your-key-here"
   export TWILIO_ACCOUNT_SID="your-sid-here"
   export TWILIO_AUTH_TOKEN="your-token-here"

📊 SAMPLE DATA CREATED:
   • 15 customers with different risk profiles
   • Various loan types and amounts
   • Due dates spread over next 7 days
   • Different language preferences
   
🚀 Your system is ready for presentations!
    """
    )


if __name__ == "__main__":
    main()
