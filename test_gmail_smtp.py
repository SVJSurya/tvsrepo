#!/usr/bin/env python3
"""
Gmail SMTP Test Script
Test your Gmail credentials before using them in the main application
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_gmail_connection():
    """Test Gmail SMTP connection with your credentials"""

    # Get credentials from environment
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    print("🔍 Testing Gmail SMTP Connection...")
    print(f"📧 Email: {sender_email}")
    print(
        f"🔑 App Password: {'*' * 12 + sender_password[-4:] if sender_password and len(sender_password) > 4 else 'Not set'}"
    )

    if not sender_email or not sender_password:
        print("❌ Gmail credentials not found in .env file")
        print("\n📝 Please update your .env file with:")
        print("GMAIL_USER=your-email@gmail.com")
        print("GMAIL_APP_PASSWORD=your-16-character-app-password")
        return False

    if (
        sender_email == "your-email@gmail.com"
        or sender_password == "your-16-character-app-password"
    ):
        print("❌ Please replace placeholder values with your actual Gmail credentials")
        return False

    try:
        # Test SMTP connection
        print("\n🔌 Connecting to Gmail SMTP server...")
        context = ssl.create_default_context()

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("✅ Connected to smtp.gmail.com:587")

            server.starttls(context=context)
            print("✅ TLS encryption enabled")

            server.login(sender_email, sender_password)
            print("✅ Authentication successful")

        print("\n🎉 Gmail SMTP configuration is working correctly!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Common solutions:")
        print("1. Make sure 2-Step Verification is enabled in your Google Account")
        print("2. Generate a new App Password (not your regular Gmail password)")
        print("3. Use the 16-character app password without spaces")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def send_test_email():
    """Send a test email to verify everything works"""

    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    # Ask for test recipient
    recipient = input(
        "\n📧 Enter email address to send test email (or press Enter to skip): "
    ).strip()

    if not recipient:
        print("⏭️ Skipping test email")
        return

    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🧪 EMI VoiceBot - Gmail Test"
        message["From"] = sender_email
        message["To"] = recipient

        # Create test content
        text_content = """
        EMI VoiceBot Gmail Test
        
        This is a test email to verify that Gmail SMTP is working correctly.
        
        If you received this email, your Gmail configuration is successful!
        
        Best regards,
        EMI VoiceBot System
        """

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                .header { text-align: center; color: #2c3e50; margin-bottom: 20px; }
                .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 EMI VoiceBot Gmail Test</h1>
                </div>
                <div class="success">
                    <h3>✅ Success!</h3>
                    <p>This is a test email to verify that Gmail SMTP is working correctly.</p>
                    <p>If you received this email, your Gmail configuration is successful!</p>
                </div>
                <p>Best regards,<br><strong>EMI VoiceBot System</strong></p>
            </div>
        </body>
        </html>
        """

        # Attach parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())

        print(f"✅ Test email sent successfully to {recipient}")
        print("📧 Check your inbox (and spam folder) for the test email")

    except Exception as e:
        print(f"❌ Failed to send test email: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 EMI VoiceBot Gmail SMTP Test")
    print("=" * 60)

    # Test connection
    if test_gmail_connection():
        send_test_email()

    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. If test passed: Restart the EMI VoiceBot server")
    print("2. If test failed: Check your Gmail App Password setup")
    print("3. Use the live demo to test payment link emails")
    print("=" * 60)
