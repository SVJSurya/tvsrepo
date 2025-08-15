#!/usr/bin/env python3
"""
EMI VoiceBot - Installation Verification Script
This script tests that all components are properly installed and configured.
"""

import sys
import os
import importlib
import json
from datetime import datetime


def test_color(text, color="green"):
    """Add color to terminal output"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "end": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"


def check_python_version():
    """Check Python version compatibility"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(test_color(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible", "green"))
        return True
    else:
        print(test_color(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+", "red"))
        return False


def check_required_packages():
    """Check if all required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "google.generativeai",
        "requests",
        "aiohttp",
        "pydantic",
        "sqlalchemy",
        "pandas",
        "numpy",
        "twilio",
        "redis",
        "celery"
    ]
    
    missing_packages = []
    installed_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            installed_packages.append(package)
            print(test_color(f"✅ {package}", "green"))
        except ImportError:
            missing_packages.append(package)
            print(test_color(f"❌ {package}", "red"))
    
    print(f"\n📊 Package Status: {len(installed_packages)}/{len(required_packages)} installed")
    
    if missing_packages:
        print(test_color("\n🔧 To install missing packages:", "yellow"))
        print("pip install -r requirements.txt")
        return False
    
    return True


def check_environment_file():
    """Check if .env file exists and has required variables"""
    print("\n🔧 Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print(test_color("❌ .env file not found", "red"))
        print(test_color("💡 Run ./setup.sh to create .env template", "yellow"))
        return False
    
    print(test_color("✅ .env file found", "green"))
    
    # Check for critical environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        critical_vars = [
            "GOOGLE_API_KEY",
            "GMAIL_USER",
            "GMAIL_APP_PASSWORD"
        ]
        
        configured_vars = []
        missing_vars = []
        
        for var in critical_vars:
            value = os.getenv(var, "")
            if value and not value.startswith("your_"):
                configured_vars.append(var)
                print(test_color(f"✅ {var}: Configured", "green"))
            else:
                missing_vars.append(var)
                print(test_color(f"⚠️ {var}: Not configured", "yellow"))
        
        if missing_vars:
            print(test_color(f"\n💡 Configure these variables in .env for full functionality", "yellow"))
        
        return True
        
    except ImportError:
        print(test_color("❌ python-dotenv not installed", "red"))
        return False


def check_required_files():
    """Check if all required project files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "advanced_ui_server.py",
        "src/agents/trigger_agent.py",
        "src/agents/context_agent.py",
        "src/agents/google_voicebot_agent.py",
        "src/agents/decision_agent.py",
        "src/agents/payment_agent.py",
        "src/agents/logging_learning_agent.py",
        "templates/live_call_demo.html",
        "templates/voice_demo.html"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(test_color(f"✅ {file_path}", "green"))
        else:
            missing_files.append(file_path)
            print(test_color(f"❌ {file_path}", "red"))
    
    print(f"\n📊 File Status: {len(existing_files)}/{len(required_files)} found")
    
    if missing_files:
        print(test_color("\n🔧 Missing critical files - check project structure", "red"))
        return False
    
    return True


def test_google_ai_connection():
    """Test Google AI API connection"""
    print("\n🤖 Testing Google AI connection...")
    
    try:
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key or api_key.startswith("your_"):
            print(test_color("⚠️ Google AI API key not configured", "yellow"))
            return False
        
        # Try to import and use Google AI
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello, this is a test connection.")
            
            if response and response.text:
                print(test_color("✅ Google AI connection successful", "green"))
                print(test_color(f"🤖 Test response: {response.text[:100]}...", "blue"))
                return True
            else:
                print(test_color("❌ Google AI returned empty response", "red"))
                return False
        except ImportError:
            print(test_color("❌ Google AI package not installed properly", "red"))
            return False
        except AttributeError as e:
            print(test_color(f"❌ Google AI API issue: {str(e)}", "red"))
            print(test_color("💡 Try: pip install --upgrade google-generativeai", "yellow"))
            return False
            
    except Exception as e:
        print(test_color(f"❌ Google AI connection failed: {str(e)}", "red"))
        return False


def test_server_import():
    """Test if server can be imported without errors"""
    print("\n🌐 Testing server import...")
    
    try:
        # Change to project directory to ensure imports work
        sys.path.insert(0, os.getcwd())
        
        # Try to import the server module
        import advanced_ui_server
        print(test_color("✅ Server module imports successfully", "green"))
        return True
        
    except Exception as e:
        print(test_color(f"❌ Server import failed: {str(e)}", "red"))
        return False


def create_test_report():
    """Create a test report file"""
    print("\n📄 Generating test report...")
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "tests_run": [
            "Python version check",
            "Required packages check",
            "Environment file check",
            "Required files check",
            "Google AI connection test",
            "Server import test"
        ],
        "status": "completed"
    }
    
    try:
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print(test_color("✅ Test report saved to test_report.json", "green"))
    except Exception as e:
        print(test_color(f"⚠️ Could not save test report: {e}", "yellow"))


def main():
    """Run all verification tests"""
    print(test_color("🚀 EMI VoiceBot - Installation Verification", "blue"))
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Environment Configuration", check_environment_file),
        ("Required Files", check_required_files),
        ("Google AI Connection", test_google_ai_connection),
        ("Server Import", test_server_import)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_function():
                passed_tests += 1
        except Exception as e:
            print(test_color(f"❌ Test failed with exception: {e}", "red"))
    
    # Final Results
    print("\n" + "="*60)
    print(test_color("🎯 VERIFICATION RESULTS", "blue"))
    print("="*60)
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print(test_color("🎉 ALL TESTS PASSED! System is ready to use.", "green"))
        print(test_color("\n🚀 To start the server:", "blue"))
        print("   python advanced_ui_server.py")
        print(test_color("\n🌐 Access the dashboard:", "blue"))
        print("   http://localhost:8001")
    elif passed_tests >= total_tests * 0.8:
        print(test_color("⚠️ MOST TESTS PASSED - Minor issues detected", "yellow"))
        print(test_color("💡 System should work with limited functionality", "yellow"))
    else:
        print(test_color("❌ MULTIPLE TESTS FAILED - Setup incomplete", "red"))
        print(test_color("🔧 Please fix the issues and run the verification again", "red"))
    
    # Create test report
    create_test_report()
    
    print(f"\n⏰ Verification completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
