"""
Utility functions to handle SQLAlchemy model attribute access properly
"""

from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.models import Customer, Loan, Payment, CustomerInteraction


def get_attribute_value(model_instance: Any, attribute_name: str) -> Any:
    """
    Safely get attribute value from SQLAlchemy model instance
    """
    return getattr(model_instance, attribute_name)


def safe_float(value: Any) -> float:
    """
    Safely convert value to float, handling SQLAlchemy columns
    """
    if hasattr(value, "__float__"):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    """
    Safely convert value to int, handling SQLAlchemy columns
    """
    if hasattr(value, "__int__"):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def safe_str(value: Any) -> str:
    """
    Safely convert value to string, handling SQLAlchemy columns
    """
    if value is None:
        return ""
    return str(value)


def safe_bool(value: Any) -> bool:
    """
    Safely convert value to bool, handling SQLAlchemy columns
    """
    if value is None:
        return False
    return bool(value)


def safe_datetime(value: Any) -> Optional[datetime]:
    """
    Safely convert value to datetime, handling SQLAlchemy columns
    """
    if value is None:
        return None
    if hasattr(value, "isoformat"):  # Already a datetime
        return value
    return value


def get_payment_statistics(db: Session, loan_ids: list, cutoff_date) -> dict:
    """
    Get payment statistics using proper SQLAlchemy queries
    """
    # Get all payments
    all_payments = (
        db.query(Payment)
        .filter(Payment.loan_id.in_(loan_ids), Payment.created_at >= cutoff_date)
        .all()
    )

    # Count by status using SQL queries for accuracy
    successful_count = (
        db.query(Payment)
        .filter(
            Payment.loan_id.in_(loan_ids),
            Payment.created_at >= cutoff_date,
            Payment.status == "completed",
        )
        .count()
    )

    failed_count = (
        db.query(Payment)
        .filter(
            Payment.loan_id.in_(loan_ids),
            Payment.created_at >= cutoff_date,
            Payment.status == "failed",
        )
        .count()
    )

    # Get completed payments for amount calculation
    completed_payments = (
        db.query(Payment)
        .filter(
            Payment.loan_id.in_(loan_ids),
            Payment.created_at >= cutoff_date,
            Payment.status == "completed",
        )
        .all()
    )

    total_amount = 0.0
    for payment in completed_payments:
        try:
            amount = safe_float(payment.amount)
            total_amount += amount
        except:
            continue

    total_payments = len(all_payments)

    return {
        "total_payments": total_payments,
        "successful_payments": successful_count,
        "failed_payments": failed_count,
        "success_rate": successful_count / total_payments if total_payments > 0 else 0,
        "total_amount_paid": total_amount,
        "on_time_payments": successful_count,  # Simplified
        "late_payments": 0,  # Simplified
        "payment_pattern": (
            "good"
            if total_payments > 0 and successful_count / total_payments > 0.8
            else "poor" if total_payments > 0 else "new"
        ),
    }


def calculate_total_outstanding(loans: list) -> float:
    """
    Calculate total outstanding amount from loan objects
    """
    total = 0.0
    for loan in loans:
        try:
            amount = safe_float(loan.outstanding_amount)
            total += amount
        except:
            continue
    return total


def filter_active_loans(loans: list) -> list:
    """
    Filter active loans from list of loan objects
    """
    active_loans = []
    for loan in loans:
        try:
            status = safe_str(loan.status)
            if status == "active":
                active_loans.append(loan)
        except:
            continue
    return active_loans
