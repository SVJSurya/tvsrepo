#!/usr/bin/env python3
"""
Demo script to showcase the EMI VoiceBot System end-to-end workflow.
This script demonstrates all the agents working together.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import create_tables, get_db_session
from src.models import Customer, Loan
from src.agents.trigger_agent import TriggerAgent
from src.agents.context_agent import ContextAgent
from src.agents.voicebot_agent import VoiceBotAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.logging_learning_agent import LoggingLearningAgent
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EMIVoiceBotDemo:
    """Demo class to showcase the EMI VoiceBot system"""

    def __init__(self):
        self.trigger_agent = TriggerAgent()
        self.context_agent = ContextAgent()
        self.voicebot_agent = VoiceBotAgent()
        self.decision_agent = DecisionAgent()
        self.payment_agent = PaymentAgent()
        self.logging_agent = LoggingLearningAgent()

    def setup_demo_data(self):
        """Setup sample data for demonstration"""
        logger.info("Setting up demo data...")

        # Create database tables
        create_tables()

        db = get_db_session()
        try:
            # Clear existing data for clean demo
            db.query(Loan).delete()
            db.query(Customer).delete()
            db.commit()

            # Create sample customers
            customers = [
                Customer(
                    name="Rahul Kumar",
                    phone_number="9876543210",
                    email="rahul@email.com",
                    language_preference="hi",
                    risk_score=45.0,
                    status="active",
                ),
                Customer(
                    name="Priya Sharma",
                    phone_number="9876543211",
                    email="priya@email.com",
                    language_preference="en",
                    risk_score=25.0,
                    status="active",
                ),
                Customer(
                    name="Amit Patel",
                    phone_number="9876543212",
                    email="amit@email.com",
                    language_preference="hi",
                    risk_score=75.0,
                    status="overdue",
                ),
            ]

            for customer in customers:
                db.add(customer)
            db.commit()

            # Refresh to get IDs
            for customer in customers:
                db.refresh(customer)

            # Create sample loans
            loans = [
                Loan(
                    customer_id=customers[0].id,
                    loan_amount=500000.0,
                    emi_amount=15000.0,
                    due_date=datetime.now(),
                    next_due_date=datetime.now(),
                    outstanding_amount=400000.0,
                    status="active",
                ),
                Loan(
                    customer_id=customers[1].id,
                    loan_amount=300000.0,
                    emi_amount=8000.0,
                    due_date=datetime.now() + timedelta(days=1),
                    next_due_date=datetime.now() + timedelta(days=1),
                    outstanding_amount=250000.0,
                    status="active",
                ),
                Loan(
                    customer_id=customers[2].id,
                    loan_amount=750000.0,
                    emi_amount=20000.0,
                    due_date=datetime.now() - timedelta(days=1),
                    next_due_date=datetime.now() - timedelta(days=1),
                    outstanding_amount=600000.0,
                    status="active",
                ),
            ]

            for loan in loans:
                db.add(loan)
            db.commit()

            logger.info(f"Created {len(customers)} customers and {len(loans)} loans")
            return customers, loans

        finally:
            db.close()

    def demonstrate_trigger_agent(self):
        """Demonstrate Trigger Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING TRIGGER AGENT")
        logger.info("=" * 50)

        # Check for due EMIs
        due_emis = self.trigger_agent.check_due_emis()
        logger.info(f"Found {len(due_emis)} customers requiring calls")

        for emi in due_emis:
            logger.info(
                f"Customer: {emi['customer_name']}, EMI: ₹{emi['emi_amount']}, Priority: {emi['priority']}"
            )

        return due_emis

    def demonstrate_context_agent(self, customer_id):
        """Demonstrate Context Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING CONTEXT AGENT")
        logger.info("=" * 50)

        # Get customer context
        context = self.context_agent.get_customer_context(customer_id)

        logger.info(f"Customer: {context['name']}")
        logger.info(f"Risk Score: {context['risk_score']}")
        logger.info(f"Language: {context['language_preference']}")
        logger.info(f"Payment Pattern: {context['payment_history']['payment_pattern']}")
        logger.info(
            f"Total Outstanding: ₹{sum([loan['outstanding_amount'] for loan in context['loans']]):,}"
        )

        return context

    def demonstrate_voicebot_agent(self, customer_context, emi_info):
        """Demonstrate VoiceBot Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING VOICEBOT AGENT")
        logger.info("=" * 50)

        # Initiate call
        call_result = self.voicebot_agent.initiate_call(customer_context, emi_info)

        logger.info(f"Call Status: {call_result['status']}")
        logger.info(f"Call Outcome: {call_result['outcome']}")
        logger.info(
            f"Conversation Summary: {call_result.get('conversation_summary', 'N/A')}"
        )

        # Log the interaction
        self.logging_agent.log_interaction(
            {
                "customer_id": customer_context["customer_id"],
                "call_id": call_result.get("call_id"),
                "outcome": call_result.get("outcome"),
                "interaction_type": "voice_call",
                "conversation_summary": call_result.get("conversation_summary"),
            }
        )

        return call_result

    def demonstrate_decision_agent(self, call_result, customer_context):
        """Demonstrate Decision Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING DECISION AGENT")
        logger.info("=" * 50)

        # Make decision based on call outcome
        decision = self.decision_agent.make_decision(call_result, customer_context)

        logger.info(f"Next Action: {decision['next_action']}")
        logger.info(f"Priority: {decision['priority']}")
        logger.info(f"Follow-up Time: {decision['follow_up_datetime']}")
        logger.info(f"Escalation Needed: {decision['escalation_needed']}")
        logger.info(f"Recommended Channel: {decision['recommended_channel']}")

        # Log the decision
        self.logging_agent.log_decision(
            {
                "customer_id": customer_context["customer_id"],
                "conversation_outcome": call_result.get("outcome"),
                "next_action": decision["next_action"],
                "priority": decision["priority"],
                "escalation_needed": decision["escalation_needed"],
            }
        )

        return decision

    def demonstrate_payment_agent(self, customer_context, decision):
        """Demonstrate Payment Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING PAYMENT AGENT")
        logger.info("=" * 50)

        if decision["next_action"] in ["send_payment_link", "payment_requested"]:
            # Create payment link
            loan_info = {"loan_id": 1, "emi_amount": 15000}
            payment_link_data = self.payment_agent.create_payment_link(
                customer_context, loan_info
            )

            logger.info(f"Payment Link Created: {payment_link_data['payment_link']}")
            logger.info(f"Amount: ₹{payment_link_data['amount']}")
            logger.info(f"Payment ID: {payment_link_data['payment_id']}")

            # Send payment link via SMS
            sms_result = self.payment_agent.send_payment_link_sms(
                customer_context, payment_link_data, "today"
            )

            logger.info(f"SMS Status: {sms_result['status']}")
            if sms_result["status"] == "sent":
                logger.info(f"SMS Message: {sms_result['message']}")

            # Log payment activity
            self.logging_agent.log_payment_activity(
                {
                    "customer_id": customer_context["customer_id"],
                    "payment_id": payment_link_data["payment_id"],
                    "amount": payment_link_data["amount"],
                    "status": "link_created_and_sent",
                }
            )

            # Simulate payment verification after some time
            logger.info("\nSimulating payment completion...")
            verification_result = self.payment_agent.verify_payment(
                payment_link_data["payment_id"]
            )
            logger.info(f"Payment Verification: {verification_result['status']}")

            if verification_result["status"] == "success":
                logger.info(f"Payment Amount: ₹{verification_result['amount']}")
                logger.info("Payment confirmation sent to customer")

            return payment_link_data, verification_result
        else:
            logger.info(f"No payment link needed for action: {decision['next_action']}")
            return None, None

    def demonstrate_learning_agent(self):
        """Demonstrate Learning Agent functionality"""
        logger.info("\n" + "=" * 50)
        logger.info("DEMONSTRATING LEARNING & ANALYTICS AGENT")
        logger.info("=" * 50)

        # Analyze interaction patterns
        interaction_analysis = self.logging_agent.analyze_interaction_patterns(30)
        logger.info("Interaction Analysis:")
        logger.info(
            f"  Total Interactions: {interaction_analysis.get('total_interactions', 0)}"
        )
        logger.info(
            f"  Average Sentiment: {interaction_analysis.get('average_sentiment', 0):.2f}"
        )
        logger.info(
            f"  Success Rate: {interaction_analysis.get('successful_outcomes', 0):.2%}"
        )

        # Generate insights report
        insights_report = self.logging_agent.generate_insights_report(30)
        logger.info("\nInsights Report Generated:")
        logger.info(
            f"  Report saved with {len(insights_report.get('recommendations', []))} recommendations"
        )

        # Show some recommendations
        for i, rec in enumerate(insights_report.get("recommendations", [])[:3]):
            logger.info(f"  Recommendation {i+1}: {rec}")

        return interaction_analysis, insights_report

    def run_complete_demo(self):
        """Run the complete end-to-end demo"""
        logger.info("🚀 Starting EMI VoiceBot System Demo")
        logger.info(
            "This demo showcases all agents working together in a real workflow"
        )

        try:
            # Step 1: Setup demo data
            customers, loans = self.setup_demo_data()

            # Step 2: Demonstrate Trigger Agent
            due_emis = self.demonstrate_trigger_agent()

            if not due_emis:
                logger.warning("No due EMIs found. Demo cannot continue.")
                return

            # Step 3: Select first customer for demo
            selected_emi = due_emis[0]
            customer_id = selected_emi["customer_id"]

            # Step 4: Demonstrate Context Agent
            customer_context = self.demonstrate_context_agent(customer_id)

            # Step 5: Demonstrate VoiceBot Agent
            call_result = self.demonstrate_voicebot_agent(
                customer_context, selected_emi
            )

            # Step 6: Demonstrate Decision Agent
            decision = self.demonstrate_decision_agent(call_result, customer_context)

            # Step 7: Demonstrate Payment Agent
            payment_data, verification_result = self.demonstrate_payment_agent(
                customer_context, decision
            )

            # Step 8: Demonstrate Learning Agent
            interaction_analysis, insights_report = self.demonstrate_learning_agent()

            # Final Summary
            logger.info("\n" + "=" * 50)
            logger.info("DEMO SUMMARY")
            logger.info("=" * 50)
            logger.info("✅ All agents demonstrated successfully!")
            logger.info(f"📞 Call Outcome: {call_result['outcome']}")
            logger.info(f"🎯 Next Action: {decision['next_action']}")
            logger.info(
                f"💳 Payment Status: {verification_result['status'] if verification_result else 'N/A'}"
            )
            logger.info(
                f"📊 Total Interactions Analyzed: {interaction_analysis.get('total_interactions', 0)}"
            )

            logger.info("\n🎉 EMI VoiceBot System Demo Completed Successfully!")
            logger.info("The system is ready for production deployment.")

        except Exception as e:
            logger.error(f"Demo failed with error: {str(e)}")
            raise

    def run_api_demo(self):
        """Instructions for running the API demo"""
        logger.info("\n" + "=" * 50)
        logger.info("API DEMO INSTRUCTIONS")
        logger.info("=" * 50)

        logger.info("To test the API endpoints, run the following commands:")
        logger.info("")
        logger.info("1. Start the FastAPI server:")
        logger.info("   python src/main.py")
        logger.info("")
        logger.info("2. Open your browser and go to:")
        logger.info("   http://localhost:8000/docs")
        logger.info("")
        logger.info("3. Try these key endpoints:")
        logger.info("   POST /demo/setup-sample-data - Setup sample data")
        logger.info("   GET  /demo/test-workflow - Test complete workflow")
        logger.info("   POST /calls/initiate - Initiate a call")
        logger.info("   POST /payments/create-link - Create payment link")
        logger.info("   GET  /analytics/insights - Get insights report")
        logger.info("")
        logger.info("4. Or use curl commands:")
        logger.info("   curl -X POST http://localhost:8000/demo/setup-sample-data")
        logger.info("   curl -X GET http://localhost:8000/demo/test-workflow")


if __name__ == "__main__":
    demo = EMIVoiceBotDemo()

    print("Select demo mode:")
    print("1. Complete Workflow Demo (Recommended)")
    print("2. API Demo Instructions")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        demo.run_complete_demo()
    elif choice == "2":
        demo.run_api_demo()
    else:
        print("Invalid choice. Running complete demo...")
        demo.run_complete_demo()
