import openai
from twilio.rest import Client
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from src.models import CustomerInteraction
from src.utils.database import get_db_session
from src.agents.decision_agent import DecisionAgent
import uuid

logger = logging.getLogger(__name__)


class VoiceBotAgent:
    """
    Agent responsible for conducting multilingual, dynamic conversations
    with customers regarding EMI payments.
    """

    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.twilio_client = None  # Will initialize when needed
        self.decision_agent = DecisionAgent()

        # Conversation templates by language
        self.conversation_templates = {
            "en": {
                "greeting": "Hello {name}, this is an automated call from your financial institution regarding your EMI payment.",
                "emi_reminder": "Your EMI of ₹{amount} is due on {date}. Would you like to make the payment now?",
                "payment_options": "You can pay through our secure payment link, UPI, or net banking. Which option would you prefer?",
                "closing": "Thank you for your time. Have a great day!",
            },
            "hi": {
                "greeting": "नमस्ते {name}, यह आपकी वित्तीय संस्था से EMI भुगतान के संबंध में एक स्वचालित कॉल है।",
                "emi_reminder": "आपकी ₹{amount} की EMI {date} को देय है। क्या आप अभी भुगतान करना चाहेंगे?",
                "payment_options": "आप हमारे सुरक्षित भुगतान लिंक, UPI, या नेट बैंकिंग के माध्यम से भुगतान कर सकते हैं। आप कौन सा विकल्प पसंद करेंगे?",
                "closing": "आपके समय के लिए धन्यवाद। आपका दिन शुभ हो!",
            },
        }

        # Conversation states
        self.conversation_states = {
            "GREETING": "greeting",
            "EMI_DISCUSSION": "emi_discussion",
            "PAYMENT_INQUIRY": "payment_inquiry",
            "PAYMENT_PROCESSING": "payment_processing",
            "CLOSING": "closing",
        }

    def initiate_call(self, customer_context: Dict, emi_info: Dict) -> Dict:
        """
        Initiate a voice call to the customer.
        For demo purposes, this will simulate the call process.
        """
        call_id = str(uuid.uuid4())

        try:
            # Create interaction record
            interaction = self._create_interaction_record(
                customer_context["customer_id"], call_id, "voice_call"
            )

            # For demo, simulate the conversation instead of actual call
            conversation_result = self._simulate_conversation(
                customer_context, emi_info
            )

            # Update interaction with results
            self._update_interaction_record(
                call_id,
                conversation_result["conversation_log"],
                conversation_result["outcome"],
                conversation_result["sentiment_score"],
                conversation_result["call_duration"],
            )

            # Make decision based on conversation outcome
            decision = self.decision_agent.make_decision(
                conversation_result, customer_context
            )

            return {
                "call_id": call_id,
                "status": "completed",
                "outcome": conversation_result["outcome"],
                "next_action": decision["next_action"],
                "conversation_summary": conversation_result["summary"],
            }

        except Exception as e:
            logger.error(f"Error in call initiation: {str(e)}")
            return {"call_id": call_id, "status": "failed", "error": str(e)}

    def _simulate_conversation(self, customer_context: Dict, emi_info: Dict) -> Dict:
        """
        Simulate a conversation with the customer.
        In production, this would be replaced with actual voice interaction.
        """
        language = customer_context.get("language_preference", "en")
        templates = self.conversation_templates.get(
            language, self.conversation_templates["en"]
        )

        # Build conversation context for AI
        context_prompt = self._build_conversation_prompt(
            customer_context, emi_info, language
        )

        # Simulate customer responses based on their profile
        customer_response_type = self._determine_customer_response_type(
            customer_context
        )

        conversation_log = []
        conversation_log.append(
            f"Bot: {templates['greeting'].format(name=customer_context['name'])}"
        )

        # EMI reminder
        if emi_info.get("emi_amount"):
            emi_message = templates["emi_reminder"].format(
                amount=emi_info["emi_amount"], date=emi_info.get("due_date", "soon")
            )
            conversation_log.append(f"Bot: {emi_message}")

        # Simulate customer response
        if customer_response_type == "cooperative":
            conversation_log.append(
                "Customer: Yes, I would like to make the payment now."
            )
            conversation_log.append(f"Bot: {templates['payment_options']}")
            conversation_log.append(
                "Customer: I'll use UPI. Please send me the payment link."
            )
            outcome = "payment_requested"
            sentiment_score = 0.8

        elif customer_response_type == "hesitant":
            conversation_log.append(
                "Customer: I'm having some financial difficulties. Can I pay in a few days?"
            )
            conversation_log.append(
                "Bot: I understand your situation. When would be a good time for you to make the payment?"
            )
            conversation_log.append("Customer: Maybe by the end of this week.")
            outcome = "promised_payment"
            sentiment_score = 0.3

        elif customer_response_type == "unavailable":
            conversation_log.append("Customer: I'm busy right now. Can you call later?")
            conversation_log.append(
                "Bot: Of course. When would be a convenient time to call you back?"
            )
            conversation_log.append("Customer: Tomorrow evening would be better.")
            outcome = "reschedule_requested"
            sentiment_score = 0.1

        else:  # non_responsive
            conversation_log.append("Customer: [No clear response or hung up]")
            outcome = "no_response"
            sentiment_score = -0.2

        conversation_log.append(f"Bot: {templates['closing']}")

        # Generate AI-powered conversation summary
        summary = self._generate_conversation_summary(
            conversation_log, customer_context
        )

        return {
            "conversation_log": "\n".join(conversation_log),
            "outcome": outcome,
            "sentiment_score": sentiment_score,
            "call_duration": len(conversation_log) * 10,  # Simulate duration
            "summary": summary,
        }

    def _determine_customer_response_type(self, customer_context: Dict) -> str:
        """
        Determine likely customer response based on their profile.
        """
        risk_score = customer_context.get("risk_score", 50)
        payment_pattern = customer_context.get("payment_history", {}).get(
            "payment_pattern", "new"
        )

        if payment_pattern == "good" and risk_score < 30:
            return "cooperative"
        elif payment_pattern == "good" and risk_score < 60:
            return "hesitant"
        elif risk_score > 70:
            return "non_responsive"
        else:
            return "hesitant"

    def _build_conversation_prompt(
        self, customer_context: Dict, emi_info: Dict, language: str
    ) -> str:
        """
        Build AI prompt for conversation generation.
        """
        prompt = f"""
        You are an AI assistant for EMI collection calls. 
        Customer: {customer_context['name']}
        Language: {language}
        Risk Score: {customer_context.get('risk_score', 'unknown')}
        Payment History: {customer_context.get('payment_history', {}).get('payment_pattern', 'unknown')}
        
        Be polite, professional, and helpful. Focus on finding a solution that works for both the customer and the institution.
        """
        return prompt

    def _generate_conversation_summary(
        self, conversation_log: List[str], customer_context: Dict
    ) -> str:
        """
        Generate AI-powered summary of the conversation.
        """
        try:
            prompt = f"""
            Summarize the following EMI collection call conversation in 2-3 sentences:
            
            Customer: {customer_context['name']}
            Conversation:
            {' '.join(conversation_log)}
            
            Focus on the outcome and customer's response.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
            )

            content = response.choices[0].message.content
            return content.strip() if content else "Conversation completed."

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return (
                "Conversation completed. Customer was contacted regarding EMI payment."
            )

    def _create_interaction_record(
        self, customer_id: int, call_id: str, interaction_type: str
    ) -> CustomerInteraction:
        """
        Create a new customer interaction record.
        """
        db = get_db_session()
        try:
            interaction = CustomerInteraction(
                customer_id=customer_id,
                call_id=call_id,
                interaction_type=interaction_type,
                status="in_progress",
                created_at=datetime.utcnow(),
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            return interaction
        finally:
            db.close()

    def _update_interaction_record(
        self,
        call_id: str,
        conversation_log: str,
        outcome: str,
        sentiment_score: float,
        call_duration: int,
    ):
        """
        Update interaction record with conversation results.
        """
        db = get_db_session()
        try:
            interaction = (
                db.query(CustomerInteraction)
                .filter(CustomerInteraction.call_id == call_id)
                .first()
            )

            if interaction:
                # Update using SQLAlchemy's update method
                db.query(CustomerInteraction).filter(
                    CustomerInteraction.call_id == call_id
                ).update(
                    {
                        "conversation_log": conversation_log,
                        "outcome": outcome,
                        "sentiment_score": sentiment_score,
                        "call_duration": call_duration,
                        "status": "completed",
                    }
                )
                db.commit()

        except Exception as e:
            logger.error(f"Error updating interaction record: {str(e)}")
        finally:
            db.close()

    def process_customer_response(
        self, call_id: str, customer_input: str, context: Dict
    ) -> Dict:
        """
        Process customer response during an ongoing call.
        """
        try:
            # Use AI to understand customer intent
            intent_analysis = self._analyze_customer_intent(customer_input, context)

            # Generate appropriate response
            bot_response = self._generate_bot_response(intent_analysis, context)

            return {
                "bot_response": bot_response,
                "detected_intent": intent_analysis["intent"],
                "confidence": intent_analysis["confidence"],
                "next_state": intent_analysis["next_state"],
            }

        except Exception as e:
            logger.error(f"Error processing customer response: {str(e)}")
            return {
                "bot_response": "I'm sorry, I didn't understand. Could you please repeat?",
                "detected_intent": "unclear",
                "confidence": 0.0,
                "next_state": "clarification",
            }

    def _analyze_customer_intent(self, customer_input: str, context: Dict) -> Dict:
        """
        Analyze customer's intent using AI.
        """
        try:
            prompt = f"""
            Analyze the customer's intent from their response in an EMI collection call:
            
            Customer said: "{customer_input}"
            
            Possible intents:
            - payment_agreement: Customer wants to pay now
            - payment_delay: Customer asks for more time
            - payment_refusal: Customer refuses to pay
            - unclear: Response is not clear
            - request_info: Customer asks for more information
            
            Respond in JSON format with intent, confidence (0-1), and suggested next_state.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
            )

            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
            else:
                result = {
                    "intent": "unclear",
                    "confidence": 0.0,
                    "next_state": "clarification",
                }
            return result

        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return {
                "intent": "unclear",
                "confidence": 0.0,
                "next_state": "clarification",
            }

    def _generate_bot_response(self, intent_analysis: Dict, context: Dict) -> str:
        """
        Generate appropriate bot response based on intent analysis.
        """
        intent = intent_analysis["intent"]
        language = context.get("language_preference", "en")

        responses = {
            "en": {
                "payment_agreement": "Great! I'll send you a secure payment link shortly. You can complete the payment using your preferred method.",
                "payment_delay": "I understand you need more time. Let's find a suitable date for your payment. When would work best for you?",
                "payment_refusal": "I understand your concerns. Let me connect you with our customer service team to discuss available options.",
                "unclear": "I'm sorry, I didn't quite understand. Could you please clarify your response?",
                "request_info": "I'd be happy to provide more information. What specific details would you like to know?",
            },
            "hi": {
                "payment_agreement": "बहुत अच्छा! मैं आपको जल्द ही एक सुरक्षित भुगतान लिंक भेजूंगा।",
                "payment_delay": "मैं समझ सकता हूं कि आपको अधिक समय चाहिए। आइए एक उपयुक्त तारीख तय करते हैं।",
                "payment_refusal": "मैं आपकी चिंताओं को समझ सकता हूं। मुझे आपको हमारी ग्राहक सेवा टीम से जोड़ने दें।",
                "unclear": "खुशी, मैं ठीक से नहीं समझ पाया। कृपया अपना उत्तर स्पष्ट कर सकते हैं?",
                "request_info": "मुझे अधिक जानकारी प्रदान करने में खुशी होगी। आप किस विशिष्ट विवरण के बारे में जानना चाहेंगे?",
            },
        }

        return responses.get(language, responses["en"]).get(
            intent, responses["en"]["unclear"]
        )
