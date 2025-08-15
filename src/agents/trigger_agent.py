import schedule
import time
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from src.utils.database import get_db_session
from src.utils.model_helpers import safe_int
from src.models import Customer, Loan
from src.agents.context_agent import ContextAgent
from src.agents.voicebot_agent import VoiceBotAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TriggerAgent:
    """
    Agent responsible for monitoring EMI due dates and initiating workflow.
    Triggers voice calls based on predefined business rules.
    """

    def __init__(self):
        self.context_agent = ContextAgent()
        self.voicebot_agent = VoiceBotAgent()
        self.reminder_days = [7, 3, 1, 0]  # Days before due date to trigger calls

    def check_due_emis(self) -> List[dict]:
        """
        Check for EMIs that are due or approaching due date.
        Returns list of customers requiring calls.
        """
        db = get_db_session()
        try:
            upcoming_dues = []
            today = datetime.now()

            for days_ahead in self.reminder_days:
                target_date = today + timedelta(days=days_ahead)

                # Query loans with due dates
                loans = (
                    db.query(Loan)
                    .filter(
                        Loan.next_due_date.between(
                            target_date.replace(hour=0, minute=0, second=0),
                            target_date.replace(hour=23, minute=59, second=59),
                        ),
                        Loan.status == "active",
                    )
                    .all()
                )

                for loan in loans:
                    customer_context = self.context_agent.get_customer_context(
                        safe_int(loan.customer_id)
                    )

                    upcoming_dues.append(
                        {
                            "loan_id": loan.id,
                            "customer_id": loan.customer_id,
                            "customer_name": customer_context["name"],
                            "phone_number": customer_context["phone_number"],
                            "emi_amount": loan.emi_amount,
                            "due_date": loan.next_due_date,
                            "days_until_due": days_ahead,
                            "outstanding_amount": loan.outstanding_amount,
                            "priority": self._calculate_priority(
                                customer_context, days_ahead
                            ),
                        }
                    )

            return sorted(upcoming_dues, key=lambda x: x["priority"], reverse=True)

        finally:
            db.close()

    def _calculate_priority(self, customer_context: dict, days_until_due: int) -> int:
        """
        Calculate priority score for calling customer.
        Higher score = higher priority
        """
        priority = 100

        # Risk score factor
        priority += customer_context.get("risk_score", 0) * 20

        # Days until due factor
        if days_until_due == 0:
            priority += 50  # Due today
        elif days_until_due == 1:
            priority += 30  # Due tomorrow
        elif days_until_due == 3:
            priority += 15  # Due in 3 days

        # Previous interaction factor
        recent_interactions = customer_context.get("recent_interactions", [])
        interaction_count = (
            len(recent_interactions)
            if isinstance(recent_interactions, list)
            else recent_interactions
        )
        if interaction_count < 2:
            priority += 10  # Haven't called much recently

        return int(priority)

    def trigger_voice_calls(self):
        """
        Main method to trigger voice calls for due EMIs.
        """
        logger.info("Starting EMI due check and voice call triggers...")

        due_emis = self.check_due_emis()

        if not due_emis:
            logger.info("No EMIs due for calling today.")
            return

        logger.info(f"Found {len(due_emis)} customers requiring calls")

        for emi_info in due_emis:
            try:
                # Get full customer context
                customer_context = self.context_agent.get_customer_context(
                    emi_info["customer_id"]
                )

                # Trigger voice call
                call_result = self.voicebot_agent.initiate_call(
                    customer_context=customer_context, emi_info=emi_info
                )

                logger.info(
                    f"Call initiated for customer {emi_info['customer_name']}: {call_result}"
                )

            except Exception as e:
                logger.error(
                    f"Error triggering call for customer {emi_info['customer_id']}: {str(e)}"
                )

    def schedule_daily_checks(self):
        """
        Schedule daily EMI checks at specific times.
        """
        # Schedule calls at 10 AM and 3 PM
        schedule.every().day.at("10:00").do(self.trigger_voice_calls)
        schedule.every().day.at("15:00").do(self.trigger_voice_calls)

        logger.info("Scheduled daily EMI checks at 10:00 AM and 3:00 PM")

    def run_scheduler(self):
        """
        Run the scheduler continuously.
        """
        self.schedule_daily_checks()

        logger.info("Trigger Agent scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def manual_trigger(self, customer_id: Optional[int] = None):
        """
        Manually trigger calls for testing purposes.
        """
        if customer_id:
            customer_context = self.context_agent.get_customer_context(customer_id)
            call_result = self.voicebot_agent.initiate_call(
                customer_context=customer_context, emi_info={"manual_trigger": True}
            )
            return call_result
        else:
            return self.trigger_voice_calls()


if __name__ == "__main__":
    trigger_agent = TriggerAgent()
    trigger_agent.run_scheduler()
