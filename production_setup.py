#!/usr/bin/env python3
"""
Production Configuration Script
Sets up the EMI VoiceBot system for real-world usage
"""

import os
import sys
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.database import get_db_session, create_tables
from src.models import Customer, Loan, Payment, CustomerInteraction


class ProductionSetup:
    def __init__(self):
        self.db = get_db_session()

    def setup_database(self):
        """Create all necessary tables"""
        print("🏗️  Setting up database tables...")
        create_tables()
        print("✅ Database tables created successfully!")

    def import_customers_from_csv(self, csv_file: str) -> List[Customer]:
        """Import customers from CSV file"""
        print(f"📊 Importing customers from {csv_file}...")

        customers = []
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                customer = Customer(
                    name=row["name"],
                    phone_number=row["phone_number"],
                    email=row.get("email"),
                    address=row.get("address", ""),
                    language_preference=row.get("language_preference", "en"),
                    status=row.get("status", "active"),
                )
                self.db.add(customer)
                customers.append(customer)

        self.db.commit()
        print(f"✅ Imported {len(customers)} customers successfully!")
        return customers

    def import_loans_from_csv(self, csv_file: str) -> List[Loan]:
        """Import loans from CSV file"""
        print(f"💰 Importing loans from {csv_file}...")

        loans = []
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Find customer by phone number or name
                customer = (
                    self.db.query(Customer)
                    .filter(
                        (Customer.phone_number == row.get("customer_phone"))
                        | (Customer.name == row.get("customer_name"))
                    )
                    .first()
                )

                if customer:
                    due_date = datetime.strptime(row["due_date"], "%Y-%m-%d").date()

                    loan = Loan(
                        customer_id=customer.id,
                        loan_amount=float(row["loan_amount"]),
                        outstanding_amount=float(row["outstanding_amount"]),
                        emi_amount=float(row["emi_amount"]),
                        due_date=due_date,
                        status=row.get("status", "active"),
                        loan_type=row.get("loan_type", "personal"),
                        tenure_months=int(row.get("tenure_months", 12)),
                    )
                    self.db.add(loan)
                    loans.append(loan)
                else:
                    print(f"⚠️  Customer not found for loan: {row}")

        self.db.commit()
        print(f"✅ Imported {len(loans)} loans successfully!")
        return loans

    def create_sample_data(self, num_customers: int = 10):
        """Create sample data for demonstration"""
        print(f"🎭 Creating {num_customers} sample customers...")

        sample_customers = [
            {
                "name": "Rahul Sharma",
                "phone": "+919876543210",
                "email": "rahul@example.com",
                "lang": "hi",
                "loan_amount": 500000,
                "emi": 15000,
            },
            {
                "name": "Priya Patel",
                "phone": "+919876543211",
                "email": "priya@example.com",
                "lang": "en",
                "loan_amount": 300000,
                "emi": 12000,
            },
            {
                "name": "Suresh Kumar",
                "phone": "+919876543212",
                "email": "suresh@example.com",
                "lang": "ta",
                "loan_amount": 400000,
                "emi": 18000,
            },
            {
                "name": "Anitha Reddy",
                "phone": "+919876543213",
                "email": "anitha@example.com",
                "lang": "te",
                "loan_amount": 250000,
                "emi": 10000,
            },
            {
                "name": "Vikram Singh",
                "phone": "+919876543214",
                "email": "vikram@example.com",
                "lang": "hi",
                "loan_amount": 600000,
                "emi": 25000,
            },
        ]

        for i, data in enumerate(sample_customers[:num_customers]):
            # Create customer
            customer = Customer(
                name=data["name"],
                phone_number=data["phone"],
                email=data["email"],
                language_preference=data["lang"],
                status="active",
            )
            self.db.add(customer)
            self.db.flush()  # Get customer ID

            # Create loan with due date in next few days
            due_date = datetime.now().date() + timedelta(days=(i % 5) + 1)

            loan = Loan(
                customer_id=customer.id,
                loan_amount=data["loan_amount"],
                outstanding_amount=data["loan_amount"] * 0.8,  # 80% outstanding
                emi_amount=data["emi"],
                due_date=due_date,
                status="active",
                loan_type="personal",
                tenure_months=36,
            )
            self.db.add(loan)

        self.db.commit()
        print(f"✅ Created {num_customers} sample customers with loans!")

    def setup_api_keys_check(self):
        """Check if API keys are configured"""
        print("🔑 Checking API key configuration...")

        required_keys = {
            "OPENAI_API_KEY": "OpenAI API key for conversations",
            "TWILIO_ACCOUNT_SID": "Twilio SID for voice calls",
            "TWILIO_AUTH_TOKEN": "Twilio auth token",
            "RAZORPAY_KEY_ID": "Razorpay key for payments",
        }

        missing_keys = []
        for key, description in required_keys.items():
            if not os.getenv(key):
                missing_keys.append(f"  - {key}: {description}")

        if missing_keys:
            print("⚠️  Missing API keys:")
            for key in missing_keys:
                print(key)
            print("\n💡 Set these in your environment or config/settings.py")
        else:
            print("✅ All API keys configured!")

    def generate_csv_templates(self):
        """Generate CSV templates for data import"""
        print("📝 Generating CSV templates...")

        # Customer template
        customer_template = [
            [
                "name",
                "phone_number",
                "email",
                "address",
                "language_preference",
                "status",
            ],
            [
                "John Doe",
                "+919876543210",
                "john@example.com",
                "123 Main St",
                "en",
                "active",
            ],
            [
                "राज कुमार",
                "+919876543211",
                "raj@example.com",
                "456 Park Ave",
                "hi",
                "active",
            ],
            [
                "Priya Sharma",
                "+919876543212",
                "priya@example.com",
                "789 Oak St",
                "hi",
                "active",
            ],
        ]

        with open("customer_template.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(customer_template)

        # Loan template
        loan_template = [
            [
                "customer_phone",
                "customer_name",
                "loan_amount",
                "outstanding_amount",
                "emi_amount",
                "due_date",
                "status",
                "loan_type",
                "tenure_months",
            ],
            [
                "+919876543210",
                "John Doe",
                "500000",
                "450000",
                "15000",
                "2025-08-20",
                "active",
                "personal",
                "36",
            ],
            [
                "+919876543211",
                "राज कुमार",
                "300000",
                "280000",
                "12000",
                "2025-08-18",
                "active",
                "home",
                "60",
            ],
            [
                "+919876543212",
                "Priya Sharma",
                "200000",
                "180000",
                "8000",
                "2025-08-25",
                "active",
                "vehicle",
                "24",
            ],
        ]

        with open("loan_template.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(loan_template)

        print("✅ Created customer_template.csv and loan_template.csv")

    def run_health_check(self):
        """Run system health check"""
        print("🏥 Running system health check...")

        try:
            # Test database connection
            customer_count = self.db.query(Customer).count()
            loan_count = self.db.query(Loan).count()

            print(f"📊 Database Status:")
            print(f"  - Customers: {customer_count}")
            print(f"  - Loans: {loan_count}")

            # Test API imports
            try:
                from src.agents.trigger_agent import TriggerAgent
                from src.agents.context_agent import ContextAgent
                from src.agents.voicebot_agent import VoiceBotAgent

                print("✅ All agents imported successfully")
            except Exception as e:
                print(f"❌ Agent import error: {e}")

            print("✅ System health check completed!")

        except Exception as e:
            print(f"❌ Health check failed: {e}")


def main():
    """Main setup function"""
    print("🚀 EMI VoiceBot Production Setup")
    print("=" * 50)

    setup = ProductionSetup()

    while True:
        print("\nChoose setup option:")
        print("1. Setup Database Tables")
        print("2. Import Customers from CSV")
        print("3. Import Loans from CSV")
        print("4. Create Sample Data")
        print("5. Generate CSV Templates")
        print("6. Check API Keys")
        print("7. Run Health Check")
        print("8. Complete Setup (All options)")
        print("9. Exit")

        choice = input("\nEnter your choice (1-9): ").strip()

        if choice == "1":
            setup.setup_database()

        elif choice == "2":
            csv_file = input("Enter customer CSV file path: ").strip()
            if os.path.exists(csv_file):
                setup.import_customers_from_csv(csv_file)
            else:
                print("❌ File not found!")

        elif choice == "3":
            csv_file = input("Enter loan CSV file path: ").strip()
            if os.path.exists(csv_file):
                setup.import_loans_from_csv(csv_file)
            else:
                print("❌ File not found!")

        elif choice == "4":
            num = int(input("Enter number of sample customers (default 10): ") or "10")
            setup.create_sample_data(num)

        elif choice == "5":
            setup.generate_csv_templates()

        elif choice == "6":
            setup.setup_api_keys_check()

        elif choice == "7":
            setup.run_health_check()

        elif choice == "8":
            # Complete setup
            setup.setup_database()
            setup.generate_csv_templates()
            setup.create_sample_data(10)
            setup.setup_api_keys_check()
            setup.run_health_check()
            print("🎉 Complete setup finished!")

        elif choice == "9":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
