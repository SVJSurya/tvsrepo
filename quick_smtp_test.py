#!/usr/bin/env python3
"""
Quick SMTP Connection Test
Diagnoses Gmail SMTP connection issues step by step
"""

import os
import smtplib
import ssl
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_smtp_connection():
    """Test SMTP connection step by step"""

    # Get credentials
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD", "").strip('"').strip("'")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    print("🔍 SMTP Connection Diagnostics")
    print("=" * 50)
    print(f"📧 Email: {sender_email}")
    print(f"🔐 Password: {'*' * len(sender_password)} ({len(sender_password)} chars)")
    print(f"🌐 Server: {smtp_server}")
    print(f"🔌 Port: {smtp_port}")
    print("=" * 50)

    # Step 1: Test DNS resolution
    print("\n🔍 Step 1: Testing DNS resolution...")
    try:
        ip = socket.gethostbyname(smtp_server)
        print(f"✅ DNS OK: {smtp_server} → {ip}")
    except Exception as e:
        print(f"❌ DNS Error: {e}")
        return False

    # Step 2: Test basic socket connection
    print("\n🔍 Step 2: Testing socket connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((smtp_server, smtp_port))
        sock.close()

        if result == 0:
            print(f"✅ Socket connection OK to {smtp_server}:{smtp_port}")
        else:
            print(f"❌ Socket connection failed: Error code {result}")
            return False
    except Exception as e:
        print(f"❌ Socket Error: {e}")
        return False

    # Step 3: Test SMTP connection
    print("\n🔍 Step 3: Testing SMTP connection...")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        print(f"✅ SMTP connection established")

        # Step 4: Test STARTTLS
        print("\n🔍 Step 4: Testing STARTTLS...")
        context = ssl.create_default_context()
        server.starttls(context=context)
        print(f"✅ TLS encryption started")

        # Step 5: Test authentication
        print("\n🔍 Step 5: Testing authentication...")
        server.login(sender_email, sender_password)
        print(f"✅ Authentication successful")

        server.quit()
        print("\n🎉 ALL TESTS PASSED!")
        print("📧 Gmail SMTP is working correctly")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if App Password is correct")
        print("   2. Ensure 2-Step Verification is enabled")
        print("   3. Try generating a new App Password")
        return False

    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False

    except socket.timeout:
        print(f"❌ Connection timeout - server not responding")
        print("🔧 This might be a network/firewall issue")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_alternative_ports():
    """Test alternative SMTP ports"""
    print("\n🔍 Testing alternative SMTP ports...")

    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD", "").strip('"').strip("'")

    # Gmail SMTP configurations to try
    configs = [
        ("smtp.gmail.com", 587, True),  # Standard TLS
        ("smtp.gmail.com", 465, False),  # SSL
        ("smtp.gmail.com", 25, True),  # Legacy
    ]

    for server, port, use_starttls in configs:
        print(f"\n📡 Testing {server}:{port} (TLS: {use_starttls})")
        try:
            if port == 465:
                # SSL connection
                context = ssl.create_default_context()
                smtp_server = smtplib.SMTP_SSL(
                    server, port, context=context, timeout=10
                )
            else:
                # Regular connection with optional STARTTLS
                smtp_server = smtplib.SMTP(server, port, timeout=10)
                if use_starttls:
                    context = ssl.create_default_context()
                    smtp_server.starttls(context=context)

            smtp_server.login(sender_email, sender_password)
            smtp_server.quit()
            print(f"✅ Success with {server}:{port}")
            return server, port, use_starttls

        except Exception as e:
            print(f"❌ Failed: {e}")

    return None, None, None


def main():
    print("🧪 Gmail SMTP Quick Diagnostic Test")

    if not test_smtp_connection():
        print("\n🔄 Trying alternative configurations...")
        server, port, tls = test_alternative_ports()

        if server:
            print(f"\n✅ Working configuration found:")
            print(f"   Server: {server}")
            print(f"   Port: {port}")
            print(f"   Use TLS: {tls}")
        else:
            print(f"\n❌ No working SMTP configuration found")
            print(f"🔧 Possible issues:")
            print(f"   1. Incorrect App Password")
            print(f"   2. Network/Firewall blocking SMTP")
            print(f"   3. 2-Step Verification not properly enabled")


if __name__ == "__main__":
    main()
