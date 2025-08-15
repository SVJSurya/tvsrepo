#!/usr/bin/env python3
"""
Alternative SMTP Test with Different Approaches
Tests Gmail SMTP with various workarounds for common issues
"""

import os
import smtplib
import ssl
import socket
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_smtp_with_relaxed_ssl():
    """Test SMTP with relaxed SSL settings"""

    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD", "").strip('"').strip("'")

    print("🔍 Testing with relaxed SSL settings...")

    try:
        # Create SSL context with relaxed settings
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Try port 587 with relaxed SSL
        print("📡 Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        server.set_debuglevel(1)  # Enable debug output

        print("🔐 Starting TLS...")
        server.starttls(context=context)

        print("🔑 Logging in...")
        server.login(sender_email, sender_password)

        print("✅ Success with relaxed SSL!")
        server.quit()
        return True

    except Exception as e:
        print(f"❌ Relaxed SSL failed: {e}")
        return False


def test_smtp_ssl_direct():
    """Test direct SSL connection on port 465"""

    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD", "").strip('"').strip("'")

    print("\n🔍 Testing direct SSL connection (port 465)...")

    try:
        # Create relaxed SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        print("📡 Connecting to smtp.gmail.com:465...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=30)
        server.set_debuglevel(1)  # Enable debug output

        print("🔑 Logging in...")
        server.login(sender_email, sender_password)

        print("✅ Success with direct SSL!")
        server.quit()
        return True

    except Exception as e:
        print(f"❌ Direct SSL failed: {e}")
        return False


def send_test_email_simple():
    """Send a simple test email if connection works"""

    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD", "").strip('"').strip("'")

    print("\n📧 Attempting to send test email...")

    try:
        # Use the most basic approach
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Try both approaches
        approaches = [
            (
                "SMTP with STARTTLS",
                lambda: smtplib.SMTP("smtp.gmail.com", 587, timeout=30),
            ),
            (
                "SMTP_SSL direct",
                lambda: smtplib.SMTP_SSL(
                    "smtp.gmail.com", 465, context=context, timeout=30
                ),
            ),
        ]

        for approach_name, server_func in approaches:
            try:
                print(f"\n🔄 Trying {approach_name}...")

                server = server_func()

                if approach_name == "SMTP with STARTTLS":
                    server.starttls(context=context)

                server.login(sender_email, sender_password)

                # Create simple test message
                message = MIMEText("Test email from EMI VoiceBot - SMTP is working!")
                message["Subject"] = "EMI VoiceBot SMTP Test - SUCCESS"
                message["From"] = sender_email
                message["To"] = sender_email

                # Send email
                server.send_message(message)
                server.quit()

                print(f"✅ {approach_name} - Email sent successfully!")
                return True

            except Exception as e:
                print(f"❌ {approach_name} failed: {e}")
                continue

        return False

    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False


def check_network_connectivity():
    """Check basic network connectivity"""

    print("\n🌐 Checking network connectivity...")

    # Test basic internet connectivity
    test_hosts = [
        ("Google DNS", "8.8.8.8", 53),
        ("Gmail SMTP", "smtp.gmail.com", 587),
        ("Gmail SMTP SSL", "smtp.gmail.com", 465),
    ]

    for name, host, port in test_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                print(f"✅ {name}: {host}:{port} - Reachable")
            else:
                print(f"❌ {name}: {host}:{port} - Not reachable (error {result})")

        except Exception as e:
            print(f"❌ {name}: {host}:{port} - Error: {e}")


def main():
    print("🔧 Advanced Gmail SMTP Troubleshooting")
    print("=" * 60)

    # Check network connectivity first
    check_network_connectivity()

    # Test different SMTP approaches
    success = False

    # Try relaxed SSL first
    if test_smtp_with_relaxed_ssl():
        success = True

    # Try direct SSL if first failed
    if not success and test_smtp_ssl_direct():
        success = True

    # Try to send actual email if connection works
    if success:
        print("\n🎉 SMTP connection successful!")
        if send_test_email_simple():
            print("\n✅ EMAIL TEST COMPLETE!")
            print("🚀 Your Gmail SMTP is now working!")
            print("📧 Check your email for the test message")
        else:
            print("\n⚠️ Connection works but email sending failed")
    else:
        print("\n❌ All SMTP connection attempts failed")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if you're behind a corporate firewall")
        print("2. Try connecting from a different network")
        print("3. Verify your App Password is exactly as generated")
        print("4. Make sure Less Secure Apps is disabled (use App Password)")
        print("5. Contact your network administrator about SMTP ports")


if __name__ == "__main__":
    main()
