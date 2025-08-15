import os
from typing import Optional


class Settings:
    """Application settings"""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/emi_voicebot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_SECRET_KEY: Optional[str] = None

    # Application
    APP_NAME: str = "EMI VoiceBot System"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # VoiceBot Settings
    VOICE_MODEL: str = "gpt-3.5-turbo"
    TTS_VOICE: str = "nova"
    LANGUAGE_SUPPORT: list = ["en", "hi", "ta", "te", "kn"]

    # Business Rules
    MAX_CALL_ATTEMPTS: int = 3
    PAYMENT_REMINDER_DAYS: list = [7, 3, 1, 0]  # Days before due date


settings = Settings()
