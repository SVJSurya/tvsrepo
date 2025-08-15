#!/usr/bin/env python3
"""
Real-time Gmail SMTP Test Script
Tests actual email sending with your Gmail credentials
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_gmail_smtp():
    """Test Gmail SMTP connection and send a real test email"""

    # Get credentials from environment
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        print("❌ Error: Gmail credentials not found in .env file")
        return False

    # Clean up password (remove quotes if present)
    sender_password = sender_password.strip('"').strip("'")

    print(f"📧 Testing Gmail SMTP with: {sender_email}")
    print(f"🔐 Password length: {len(sender_password)} characters")

    # Test email details
    test_recipient = input(
        "📮 Enter recipient email for test (press Enter for sender email): "
    ).strip()
    if not test_recipient:
        test_recipient = sender_email

    print(f"📨 Sending test email to: {test_recipient}")

    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🧪 EMI VoiceBot Email Test - " + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        message["From"] = sender_email
        message["To"] = test_recipient

        # Create test payment link
        test_payment_id = str(uuid.uuid4())
        test_payment_link = (
            f"https://emi-payment-demo.example.com/pay/{test_payment_id}"
        )

        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                .test-info {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
                .payment-button {{ display: block; width: 200px; margin: 30px auto; padding: 15px; background: #27ae60; color: white; text-decoration: none; text-align: center; border-radius: 5px; font-weight: bold; }}
                .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 EMI VoiceBot Email Test</h1>
                    <h2>Gmail SMTP Test Successful!</h2>
                </div>
                
                <div class="success">
                    <strong>✅ Email System Working!</strong><br>
                    Your Gmail SMTP configuration is properly set up and working.
                </div>
                
                <div class="test-info">
                    <h3>📋 Test Details:</h3>
                    <p><strong>Test Time:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                    <p><strong>Sender Email:</strong> {sender_email}</p>
                    <p><strong>Test Payment ID:</strong> {test_payment_id}</p>
                    <p><strong>Test Link:</strong> <a href="{test_payment_link}">Demo Payment Link</a></p>
                </div>
                
                <a href="{test_payment_link}" class="payment-button">
                    🔗 Test Payment Link
                </a>
                
                <div class="test-info">
                    <h3>🎯 Next Steps:</h3>
                    <ul>
                        <li>✅ Gmail SMTP is configured correctly</li>
                        <li>✅ Email sending is working</li>
                        <li>✅ Ready for live demo testing</li>
                        <li>🚀 Test the interactive live demo now!</li>
                    </ul>
                </div>
                
                <p style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                    This is an automated test email from the EMI VoiceBot system.<br>
                    Generated at {datetime.now().isoformat()}
                </p>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_content = f"""
        EMI VoiceBot Email Test - SUCCESS!
        
        Your Gmail SMTP configuration is working correctly.
        
        Test Details:
        - Test Time: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        - Sender Email: {sender_email}
        - Test Payment ID: {test_payment_id}
        - Test Link: {test_payment_link}
        
        Next Steps:
        ✅ Gmail SMTP is configured correctly
        ✅ Email sending is working
        ✅ Ready for live demo testing
        🚀 Test the interactive live demo now!
        
        This is an automated test email from the EMI VoiceBot system.
        """

        # Attach parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)

        print("🔄 Connecting to Gmail SMTP server...")

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔐 Starting TLS encryption...")
            server.starttls(context=context)

            print("🔑 Authenticating with Gmail...")
            server.login(sender_email, sender_password)

            print("📤 Sending test email...")
            server.sendmail(sender_email, test_recipient, message.as_string())

        print("\n" + "=" * 60)
        print("✅ EMAIL TEST SUCCESSFUL!")
        print("=" * 60)
        print(f"📧 Test email sent to: {test_recipient}")
        print(f"🆔 Payment ID: {test_payment_id}")
        print(f"🔗 Test Link: {test_payment_link}")
        print(f"⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎉 Your Gmail SMTP is working perfectly!")
        print("🚀 Ready to test the interactive live demo!")
        print("=" * 60)

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR:")
        print(f"   Gmail rejected your credentials")
        print(f"   Error: {str(e)}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check if 2-Step Verification is enabled")
        print(f"   2. Verify your App Password is correct")
        print(
            f"   3. Make sure you're using an App Password, not your regular password"
        )
        return False

    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR:")
        print(f"   Error: {str(e)}")
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   Error: {str(e)}")
        return False


def main():
    print("🧪 EMI VoiceBot - Real-time Gmail SMTP Test")
    print("=" * 60)
    print("This will send a real test email using your Gmail credentials")
    print("=" * 60)

    success = test_gmail_smtp()

    if success:
        print("\n🎯 READY FOR LIVE DEMO!")
        print("   Go to: http://localhost:8001/live-demo")
        print("   Test the interactive payment link feature!")
    else:
        print("\n🔧 SETUP REQUIRED:")
        print("   Please fix the Gmail SMTP configuration")
        print("   Check the troubleshooting steps above")


if __name__ == "__main__":
    main()
