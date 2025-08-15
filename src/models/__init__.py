from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

Base = declarative_base()


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    OVERDUE = "overdue"
    DEFAULTED = "defaulted"
    CLOSED = "closed"


class CallStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# SQLAlchemy Models
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    language_preference = Column(String, default="en")
    risk_score = Column(Float, default=0.0)
    status = Column(String, default=CustomerStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loans = relationship("Loan", back_populates="customer")
    interactions = relationship("CustomerInteraction", back_populates="customer")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    loan_amount = Column(Float)
    emi_amount = Column(Float)
    due_date = Column(DateTime)
    next_due_date = Column(DateTime)
    outstanding_amount = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="loans")
    payments = relationship("Payment", back_populates="loan")


class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    call_id = Column(String, unique=True)
    interaction_type = Column(String)  # voice_call, sms, whatsapp
    conversation_log = Column(Text)
    sentiment_score = Column(Float)
    outcome = Column(String)  # payment_made, promised_payment, no_response, etc.
    call_duration = Column(Integer)  # in seconds
    status = Column(String, default=CallStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="interactions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    amount = Column(Float)
    payment_method = Column(String)
    transaction_id = Column(String, unique=True)
    status = Column(String, default=PaymentStatus.PENDING)
    payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("Loan", back_populates="payments")


# Pydantic Models for API
class CustomerBase(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    language_preference: str = "en"


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    risk_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoanBase(BaseModel):
    loan_amount: float
    emi_amount: float
    due_date: datetime
    outstanding_amount: float


class LoanCreate(LoanBase):
    customer_id: int


class LoanResponse(LoanBase):
    id: int
    customer_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    customer_id: int
    interaction_type: str
    conversation_log: Optional[str] = None
    sentiment_score: Optional[float] = None
    outcome: Optional[str] = None
    call_duration: Optional[int] = None


class InteractionResponse(InteractionCreate):
    id: int
    call_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    loan_id: int
    amount: float
    payment_method: str


class PaymentResponse(PaymentCreate):
    id: int
    transaction_id: str
    status: str
    payment_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
