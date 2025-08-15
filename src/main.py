from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from src.utils.database import get_database, create_tables
from src.models import (
    CustomerCreate,
    CustomerResponse,
    LoanCreate,
    LoanResponse,
    InteractionCreate,
    InteractionResponse,
    PaymentCreate,
    PaymentResponse,
)
from src.agents.trigger_agent import TriggerAgent
from src.agents.context_agent import ContextAgent
from src.agents.voicebot_agent import VoiceBotAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.logging_learning_agent import LoggingLearningAgent

# Initialize FastAPI app
app = FastAPI(
    title="EMI VoiceBot System",
    description="Agentic VoiceBots for EMI Collections/Payments",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
trigger_agent = TriggerAgent()
context_agent = ContextAgent()
voicebot_agent = VoiceBotAgent()
decision_agent = DecisionAgent()
payment_agent = PaymentAgent()
logging_agent = LoggingLearningAgent()


@app.on_event("startup")
async def startup_event():
    """Initialize database and system on startup"""
    create_tables()
    logging_agent.log_system_event(
        {
            "event": "system_startup",
            "component": "fastapi_app",
            "severity": "info",
            "message": "EMI VoiceBot system started successfully",
        }
    )


@app.get("/")
async def root():
    return {
        "message": "EMI VoiceBot System API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"database": "connected", "agents": "initialized"},
    }


# Customer Management Endpoints
@app.post("/customers", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate, db: Session = Depends(get_database)
):
    """Create a new customer"""
    from src.models import Customer

    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    logging_agent.log_system_event(
        {
            "event": "customer_created",
            "component": "api",
            "severity": "info",
            "message": f"New customer created: {db_customer.name}",
            "metadata": {"customer_id": db_customer.id},
        }
    )

    return db_customer


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_database)):
    """Get customer by ID"""
    from src.models import Customer

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@app.get("/customers/{customer_id}/context")
async def get_customer_context(customer_id: int):
    """Get comprehensive customer context"""
    try:
        context = context_agent.get_customer_context(customer_id)
        return context
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Loan Management Endpoints
@app.post("/loans", response_model=LoanResponse)
async def create_loan(loan: LoanCreate, db: Session = Depends(get_database)):
    """Create a new loan"""
    from src.models import Loan

    db_loan = Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)

    return db_loan


@app.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: int, db: Session = Depends(get_database)):
    """Get loan by ID"""
    from src.models import Loan

    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    return loan


# VoiceBot Interaction Endpoints
@app.post("/calls/initiate")
async def initiate_call(customer_id: int, background_tasks: BackgroundTasks):
    """Initiate a voice call to customer"""
    try:
        # Get customer context
        customer_context = context_agent.get_customer_context(customer_id)

        # Initiate call
        call_result = voicebot_agent.initiate_call(
            customer_context=customer_context, emi_info={"manual_trigger": True}
        )

        # Log interaction
        logging_agent.log_interaction(
            {
                "customer_id": customer_id,
                "call_id": call_result.get("call_id"),
                "outcome": call_result.get("outcome"),
                "interaction_type": "voice_call",
            }
        )

        return call_result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calls/{call_id}/response")
async def process_customer_response(
    call_id: str, customer_input: str, customer_id: int
):
    """Process customer response during call"""
    try:
        customer_context = context_agent.get_customer_context(customer_id)

        response = voicebot_agent.process_customer_response(
            call_id=call_id, customer_input=customer_input, context=customer_context
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Payment Endpoints
@app.post("/payments/create-link")
async def create_payment_link(
    customer_id: int, loan_id: int, amount: Optional[float] = None
):
    """Create payment link for customer"""
    try:
        customer_context = context_agent.get_customer_context(customer_id)
        loan_info = {"loan_id": loan_id, "emi_amount": amount or 5000}

        payment_link_data = payment_agent.create_payment_link(
            customer_context, loan_info, amount
        )

        logging_agent.log_payment_activity(
            {
                "customer_id": customer_id,
                "payment_id": payment_link_data.get("payment_id"),
                "amount": payment_link_data.get("amount"),
                "status": "link_created",
            }
        )

        return payment_link_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payments/send-link")
async def send_payment_link(customer_id: int, loan_id: int, channel: str = "sms"):
    """Send payment link to customer via SMS or WhatsApp"""
    try:
        customer_context = context_agent.get_customer_context(customer_id)
        loan_info = {"loan_id": loan_id, "emi_amount": 5000}

        # Create payment link
        payment_link_data = payment_agent.create_payment_link(
            customer_context, loan_info
        )

        # Send via preferred channel
        if channel == "sms":
            result = payment_agent.send_payment_link_sms(
                customer_context, payment_link_data
            )
        elif channel == "whatsapp":
            result = payment_agent.send_payment_link_whatsapp(
                customer_context, payment_link_data
            )
        else:
            raise HTTPException(
                status_code=400, detail="Invalid channel. Use 'sms' or 'whatsapp'"
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payments/{payment_id}/verify")
async def verify_payment(payment_id: str, razorpay_payment_id: Optional[str] = None):
    """Verify payment completion"""
    try:
        result = payment_agent.verify_payment(payment_id, razorpay_payment_id)

        logging_agent.log_payment_activity(
            {
                "payment_id": payment_id,
                "status": result.get("status"),
                "amount": result.get("amount"),
            }
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments/{payment_id}/status")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    try:
        return payment_agent.get_payment_status(payment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Trigger and Scheduling Endpoints
@app.post("/triggers/manual")
async def manual_trigger(customer_id: Optional[int] = None):
    """Manually trigger EMI calls"""
    try:
        result = trigger_agent.manual_trigger(customer_id)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/triggers/due-emis")
async def get_due_emis():
    """Get list of EMIs due for calling"""
    try:
        due_emis = trigger_agent.check_due_emis()
        return {"due_emis": due_emis, "count": len(due_emis)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics and Insights Endpoints
@app.get("/analytics/interactions")
async def get_interaction_analytics(days: int = 30):
    """Get interaction analytics"""
    try:
        analytics = logging_agent.analyze_interaction_patterns(days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/payments")
async def get_payment_analytics(days: int = 30):
    """Get payment analytics"""
    try:
        analytics = payment_agent.get_payment_analytics(days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/insights")
async def get_insights_report(days: int = 30):
    """Get comprehensive insights report"""
    try:
        report = logging_agent.generate_insights_report(days)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ML and Learning Endpoints
@app.post("/ml/train-predictor")
async def train_outcome_predictor():
    """Train ML model to predict interaction outcomes"""
    try:
        result = logging_agent.train_outcome_predictor()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ml/predict-outcome")
async def predict_interaction_outcome(customer_id: int):
    """Predict interaction outcome for customer"""
    try:
        customer_context = context_agent.get_customer_context(customer_id)
        prediction = logging_agent.predict_interaction_outcome(customer_context)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin and Management Endpoints
@app.get("/admin/system-status")
async def get_system_status():
    """Get overall system status"""
    return {
        "system": "EMI VoiceBot System",
        "status": "operational",
        "agents": {
            "trigger_agent": "active",
            "context_agent": "active",
            "voicebot_agent": "active",
            "decision_agent": "active",
            "payment_agent": "active",
            "logging_agent": "active",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/admin/customer-segments")
async def get_customer_segments():
    """Get customer segmentation data"""
    try:
        segments = context_agent.get_customer_segments()
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Demo Endpoints
@app.post("/demo/setup-sample-data")
async def setup_sample_data(db: Session = Depends(get_database)):
    """Set up sample data for demo purposes"""
    try:
        from src.models import Customer, Loan

        # Create sample customers
        customers_data = [
            {
                "name": "Rahul Kumar",
                "phone_number": "9876543210",
                "email": "rahul@email.com",
                "language_preference": "hi",
            },
            {
                "name": "Priya Sharma",
                "phone_number": "9876543211",
                "email": "priya@email.com",
                "language_preference": "en",
            },
            {
                "name": "Amit Patel",
                "phone_number": "9876543212",
                "email": "amit@email.com",
                "language_preference": "hi",
            },
        ]

        created_customers = []
        for customer_data in customers_data:
            customer = Customer(**customer_data)
            db.add(customer)
            db.commit()
            db.refresh(customer)
            created_customers.append(customer)

        # Create sample loans
        loans_data = [
            {
                "customer_id": created_customers[0].id,
                "loan_amount": 500000,
                "emi_amount": 15000,
                "outstanding_amount": 400000,
                "due_date": datetime.now(),
                "next_due_date": datetime.now(),
            },
            {
                "customer_id": created_customers[1].id,
                "loan_amount": 300000,
                "emi_amount": 8000,
                "outstanding_amount": 250000,
                "due_date": datetime.now(),
                "next_due_date": datetime.now(),
            },
            {
                "customer_id": created_customers[2].id,
                "loan_amount": 750000,
                "emi_amount": 20000,
                "outstanding_amount": 600000,
                "due_date": datetime.now(),
                "next_due_date": datetime.now(),
            },
        ]

        for loan_data in loans_data:
            loan = Loan(**loan_data)
            db.add(loan)
            db.commit()

        return {
            "status": "success",
            "message": "Sample data created successfully",
            "customers_created": len(created_customers),
            "loans_created": len(loans_data),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/test-workflow")
async def test_demo_workflow():
    """Test the complete workflow with sample data"""
    try:
        # Step 1: Check due EMIs
        due_emis = trigger_agent.check_due_emis()

        if not due_emis:
            return {"message": "No due EMIs found. Please setup sample data first."}

        # Step 2: Get customer context for first due EMI
        customer_id = due_emis[0]["customer_id"]
        customer_context = context_agent.get_customer_context(customer_id)

        # Step 3: Simulate voice call
        call_result = voicebot_agent.initiate_call(customer_context, due_emis[0])

        # Step 4: Create payment link
        loan_info = {"loan_id": 1, "emi_amount": due_emis[0]["emi_amount"]}
        payment_link = payment_agent.create_payment_link(customer_context, loan_info)

        # Step 5: Log everything
        logging_agent.log_interaction(
            {
                "customer_id": customer_id,
                "call_id": call_result.get("call_id"),
                "outcome": call_result.get("outcome"),
                "interaction_type": "demo_workflow",
            }
        )

        return {
            "workflow_status": "completed",
            "due_emis_found": len(due_emis),
            "customer_context": customer_context,
            "call_result": call_result,
            "payment_link": payment_link,
            "next_steps": "Customer can now make payment using the provided link",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo workflow failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
