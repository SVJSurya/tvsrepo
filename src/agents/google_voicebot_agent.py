import google.generativeai as genai
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from src.models import CustomerInteraction
from src.utils.database import get_db_session
from src.agents.decision_agent import DecisionAgent
import os
import uuid

logger = logging.getLogger(__name__)


class GoogleVoiceBotAgent:
    """
    Agent responsible for conducting multilingual, dynamic conversations
    with customers regarding EMI payments using Google Gemini API (FREE).
    """

    def __init__(self):
        # Initialize Google Gemini (FREE API)
        api_key = os.getenv("GOOGLE_API_KEY", "your_google_api_key_here")
        if api_key and api_key != "your_google_api_key_here":
            try:
                genai.configure(api_key=api_key)  # type: ignore
                # Use gemini-1.5-flash for free tier (faster and free)
                self.model = genai.GenerativeModel("gemini-1.5-flash")  # type: ignore
                self.gemini_available = True
                logger.info("Google Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Google Gemini API initialization failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            logger.warning(
                "Google Gemini API not configured - using rule-based responses"
            )

        self.decision_agent = DecisionAgent()

        # Conversation templates by language (fallback for when API is not available)
        self.conversation_templates = {
            "en": {
                "greeting": "Hello {name}, this is an automated call from your financial institution regarding your EMI payment.",
                "emi_reminder": "Your EMI of ₹{amount} is due on {date}. Would you like to make the payment now?",
                "payment_confirmation": "Thank you! I'll send you the payment link via SMS. Please complete the payment within 24 hours.",
                "extension_offer": "I understand your situation. We can offer a {days}-day extension with a fee of ₹{fee}. Would this help?",
                "callback_schedule": "I'll schedule a callback for {date} at {time}. Is this convenient for you?",
                "escalation": "I'm transferring your call to our customer service team for further assistance.",
                "closing": "Thank you for your time. Have a great day!",
                "payment_options": "You can pay via UPI, net banking, or visit our nearest branch. Which option would you prefer?",
                "partial_payment": "Would you like to make a partial payment of ₹{amount} today and schedule the remaining amount?",
                "payment_difficulty": "I understand you're facing financial difficulties. Let me check what assistance programs are available for you.",
            },
            "hi": {
                "greeting": "नमस्ते {name}, यह आपकी EMI भुगतान के संबंध में आपकी वित्तीय संस्था से एक स्वचालित कॉल है।",
                "emi_reminder": "आपकी ₹{amount} की EMI {date} तक देय है। क्या आप अभी भुगतान करना चाहेंगे?",
                "payment_confirmation": "धन्यवाद! मैं आपको SMS के माध्यम से भुगतान लिंक भेजूंगा। कृपया 24 घंटे के भीतर भुगतान पूरा करें।",
                "extension_offer": "मैं आपकी स्थिति समझता हूं। हम ₹{fee} शुल्क के साथ {days} दिन का विस्तार दे सकते हैं। क्या यह मदद करेगा?",
                "callback_schedule": "मैं {date} को {time} बजे कॉलबैक शेड्यूल करूंगा। क्या यह आपके लिए सुविधाजनक है?",
                "escalation": "मैं आपकी कॉल को आगे की सहायता के लिए हमारी ग्राहक सेवा टीम को स्थानांतरित कर रहा हूं।",
                "closing": "आपके समय के लिए धन्यवाद। आपका दिन शुभ हो!",
                "payment_options": "आप UPI, नेट बैंकिंग के माध्यम से भुगतान कर सकते हैं या हमारी निकटतम शाखा में जा सकते हैं। आप कौन सा विकल्प पसंद करेंगे?",
                "partial_payment": "क्या आप आज ₹{amount} का आंशिक भुगतान करना चाहेंगे और शेष राशि को शेड्यूल करना चाहेंगे?",
                "payment_difficulty": "मैं समझता हूं कि आप वित्तीय कठिनाइयों का सामना कर रहे हैं। मुझे देखने दें कि आपके लिए कौन से सहायता कार्यक्रम उपलब्ध हैं।",
            },
        }

        # Response patterns for rule-based fallback
        self.response_patterns = {
            "payment_request": ["pay", "payment", "money", "amount", "due"],
            "extension_request": ["extension", "delay", "postpone", "later", "extend"],
            "help_request": ["help", "assist", "support", "problem", "issue"],
            "callback_request": ["callback", "call back", "later", "busy"],
            "difficulty": ["difficult", "problem", "can't", "unable", "financial"],
            "confirmation": ["yes", "ok", "sure", "agree", "proceed"],
            "denial": ["no", "not now", "refuse", "cannot", "won't"],
        }

    def analyze_call(
        self,
        call_type: str,
        user_input: str,
        customer_context: Optional[Dict] = None,
        conversation_history: Optional[List] = None,
    ) -> Dict:
        """
        Analyze customer call and generate appropriate response.
        Uses Google Gemini if available, falls back to rule-based responses.
        """
        try:
            if self.gemini_available:
                return self._analyze_with_gemini(
                    call_type, user_input, customer_context, conversation_history
                )
            else:
                return self._analyze_with_rules(call_type, user_input, customer_context)
        except Exception as e:
            logger.error(f"Error in call analysis: {e}")
            return self._get_fallback_response(user_input, customer_context)

    def _analyze_with_gemini(
        self,
        call_type: str,
        user_input: str,
        customer_context: Optional[Dict] = None,
        conversation_history: Optional[List] = None,
    ) -> Dict:
        """
        Use Google Gemini AI for intelligent conversation analysis.
        """
        try:
            # Prepare context for Gemini
            context = self._prepare_context_for_ai(customer_context)

            # Prepare conversation history
            history_text = ""
            if conversation_history and len(conversation_history) > 0:
                history_text = "\n\nConversation History:\n"
                for i, exchange in enumerate(
                    conversation_history[-5:], 1
                ):  # Last 5 exchanges
                    history_text += f"{i}. Customer: {exchange.get('user_input', '')}\n"
                    history_text += f"   Agent: {exchange.get('ai_response', '')}\n"

            prompt = f"""
            You are an EMI collection agent helping customers with loan payments. 
            
            Customer Context:
            {json.dumps(context, indent=2)}
            {history_text}
            
            Customer's Current Input: "{user_input}"
            
            Please provide a helpful, empathetic response that:
            1. ACKNOWLEDGES the conversation history and context
            2. RESPONDS SPECIFICALLY to the customer's current input
            3. Offers appropriate next steps based on the conversation flow
            4. Maintains continuity from previous exchanges
            5. Follows banking compliance guidelines
            
            If this is a follow-up to previous questions or offers, reference them naturally.
            
            Respond in JSON format:
            {{
                "response": "Your contextual response here",
                "intent": "payment_request|extension_request|help_request|callback_request|follow_up|other",
                "sentiment": "positive|neutral|negative",
                "next_action": "send_payment_link|schedule_callback|offer_extension|escalate|continue_conversation",
                "confidence": 0.95
            }}
            """

            response = self.model.generate_content(prompt)

            # Clean and parse AI response
            try:
                response_text = response.text.strip()

                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = (
                        response_text.replace("```json", "").replace("```", "").strip()
                    )
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()

                ai_result = json.loads(response_text)
                return {
                    "response": ai_result.get(
                        "response", "I understand. Let me help you with that."
                    ),
                    "intent": ai_result.get("intent", "other"),
                    "sentiment": ai_result.get("sentiment", "neutral"),
                    "next_action": ai_result.get(
                        "next_action", "continue_conversation"
                    ),
                    "confidence": ai_result.get("confidence", 0.8),
                    "ai_powered": True,
                }
            except json.JSONDecodeError as json_error:
                logger.warning(
                    f"JSON parsing failed: {json_error}. Raw response: {response.text}"
                )
                # If JSON parsing fails, extract response text
                return {
                    "response": response.text.strip(),
                    "intent": "other",
                    "sentiment": "neutral",
                    "next_action": "continue_conversation",
                    "confidence": 0.7,
                    "ai_powered": True,
                }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback to rule-based
            return self._analyze_with_rules(call_type, user_input, customer_context)

    def _analyze_with_rules(
        self, call_type: str, user_input: str, customer_context: Dict = None
    ) -> Dict:
        """
        Rule-based conversation analysis for when AI is not available.
        """
        user_input_lower = user_input.lower()
        intent = "other"
        response = "I understand. Let me help you with that."
        next_action = "continue_conversation"

        # Detect intent based on keywords
        for pattern_type, keywords in self.response_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                intent = pattern_type
                break

        # Generate appropriate response based on intent
        if intent == "payment_request":
            response = "I can help you make the payment right away. I'll send you a secure payment link via SMS."
            next_action = "send_payment_link"
        elif intent == "extension_request":
            response = "I understand you need more time. We can offer a 15-day extension for a small fee of ₹150. Would that work for you?"
            next_action = "offer_extension"
        elif intent == "help_request":
            response = "I'm here to help! You can make payments, request extensions, or get account information. What would you like to do?"
            next_action = "continue_conversation"
        elif intent == "callback_request":
            response = "I'll schedule a callback for you. When would be a convenient time to call you back?"
            next_action = "schedule_callback"
        elif intent == "difficulty":
            response = "I understand you're facing difficulties. Let me check what assistance options are available for you."
            next_action = "escalate"
        elif intent == "confirmation":
            response = "Great! I'll proceed with that for you right away."
            next_action = "send_payment_link"
        elif intent == "denial":
            response = "I understand. Is there anything else I can help you with today?"
            next_action = "continue_conversation"

        return {
            "response": response,
            "intent": intent,
            "sentiment": "neutral",
            "next_action": next_action,
            "confidence": 0.8,
            "ai_powered": False,
        }

    def _prepare_context_for_ai(self, customer_context: Dict = None) -> Dict:
        """
        Prepare customer context for AI processing.
        """
        if not customer_context:
            return {"status": "new_customer"}

        return {
            "name": customer_context.get("name", "Customer"),
            "emi_amount": customer_context.get("emi_amount", 0),
            "due_date": customer_context.get("due_date", ""),
            "risk_score": customer_context.get("risk_score", 50),
            "previous_interactions": customer_context.get("interaction_count", 0),
        }

    def _get_fallback_response(
        self, user_input: str, customer_context: Dict = None
    ) -> Dict:
        """
        Ultimate fallback response for error conditions.
        """
        return {
            "response": "Thank you for calling. I'm here to help with your EMI payment. How can I assist you today?",
            "intent": "greeting",
            "sentiment": "neutral",
            "next_action": "continue_conversation",
            "confidence": 0.5,
            "ai_powered": False,
        }

    def get_template_response(
        self, template_key: str, language: str = "en", **kwargs
    ) -> str:
        """
        Get a templated response in the specified language.
        """
        templates = self.conversation_templates.get(
            language, self.conversation_templates["en"]
        )
        template = templates.get(template_key, templates["greeting"])
        return template.format(**kwargs)

    def generate_multilingual_response(
        self, intent: str, customer_context: Dict, language: str = "en"
    ) -> str:
        """
        Generate response in customer's preferred language.
        """
        name = customer_context.get("name", "Customer")
        amount = customer_context.get("emi_amount", 0)
        due_date = customer_context.get("due_date", "soon")

        if intent == "greeting":
            return self.get_template_response("greeting", language, name=name)
        elif intent == "emi_reminder":
            return self.get_template_response(
                "emi_reminder", language, name=name, amount=amount, date=due_date
            )
        elif intent == "payment_confirmation":
            return self.get_template_response("payment_confirmation", language)
        else:
            return self.get_template_response("greeting", language, name=name)
