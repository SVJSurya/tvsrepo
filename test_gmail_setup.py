#!/usr/bin/env python3
"""
Gmail App Password Setup Test
Run this script to test your Gmail configuration
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def test_gmail_connection():
    print("🔍 Testing Gmail Connection...")
    print("=" * 50)

    # Load from .env
    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")

    print(f"📧 Gmail User: {gmail_user}")
    print(f"🔑 Password Set: {'Yes' if gmail_password else 'No (empty)'}")

    if not gmail_user:
        print("❌ GMAIL_USER not set in .env file")
        return False

    if not gmail_password:
        print("❌ GMAIL_APP_PASSWORD not set in .env file")
        print("\n📝 Steps to get App Password:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate App Password for 'Mail'")
        print("3. Copy the 16-character password")
        print("4. Add it to your .env file")
        return False

    try:
        print("\n🔗 Connecting to Gmail SMTP...")

        # Create SMTP connection
        context = ssl.create_default_context()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=context)

        print("✅ SMTP connection established")

        # Try to login
        server.login(gmail_user, gmail_password)
        print("✅ Gmail login successful!")

        # Send test email to yourself
        print(f"\n📤 Sending test email to {gmail_user}...")

        message = MIMEMultipart()
        message["From"] = gmail_user
        message["To"] = gmail_user
        message["Subject"] = "EMI VoiceBot - Gmail Test Email"

        body = """
        🎉 Congratulations! 
        
        Your Gmail SMTP configuration is working perfectly!
        
        ✅ EMI VoiceBot can now send payment links via email
        ✅ The interactive live demo will work with real emails
        ✅ Your system is ready for production use
        
        This is an automated test email from your EMI VoiceBot system.
        
        Best regards,
        EMI VoiceBot AI System
        """

        message.attach(MIMEText(body, "plain"))

        server.sendmail(gmail_user, gmail_user, message.as_string())
        server.quit()

        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox: {gmail_user}")
        print("\n🎯 Your Gmail configuration is ready!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("🔑 Please check your App Password")
        print(
            "💡 Make sure you're using the 16-character App Password, not your regular Gmail password"
        )
        return False

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Load environment variables
    from pathlib import Path

    env_file = Path(".env")

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"').strip("'")

    test_gmail_connection()
