from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.utils.database import get_db_session
from src.models import Customer, Loan, CustomerInteraction, Payment
from src.utils.model_helpers import (
    get_payment_statistics,
    calculate_total_outstanding,
    filter_active_loans,
    safe_float,
    safe_str,
    safe_int,
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ContextAgent:
    """
    Agent responsible for gathering customer profile, payment history,
    language preference, and risk score.
    """

    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes cache TTL

    def get_customer_context(self, customer_id: int) -> Dict:
        """
        Gather comprehensive customer context including:
        - Customer profile
        - Payment history
        - Risk score
        - Recent interactions
        - Language preference
        """
        # Check cache first
        cache_key = f"customer_context_{customer_id}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]

        db = get_db_session()
        try:
            # Get customer basic info
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError(f"Customer with ID {customer_id} not found")

            # Get loan information
            loans = (
                db.query(Loan)
                .filter(Loan.customer_id == customer_id, Loan.status == "active")
                .all()
            )

            # Get payment history
            payment_history = self._get_payment_history(db, customer_id)

            # Get recent interactions
            recent_interactions = self._get_recent_interactions(db, customer_id)

            # Calculate risk score
            risk_score = self._calculate_risk_score(customer, loans, payment_history)

            # Prepare context
            context = {
                "customer_id": customer.id,
                "name": customer.name,
                "phone_number": customer.phone_number,
                "email": customer.email,
                "language_preference": customer.language_preference,
                "risk_score": risk_score,
                "status": customer.status,
                "loans": [
                    {
                        "loan_id": loan.id,
                        "loan_amount": loan.loan_amount,
                        "emi_amount": loan.emi_amount,
                        "due_date": loan.next_due_date,
                        "outstanding_amount": loan.outstanding_amount,
                        "status": loan.status,
                    }
                    for loan in loans
                ],
                "payment_history": payment_history,
                "recent_interactions": recent_interactions,
                "communication_preferences": self._get_communication_preferences(
                    customer
                ),
                "best_contact_time": self._determine_best_contact_time(
                    recent_interactions
                ),
                "conversation_context": self._build_conversation_context(
                    customer, loans, payment_history
                ),
            }

            # Cache the context
            self._cache_data(cache_key, context)

            return context

        finally:
            db.close()

    def _get_payment_history(
        self, db: Session, customer_id: int, months: int = 6
    ) -> Dict:
        """Get customer's payment history for the last N months"""
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        # Get all loans for the customer
        loan_ids = db.query(Loan.id).filter(Loan.customer_id == customer_id).all()
        loan_ids = [lid[0] for lid in loan_ids]

        # Get payments
        payments = (
            db.query(Payment)
            .filter(Payment.loan_id.in_(loan_ids), Payment.created_at >= cutoff_date)
            .order_by(Payment.payment_date.desc())
            .all()
        )

        # Calculate statistics using helper function
        return get_payment_statistics(db, loan_ids, cutoff_date)

    def _get_recent_interactions(
        self, db: Session, customer_id: int, days: int = 30
    ) -> List[Dict]:
        """Get recent customer interactions"""
        cutoff_date = datetime.now() - timedelta(days=days)

        interactions = (
            db.query(CustomerInteraction)
            .filter(
                CustomerInteraction.customer_id == customer_id,
                CustomerInteraction.created_at >= cutoff_date,
            )
            .order_by(CustomerInteraction.created_at.desc())
            .limit(10)
            .all()
        )

        return [
            {
                "interaction_id": interaction.id,
                "type": interaction.interaction_type,
                "outcome": interaction.outcome,
                "sentiment_score": interaction.sentiment_score,
                "call_duration": interaction.call_duration,
                "date": interaction.created_at,
                "status": interaction.status,
            }
            for interaction in interactions
        ]

    def _calculate_risk_score(
        self, customer: Customer, loans: List[Loan], payment_history: Dict
    ) -> float:
        """Calculate customer risk score (0-100, higher = more risky)"""
        risk_score = 0.0

        # Payment history factor (40% weight)
        payment_factor = 40
        if payment_history["payment_pattern"] == "good":
            risk_score += 10
        elif payment_history["payment_pattern"] == "poor":
            risk_score += 35
        else:  # new customer
            risk_score += 25

        # Outstanding amount factor (30% weight)
        total_outstanding = calculate_total_outstanding(loans)
        if total_outstanding > 100000:  # High outstanding
            risk_score += 25
        elif total_outstanding > 50000:  # Medium outstanding
            risk_score += 15
        else:  # Low outstanding
            risk_score += 5

        # Current status factor (20% weight)
        customer_status = safe_str(customer.status)
        if customer_status == "overdue":
            risk_score += 20
        elif customer_status == "defaulted":
            risk_score += 30
        else:
            risk_score += 5

        # Recent interaction factor (10% weight)
        if payment_history["failed_payments"] > 2:
            risk_score += 10
        elif payment_history["failed_payments"] > 0:
            risk_score += 5

        return min(risk_score, 100.0)  # Cap at 100

    def _get_communication_preferences(self, customer: Customer) -> Dict:
        """Determine customer's communication preferences"""
        return {
            "language": customer.language_preference,
            "preferred_channel": "voice",  # Could be enhanced to track preference
            "timezone": "Asia/Kolkata",  # Could be enhanced based on location
            "formality_level": "polite",  # Could be learned from interactions
        }

    def _determine_best_contact_time(self, recent_interactions: List[Dict]) -> str:
        """Determine best time to contact customer based on interaction history"""
        # Simple logic - could be enhanced with ML
        successful_interactions = [
            i
            for i in recent_interactions
            if i["outcome"] in ["payment_made", "promised_payment"]
        ]

        if successful_interactions:
            # Analyze time patterns from successful interactions
            return "10:00-16:00"  # Business hours
        else:
            return "10:00-12:00"  # Morning preference

    def _build_conversation_context(
        self, customer: Customer, loans: List[Loan], payment_history: Dict
    ) -> str:
        """Build context string for conversation personalization"""
        context_parts = []

        # Customer greeting
        context_parts.append(f"Customer: {customer.name}")

        # Payment pattern
        if payment_history["payment_pattern"] == "good":
            context_parts.append("Good payment history")
        elif payment_history["payment_pattern"] == "poor":
            context_parts.append("Irregular payment pattern")

        # Current dues
        active_loans = filter_active_loans(loans)
        if active_loans:
            total_due = calculate_total_outstanding(active_loans)
            context_parts.append(f"Total outstanding: ₹{total_due:,.2f}")

        return " | ".join(context_parts)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False

        cached_time = self.cache[cache_key]["timestamp"]
        return (datetime.now() - cached_time).seconds < self.cache_ttl

    def _cache_data(self, cache_key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[cache_key] = {"data": data, "timestamp": datetime.now()}

    def update_customer_context(
        self,
        customer_id: int,
        interaction_outcome: str,
        sentiment_score: Optional[float] = None,
    ):
        """Update customer context after an interaction"""
        # Invalidate cache
        cache_key = f"customer_context_{customer_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]

        # Log the update
        logger.info(
            f"Updated context for customer {customer_id}: {interaction_outcome}"
        )

    def get_customer_segments(self) -> Dict[str, List[int]]:
        """Segment customers based on risk and behavior"""
        db = get_db_session()
        try:
            customers = db.query(Customer).all()
            segments = {"high_risk": [], "medium_risk": [], "low_risk": [], "vip": []}

            for customer in customers:
                context = self.get_customer_context(safe_int(customer.id))
                risk_score = context["risk_score"]

                if risk_score > 70:
                    segments["high_risk"].append(customer.id)
                elif risk_score > 40:
                    segments["medium_risk"].append(customer.id)
                else:
                    segments["low_risk"].append(customer.id)

                # VIP customers (good payment history + high loan amounts)
                if (
                    context["payment_history"]["payment_pattern"] == "good"
                    and sum([loan["loan_amount"] for loan in context["loans"]]) > 500000
                ):
                    segments["vip"].append(customer.id)

            return segments

        finally:
            db.close()
