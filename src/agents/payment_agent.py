import razorpay
from twilio.rest import Client
import requests
from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime, timedelta
from sqlalchemy import update
from src.models import Payment, Loan
from src.utils.database import get_db_session
from src.utils.model_helpers import safe_float, safe_str, safe_datetime, safe_int
import json

logger = logging.getLogger(__name__)


class PaymentAgent:
    """
    Agent responsible for sending secure payment links and confirming transactions.
    Integrates with payment gateways and messaging services.
    """

    def __init__(self):
        self.razorpay_client = None  # Initialize when needed
        self.twilio_client = None  # Initialize when needed

        # Payment methods configuration
        self.payment_methods = {
            "upi": {"enabled": True, "fee": 0},
            "netbanking": {"enabled": True, "fee": 0},
            "card": {"enabled": True, "fee": 0},
            "wallet": {"enabled": True, "fee": 0},
        }

        # Message templates
        self.message_templates = {
            "en": {
                "payment_link": "Hi {name}, your EMI payment link: {link}. Amount: ₹{amount}. Due: {due_date}. Pay securely now.",
                "payment_success": "Thank you {name}! Your EMI payment of ₹{amount} has been successfully processed. Transaction ID: {txn_id}",
                "payment_failed": "Hi {name}, your payment of ₹{amount} could not be processed. Please try again or contact support.",
                "payment_reminder": "Reminder: Your EMI of ₹{amount} is due on {due_date}. Pay now: {link}",
            },
            "hi": {
                "payment_link": "नमस्ते {name}, आपका EMI भुगतान लिंक: {link}। राशि: ₹{amount}। देय तिथि: {due_date}। अभी सुरक्षित भुगतान करें।",
                "payment_success": "धन्यवाद {name}! आपका ₹{amount} का EMI भुगतान सफलतापूर्वक प्रोसेस हो गया है। लेनदेन ID: {txn_id}",
                "payment_failed": "नमस्ते {name}, आपका ₹{amount} का भुगतान प्रोसेस नहीं हो सका। कृपया पुनः प्रयास करें या सहायता से संपर्क करें।",
                "payment_reminder": "अनुस्मारक: आपकी ₹{amount} की EMI {due_date} को देय है। अभी भुगतान करें: {link}",
            },
        }

    def create_payment_link(
        self,
        customer_context: Dict,
        loan_info: Dict,
        custom_amount: Optional[float] = None,
    ) -> Dict:
        """
        Create a secure payment link for the customer.
        """
        try:
            # Determine payment amount
            amount = custom_amount or loan_info.get("emi_amount", 0)

            # Generate unique payment ID
            payment_id = str(uuid.uuid4())

            # For demo purposes, simulate payment link creation
            # In production, this would integrate with actual payment gateway
            payment_link_data = self._simulate_razorpay_payment_link(
                customer_context, amount, payment_id
            )

            # Store payment record
            loan_id = (
                loan_info.get("loan_id", 0)
                if isinstance(loan_info.get("loan_id"), int)
                else 0
            )
            payment_record = self._create_payment_record(
                loan_id, amount, payment_id, "payment_link"
            )

            return {
                "payment_id": payment_id,
                "payment_link": payment_link_data["short_url"],
                "amount": amount,
                "currency": "INR",
                "expires_at": payment_link_data["expires_at"],
                "status": "created",
                "payment_methods": list(self.payment_methods.keys()),
            }

        except Exception as e:
            logger.error(f"Error creating payment link: {str(e)}")
            return {"error": "Failed to create payment link", "details": str(e)}

    def _simulate_razorpay_payment_link(
        self, customer_context: Dict, amount: float, payment_id: str
    ) -> Dict:
        """
        Simulate Razorpay payment link creation.
        In production, this would use actual Razorpay API.
        """
        # Simulate API call to Razorpay
        return {
            "id": f"plink_{payment_id[:8]}",
            "short_url": f"https://rzp.io/l/{payment_id[:8]}",
            "amount": int(amount * 100),  # Razorpay uses paise
            "currency": "INR",
            "expires_at": int((datetime.now().timestamp() + 86400) * 1000),  # 24 hours
            "status": "created",
            "customer": {
                "name": customer_context["name"],
                "contact": customer_context["phone_number"],
                "email": customer_context.get("email"),
            },
        }

    def send_payment_link_sms(
        self,
        customer_context: Dict,
        payment_link_data: Dict,
        due_date: Optional[str] = None,
    ) -> Dict:
        """
        Send payment link via SMS to customer.
        """
        try:
            language = customer_context.get("language_preference", "en")
            templates = self.message_templates.get(
                language, self.message_templates["en"]
            )

            message = templates["payment_link"].format(
                name=customer_context["name"],
                link=payment_link_data["payment_link"],
                amount=payment_link_data["amount"],
                due_date=due_date or "soon",
            )

            # For demo purposes, simulate SMS sending
            sms_result = self._simulate_sms_send(
                customer_context["phone_number"], message
            )

            return {
                "status": "sent",
                "message_id": sms_result["sid"],
                "to": customer_context["phone_number"],
                "message": message,
            }

        except Exception as e:
            logger.error(f"Error sending payment link SMS: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def send_payment_link_whatsapp(
        self, customer_context: Dict, payment_link_data: Dict
    ) -> Dict:
        """
        Send payment link via WhatsApp to customer.
        """
        try:
            language = customer_context.get("language_preference", "en")
            templates = self.message_templates.get(
                language, self.message_templates["en"]
            )

            message = templates["payment_link"].format(
                name=customer_context["name"],
                link=payment_link_data["payment_link"],
                amount=payment_link_data["amount"],
                due_date="soon",
            )

            # For demo purposes, simulate WhatsApp sending
            whatsapp_result = self._simulate_whatsapp_send(
                customer_context["phone_number"], message
            )

            return {
                "status": "sent",
                "message_id": whatsapp_result["sid"],
                "to": f"whatsapp:+91{customer_context['phone_number']}",
                "message": message,
            }

        except Exception as e:
            logger.error(f"Error sending payment link WhatsApp: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def _simulate_sms_send(self, phone_number: str, message: str) -> Dict:
        """
        Simulate SMS sending via Twilio.
        """
        return {
            "sid": f"SM{uuid.uuid4().hex[:8]}",
            "status": "queued",
            "to": phone_number,
            "body": message,
        }

    def _simulate_whatsapp_send(self, phone_number: str, message: str) -> Dict:
        """
        Simulate WhatsApp message sending via Twilio.
        """
        return {
            "sid": f"WA{uuid.uuid4().hex[:8]}",
            "status": "queued",
            "to": f"whatsapp:+91{phone_number}",
            "body": message,
        }

    def verify_payment(
        self,
        payment_id: str,
        razorpay_payment_id: Optional[str] = None,
        razorpay_signature: Optional[str] = None,
    ) -> Dict:
        """
        Verify payment completion and update records.
        """
        db = None
        try:
            db = get_db_session()

            # Find payment record
            payment = (
                db.query(Payment).filter(Payment.transaction_id == payment_id).first()
            )

            if not payment:
                return {"status": "error", "message": "Payment record not found"}

            # For demo purposes, simulate payment verification
            # In production, this would verify with Razorpay
            verification_result = self._simulate_payment_verification(
                payment_id, razorpay_payment_id
            )

            if verification_result["status"] == "success":
                # Update payment record using SQLAlchemy update
                db.execute(
                    update(Payment)
                    .where(Payment.id == payment.id)
                    .values(status="completed", payment_date=datetime.utcnow())
                )
                db.commit()

                # Update loan outstanding amount
                self._update_loan_outstanding(
                    safe_int(payment.loan_id), safe_float(payment.amount)
                )

                # Send confirmation message
                confirmation_result = self._send_payment_confirmation(payment)

                return {
                    "status": "success",
                    "payment_id": payment_id,
                    "amount": safe_float(payment.amount),
                    "transaction_date": datetime.utcnow().isoformat(),
                    "confirmation_sent": confirmation_result["status"] == "sent",
                }
            else:
                # Update payment as failed
                db.execute(
                    update(Payment)
                    .where(Payment.id == payment.id)
                    .values(status="failed")
                )
                db.commit()

                return {
                    "status": "failed",
                    "payment_id": payment_id,
                    "reason": verification_result.get(
                        "reason", "Payment verification failed"
                    ),
                }

        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if db is not None:
                db.close()

    def _simulate_payment_verification(
        self, payment_id: str, razorpay_payment_id: Optional[str] = None
    ) -> Dict:
        """
        Simulate payment verification with Razorpay.
        """
        # For demo, randomly simulate success/failure
        import random

        if random.random() > 0.1:  # 90% success rate
            return {
                "status": "success",
                "razorpay_payment_id": razorpay_payment_id
                or f"pay_{uuid.uuid4().hex[:8]}",
                "method": "upi",
            }
        else:
            return {"status": "failed", "reason": "Insufficient funds"}

    def _create_payment_record(
        self, loan_id: int, amount: float, transaction_id: str, payment_method: str
    ) -> Payment:
        """
        Create payment record in database.
        """
        db = get_db_session()
        try:
            payment = Payment(
                loan_id=loan_id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            return payment
        finally:
            db.close()

    def _update_loan_outstanding(self, loan_id: int, payment_amount: float):
        """
        Update loan outstanding amount after successful payment.
        """
        db = get_db_session()
        try:
            loan = db.query(Loan).filter(Loan.id == loan_id).first()
            if loan:
                current_outstanding = safe_float(loan.outstanding_amount)
                new_outstanding = max(0, current_outstanding - payment_amount)

                db.execute(
                    update(Loan)
                    .where(Loan.id == loan_id)
                    .values(outstanding_amount=new_outstanding)
                )
                db.commit()
        except Exception as e:
            logger.error(f"Error updating loan outstanding: {str(e)}")
        finally:
            db.close()

    def _send_payment_confirmation(self, payment: Payment) -> Dict:
        """
        Send payment confirmation message to customer.
        """
        db = None
        try:
            # Get customer details
            db = get_db_session()
            loan = db.query(Loan).filter(Loan.id == payment.loan_id).first()
            customer = loan.customer if loan else None

            if not customer:
                return {"status": "failed", "reason": "Customer not found"}

            language = customer.language_preference or "en"
            templates = self.message_templates.get(
                language, self.message_templates["en"]
            )

            message = templates["payment_success"].format(
                name=customer.name, amount=payment.amount, txn_id=payment.transaction_id
            )

            # Send confirmation SMS
            sms_result = self._simulate_sms_send(customer.phone_number, message)

            return {"status": "sent", "message_id": sms_result["sid"]}

        except Exception as e:
            logger.error(f"Error sending payment confirmation: {str(e)}")
            return {"status": "failed", "error": str(e)}
        finally:
            if db is not None:
                db.close()

    def send_payment_reminder_sms(
        self, customer_context: Dict, loan_info: Dict, due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send payment reminder to customer.
        """
        try:
            # Create payment link
            payment_link_data = self.create_payment_link(customer_context, loan_info)

            if "error" in payment_link_data:
                return payment_link_data

            language = customer_context.get("language_preference", "en")
            templates = self.message_templates.get(
                language, self.message_templates["en"]
            )

            # Calculate days until due
            days_until_due = 1  # Default to urgent for demo
            if due_date:
                try:
                    due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    days_until_due = (due_dt - datetime.utcnow()).days
                except:
                    days_until_due = 1

            message = templates["payment_reminder"].format(
                name=customer_context["name"],
                amount=loan_info.get("emi_amount", 0),
                due_date=loan_info.get("due_date", "soon"),
                link=payment_link_data["payment_link"],
            )

            # Send reminder via preferred channel
            if days_until_due <= 1:
                # Urgent - send both SMS and WhatsApp
                sms_result = self._simulate_sms_send(
                    customer_context["phone_number"], message
                )
                whatsapp_result = self._simulate_whatsapp_send(
                    customer_context["phone_number"], message
                )

                return {
                    "status": "sent",
                    "channels": ["sms", "whatsapp"],
                    "sms_id": sms_result["sid"],
                    "whatsapp_id": whatsapp_result["sid"],
                }
            else:
                # Normal reminder - SMS only
                sms_result = self._simulate_sms_send(
                    customer_context["phone_number"], message
                )

                return {
                    "status": "sent",
                    "channels": ["sms"],
                    "sms_id": sms_result["sid"],
                }

        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def get_payment_status(self, payment_id: str) -> Dict:
        """
        Get current status of a payment.
        """
        db = get_db_session()
        try:
            payment = (
                db.query(Payment).filter(Payment.transaction_id == payment_id).first()
            )

            if not payment:
                return {"status": "not_found", "message": "Payment not found"}

            payment_date_value = safe_datetime(payment.payment_date)

            return {
                "payment_id": payment_id,
                "status": safe_str(payment.status),
                "amount": safe_float(payment.amount),
                "payment_method": safe_str(payment.payment_method),
                "created_at": payment.created_at.isoformat(),
                "payment_date": (
                    payment_date_value.isoformat()
                    if payment_date_value and hasattr(payment_date_value, "isoformat")
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def get_payment_analytics(self, days: int = 30) -> Dict:
        """
        Get payment analytics for the specified period.
        """
        db = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            payments = db.query(Payment).filter(Payment.created_at >= cutoff_date).all()

            total_payments = len(payments)
            successful_payments = len(
                [p for p in payments if safe_str(p.status) == "completed"]
            )
            failed_payments = len(
                [p for p in payments if safe_str(p.status) == "failed"]
            )
            pending_payments = len(
                [p for p in payments if safe_str(p.status) == "pending"]
            )

            total_amount = sum(
                [
                    safe_float(p.amount)
                    for p in payments
                    if safe_str(p.status) == "completed"
                ]
            )

            # Payment method distribution
            method_distribution = {}
            for payment in payments:
                method = safe_str(payment.payment_method)
                method_distribution[method] = method_distribution.get(method, 0) + 1

            return {
                "period_days": days,
                "total_payments": total_payments,
                "successful_payments": successful_payments,
                "failed_payments": failed_payments,
                "pending_payments": pending_payments,
                "success_rate": (
                    successful_payments / total_payments if total_payments > 0 else 0
                ),
                "total_amount_collected": total_amount,
                "payment_method_distribution": method_distribution,
                "average_payment_amount": (
                    total_amount / successful_payments if successful_payments > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting payment analytics: {str(e)}")
            return {"error": "Failed to get analytics", "details": str(e)}
        finally:
            db.close()
