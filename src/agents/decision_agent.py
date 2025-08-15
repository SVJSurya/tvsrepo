from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from src.utils.database import get_db_session
from src.models import Customer, Loan, CustomerInteraction

logger = logging.getLogger(__name__)


class DecisionAgent:
    """
    Agent responsible for determining next steps based on customer interactions.
    Uses rule-based logic and could be enhanced with ML models.
    """

    def __init__(self):
        self.decision_rules = self._load_decision_rules()

    def _load_decision_rules(self) -> Dict:
        """
        Load business rules for decision making.
        """
        return {
            "payment_agreement": {
                "next_action": "send_payment_link",
                "priority": "high",
                "follow_up_hours": 2,
            },
            "payment_requested": {
                "next_action": "send_payment_link",
                "priority": "high",
                "follow_up_hours": 2,
            },
            "promised_payment": {
                "next_action": "schedule_follow_up",
                "priority": "medium",
                "follow_up_hours": 24,
            },
            "payment_delay": {
                "next_action": "schedule_follow_up",
                "priority": "medium",
                "follow_up_hours": 48,
            },
            "reschedule_requested": {
                "next_action": "schedule_callback",
                "priority": "low",
                "follow_up_hours": 24,
            },
            "no_response": {
                "next_action": "retry_call",
                "priority": "medium",
                "follow_up_hours": 6,
            },
            "payment_refusal": {
                "next_action": "escalate_to_human",
                "priority": "high",
                "follow_up_hours": 4,
            },
            "unclear": {
                "next_action": "retry_call",
                "priority": "low",
                "follow_up_hours": 12,
            },
        }

    def make_decision(self, conversation_result: Dict, customer_context: Dict) -> Dict:
        """
        Make decision based on conversation outcome and customer context.
        """
        outcome = conversation_result.get("outcome", "unclear")
        sentiment_score = conversation_result.get("sentiment_score", 0.0)
        customer_risk_score = customer_context.get("risk_score", 50)

        # Get base decision from rules
        base_decision = self.decision_rules.get(outcome, self.decision_rules["unclear"])

        # Enhance decision with contextual factors
        enhanced_decision = self._enhance_decision_with_context(
            base_decision, customer_context, conversation_result
        )

        # Determine escalation needs
        escalation_decision = self._check_escalation_criteria(
            customer_context, conversation_result
        )

        # Combine decisions
        final_decision = {
            "next_action": enhanced_decision["next_action"],
            "priority": enhanced_decision["priority"],
            "follow_up_datetime": self._calculate_follow_up_time(
                enhanced_decision["follow_up_hours"]
            ),
            "escalation_needed": escalation_decision["escalation_needed"],
            "escalation_reason": escalation_decision["reason"],
            "recommended_channel": self._recommend_communication_channel(
                customer_context, outcome
            ),
            "message_tone": self._determine_message_tone(
                customer_context, sentiment_score
            ),
            "additional_actions": self._get_additional_actions(
                customer_context, outcome
            ),
        }

        # Log decision
        self._log_decision(
            customer_context["customer_id"], final_decision, conversation_result
        )

        return final_decision

    def _enhance_decision_with_context(
        self, base_decision: Dict, customer_context: Dict, conversation_result: Dict
    ) -> Dict:
        """
        Enhance base decision with customer-specific context.
        """
        enhanced_decision = base_decision.copy()

        risk_score = customer_context.get("risk_score", 50)
        payment_history = customer_context.get("payment_history", {})
        recent_interactions = customer_context.get("recent_interactions", [])

        # Adjust priority based on risk score
        if risk_score > 80:
            enhanced_decision["priority"] = "critical"
            enhanced_decision["follow_up_hours"] = min(
                enhanced_decision["follow_up_hours"], 2
            )
        elif risk_score > 60:
            enhanced_decision["priority"] = "high"
            enhanced_decision["follow_up_hours"] = min(
                enhanced_decision["follow_up_hours"], 4
            )

        # Adjust based on payment history
        if payment_history.get("payment_pattern") == "good":
            enhanced_decision["follow_up_hours"] = (
                enhanced_decision["follow_up_hours"] * 1.5
            )
        elif payment_history.get("payment_pattern") == "poor":
            enhanced_decision["follow_up_hours"] = (
                enhanced_decision["follow_up_hours"] * 0.75
            )

        # Adjust based on recent interaction count
        if len(recent_interactions) > 3:
            enhanced_decision["follow_up_hours"] = (
                enhanced_decision["follow_up_hours"] * 1.25
            )

        return enhanced_decision

    def _check_escalation_criteria(
        self, customer_context: Dict, conversation_result: Dict
    ) -> Dict:
        """
        Check if escalation to human agent is needed.
        """
        escalation_needed = False
        reason = None

        risk_score = customer_context.get("risk_score", 50)
        outcome = conversation_result.get("outcome")
        recent_interactions = customer_context.get("recent_interactions", [])
        sentiment_score = conversation_result.get("sentiment_score", 0.0)

        # High risk customer
        if risk_score > 85:
            escalation_needed = True
            reason = "high_risk_customer"

        # Negative sentiment
        elif sentiment_score < -0.5:
            escalation_needed = True
            reason = "negative_customer_sentiment"

        # Multiple failed attempts
        elif (
            len(
                [
                    i
                    for i in recent_interactions
                    if i["outcome"] in ["no_response", "payment_refusal"]
                ]
            )
            >= 3
        ):
            escalation_needed = True
            reason = "multiple_failed_attempts"

        # Payment refusal
        elif outcome == "payment_refusal":
            escalation_needed = True
            reason = "payment_refusal"

        # VIP customer requiring special handling
        elif self._is_vip_customer(customer_context):
            escalation_needed = True
            reason = "vip_customer_handling"

        return {"escalation_needed": escalation_needed, "reason": reason}

    def _is_vip_customer(self, customer_context: Dict) -> bool:
        """
        Check if customer is VIP based on loan amounts and history.
        """
        total_loan_amount = sum(
            [loan["loan_amount"] for loan in customer_context.get("loans", [])]
        )
        payment_pattern = customer_context.get("payment_history", {}).get(
            "payment_pattern"
        )

        return total_loan_amount > 500000 and payment_pattern == "good"

    def _calculate_follow_up_time(self, hours: float) -> datetime:
        """
        Calculate next follow-up datetime.
        """
        return datetime.now() + timedelta(hours=hours)

    def _recommend_communication_channel(
        self, customer_context: Dict, outcome: str
    ) -> str:
        """
        Recommend the best communication channel for follow-up.
        """
        recent_interactions = customer_context.get("recent_interactions", [])

        # If customer didn't respond to voice, try SMS/WhatsApp
        if outcome in ["no_response", "reschedule_requested"]:
            return "sms"

        # If customer was cooperative, continue with voice
        elif outcome in ["payment_requested", "promised_payment"]:
            return "voice"

        # For unclear responses, try different channel
        elif outcome == "unclear":
            voice_attempts = len(
                [i for i in recent_interactions if i["type"] == "voice_call"]
            )
            if voice_attempts >= 2:
                return "sms"
            else:
                return "voice"

        return "voice"  # Default

    def _determine_message_tone(
        self, customer_context: Dict, sentiment_score: float
    ) -> str:
        """
        Determine appropriate tone for communication.
        """
        risk_score = customer_context.get("risk_score", 50)
        payment_pattern = customer_context.get("payment_history", {}).get(
            "payment_pattern"
        )

        if sentiment_score > 0.5:
            return "friendly"
        elif sentiment_score < -0.3:
            return "empathetic"
        elif payment_pattern == "good":
            return "respectful"
        elif risk_score > 70:
            return "firm_but_polite"
        else:
            return "professional"

    def _get_additional_actions(
        self, customer_context: Dict, outcome: str
    ) -> List[str]:
        """
        Get list of additional actions to take.
        """
        actions = []

        risk_score = customer_context.get("risk_score", 50)

        # Update customer risk score
        actions.append("update_risk_score")

        # Send SMS reminder for high-risk customers
        if risk_score > 70:
            actions.append("send_sms_reminder")

        # Update CRM with interaction
        actions.append("update_crm")

        # Schedule payment reminder
        if outcome in ["promised_payment", "payment_delay"]:
            actions.append("schedule_payment_reminder")

        # Generate payment link
        if outcome in ["payment_requested", "payment_agreement"]:
            actions.append("generate_payment_link")

        return actions

    def _log_decision(
        self, customer_id: int, decision: Dict, conversation_result: Dict
    ):
        """
        Log the decision for audit and learning purposes.
        """
        logger.info(
            f"Decision made for customer {customer_id}: {decision['next_action']}"
        )

        # Here you could log to database or analytics system
        # For now, just log to file
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": customer_id,
            "conversation_outcome": conversation_result.get("outcome"),
            "decision": decision,
        }

        # In production, save this to a decision log table or analytics system

    def get_pending_actions(self, customer_id: Optional[int] = None) -> List[Dict]:
        """
        Get list of pending actions that need to be executed.
        """
        # This would query a task/action queue in production
        # For demo, return empty list
        return []

    def execute_action(self, action: Dict) -> Dict:
        """
        Execute a specific action.
        """
        action_type = action.get("action_type")

        if action_type == "send_payment_link":
            return self._send_payment_link(action)
        elif action_type == "schedule_follow_up":
            return self._schedule_follow_up(action)
        elif action_type == "escalate_to_human":
            return self._escalate_to_human(action)
        elif action_type == "send_sms_reminder":
            return self._send_sms_reminder(action)
        else:
            return {
                "status": "unknown_action",
                "message": f"Unknown action type: {action_type}",
            }

    def _send_payment_link(self, action: Dict) -> Dict:
        """
        Send payment link to customer.
        """
        # This would integrate with payment agent
        logger.info(f"Sending payment link to customer {action.get('customer_id')}")
        return {"status": "success", "message": "Payment link sent"}

    def _schedule_follow_up(self, action: Dict) -> Dict:
        """
        Schedule follow-up call or message.
        """
        logger.info(f"Scheduling follow-up for customer {action.get('customer_id')}")
        return {"status": "success", "message": "Follow-up scheduled"}

    def _escalate_to_human(self, action: Dict) -> Dict:
        """
        Escalate to human agent.
        """
        logger.info(f"Escalating customer {action.get('customer_id')} to human agent")
        return {"status": "success", "message": "Escalated to human agent"}

    def _send_sms_reminder(self, action: Dict) -> Dict:
        """
        Send SMS reminder to customer.
        """
        logger.info(f"Sending SMS reminder to customer {action.get('customer_id')}")
        return {"status": "success", "message": "SMS reminder sent"}

    def analyze_decision_patterns(self, days: int = 30) -> Dict:
        """
        Analyze decision patterns for optimization.
        """
        # This would analyze decision effectiveness in production
        return {
            "total_decisions": 100,
            "successful_outcomes": 75,
            "most_effective_actions": ["send_payment_link", "schedule_follow_up"],
            "least_effective_actions": ["retry_call"],
            "average_resolution_time": "2.5 days",
        }
