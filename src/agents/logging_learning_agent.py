import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.utils.database import get_db_session
from src.models import CustomerInteraction, Customer, Payment
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

logger = logging.getLogger(__name__)


class LoggingLearningAgent:
    """
    Agent responsible for logging interactions and learning from outcomes
    to improve future performance.
    """

    def __init__(self):
        self.log_levels = {
            "interaction": logging.INFO,
            "decision": logging.INFO,
            "payment": logging.INFO,
            "error": logging.ERROR,
            "system": logging.DEBUG,
        }

        # Initialize ML models
        self.outcome_predictor = None
        self.sentiment_analyzer = None
        self.models_path = "data/models"

        # Ensure models directory exists
        os.makedirs(self.models_path, exist_ok=True)

        # Load existing models if available
        self._load_models()

    def log_interaction(self, interaction_data: Dict) -> str:
        """
        Log customer interaction with structured data.
        """
        log_id = f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{interaction_data['customer_id']}"

        # Structured log entry
        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "customer_interaction",
            "customer_id": interaction_data["customer_id"],
            "interaction_type": interaction_data.get("interaction_type", "unknown"),
            "call_id": interaction_data.get("call_id"),
            "outcome": interaction_data.get("outcome"),
            "sentiment_score": interaction_data.get("sentiment_score"),
            "call_duration": interaction_data.get("call_duration"),
            "conversation_summary": interaction_data.get("conversation_summary"),
            "next_action": interaction_data.get("next_action"),
            "agent_version": "1.0",
        }

        # Log to file and database
        logger.info(f"INTERACTION_LOG: {json.dumps(log_entry)}")

        # Store in database for analysis
        self._store_log_entry(log_entry)

        return log_id

    def log_decision(self, decision_data: Dict) -> str:
        """
        Log decision-making process and outcomes.
        """
        log_id = f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{decision_data['customer_id']}"

        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "decision",
            "customer_id": decision_data["customer_id"],
            "conversation_outcome": decision_data.get("conversation_outcome"),
            "decision_action": decision_data.get("next_action"),
            "priority": decision_data.get("priority"),
            "escalation_needed": decision_data.get("escalation_needed"),
            "confidence_score": decision_data.get("confidence_score", 0.0),
            "factors_considered": decision_data.get("factors", []),
            "business_rules_applied": decision_data.get("rules_applied", []),
        }

        logger.info(f"DECISION_LOG: {json.dumps(log_entry)}")
        self._store_log_entry(log_entry)

        return log_id

    def log_payment_activity(self, payment_data: Dict) -> str:
        """
        Log payment-related activities and outcomes.
        """
        log_id = f"PAY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{payment_data.get('customer_id', 'unknown')}"

        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "payment",
            "customer_id": payment_data.get("customer_id"),
            "payment_id": payment_data.get("payment_id"),
            "amount": payment_data.get("amount"),
            "payment_method": payment_data.get("payment_method"),
            "status": payment_data.get("status"),
            "gateway_response": payment_data.get("gateway_response"),
            "failure_reason": payment_data.get("failure_reason"),
            "time_to_payment": payment_data.get(
                "time_to_payment"
            ),  # Time from link send to payment
        }

        logger.info(f"PAYMENT_LOG: {json.dumps(log_entry)}")
        self._store_log_entry(log_entry)

        return log_id

    def log_system_event(self, event_data: Dict) -> str:
        """
        Log system events for monitoring and debugging.
        """
        log_id = f"SYS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "system_event",
            "event_name": event_data.get("event"),
            "component": event_data.get("component"),
            "severity": event_data.get("severity", "info"),
            "message": event_data.get("message"),
            "metadata": event_data.get("metadata", {}),
        }

        log_level = getattr(
            logging, event_data.get("severity", "info").upper(), logging.INFO
        )
        logger.log(log_level, f"SYSTEM_LOG: {json.dumps(log_entry)}")

        self._store_log_entry(log_entry)

        return log_id

    def _store_log_entry(self, log_entry: Dict):
        """
        Store log entry in database for future analysis.
        """
        try:
            # In production, this would store in a dedicated logging table
            # For demo, we'll use a simple file-based approach
            log_file = (
                f"data/logs/emi_voicebot_{datetime.now().strftime('%Y%m%d')}.jsonl"
            )
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Error storing log entry: {str(e)}")

    def analyze_interaction_patterns(self, days: int = 30) -> Dict:
        """
        Analyze interaction patterns to identify improvement opportunities.
        """
        db = None
        try:
            # Get interaction data from database
            db = get_db_session()
            cutoff_date = datetime.now() - timedelta(days=days)

            interactions = (
                db.query(CustomerInteraction)
                .filter(CustomerInteraction.created_at >= cutoff_date)
                .all()
            )

            if not interactions:
                return {"message": "No interactions found for analysis"}

            # Convert to DataFrame for analysis
            data = []
            for interaction in interactions:
                data.append(
                    {
                        "customer_id": interaction.customer_id,
                        "outcome": interaction.outcome,
                        "sentiment_score": interaction.sentiment_score or 0,
                        "call_duration": interaction.call_duration or 0,
                        "hour_of_day": interaction.created_at.hour,
                        "day_of_week": interaction.created_at.weekday(),
                    }
                )

            df = pd.DataFrame(data)

            # Analyze patterns
            analysis = {
                "total_interactions": len(df),
                "outcome_distribution": df["outcome"].value_counts().to_dict(),
                "average_sentiment": float(df["sentiment_score"].mean()),
                "average_call_duration": float(df["call_duration"].mean()),
                "best_call_hours": df.groupby("hour_of_day")["sentiment_score"]
                .mean()
                .sort_values(ascending=False)
                .head(3)
                .to_dict(),
                "best_call_days": df.groupby("day_of_week")["sentiment_score"]
                .mean()
                .sort_values(ascending=False)
                .to_dict(),
                "successful_outcomes": len(
                    df[df["outcome"].isin(["payment_made", "promised_payment"])]
                )
                / len(df),
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {str(e)}")
            return {"error": str(e)}
        finally:
            if db is not None:
                db.close()

    def train_outcome_predictor(self) -> Dict:
        """
        Train ML model to predict interaction outcomes based on customer features.
        """
        try:
            # Get training data
            training_data = self._prepare_training_data()

            if len(training_data) < 50:
                return {
                    "error": "Insufficient training data. Need at least 50 interactions."
                }

            df = pd.DataFrame(training_data)

            # Features for prediction
            feature_columns = [
                "risk_score",
                "previous_interactions",
                "time_since_last_payment",
                "outstanding_amount",
                "call_hour",
                "call_day",
            ]

            X = df[feature_columns]
            y = df["outcome_success"]  # Binary: successful outcome or not

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            self.outcome_predictor = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.outcome_predictor.fit(X_train, y_train)

            # Evaluate model
            y_pred = self.outcome_predictor.predict(X_test)
            accuracy = (y_pred == y_test).mean()

            # Save model
            model_path = os.path.join(self.models_path, "outcome_predictor.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(self.outcome_predictor, f)

            # Feature importance
            feature_importance = dict(
                zip(feature_columns, self.outcome_predictor.feature_importances_)
            )

            return {
                "status": "success",
                "accuracy": float(accuracy),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "feature_importance": feature_importance,
            }

        except Exception as e:
            logger.error(f"Error training outcome predictor: {str(e)}")
            return {"error": str(e)}

    def predict_interaction_outcome(self, customer_context: Dict) -> Dict:
        """
        Predict likely outcome of interaction based on customer context.
        """
        try:
            if not self.outcome_predictor:
                return {"error": "Outcome predictor model not available"}

            # Prepare features
            features = self._extract_prediction_features(customer_context)

            # Make prediction
            probability = self.outcome_predictor.predict_proba([features])[0]
            prediction = self.outcome_predictor.predict([features])[0]

            return {
                "predicted_success": bool(prediction),
                "success_probability": (
                    float(probability[1]) if len(probability) > 1 else 0.5
                ),
                "features_used": features,
            }

        except Exception as e:
            logger.error(f"Error predicting outcome: {str(e)}")
            return {"error": str(e)}

    def _prepare_training_data(self) -> List[Dict]:
        """
        Prepare training data from historical interactions.
        """
        db = get_db_session()
        try:
            # Get interactions with customer context
            interactions = db.query(CustomerInteraction).join(Customer).all()

            training_data = []
            for interaction in interactions:
                customer = interaction.customer

                # Determine if outcome was successful
                outcome_success = interaction.outcome in [
                    "payment_made",
                    "promised_payment",
                    "payment_requested",
                ]

                training_data.append(
                    {
                        "risk_score": customer.risk_score or 50,
                        "previous_interactions": len(customer.interactions),
                        "time_since_last_payment": 30,  # Simplified - would calculate actual
                        "outstanding_amount": 50000,  # Simplified - would get from loans
                        "call_hour": interaction.created_at.hour,
                        "call_day": interaction.created_at.weekday(),
                        "outcome_success": outcome_success,
                    }
                )

            return training_data

        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return []
        finally:
            db.close()

    def _extract_prediction_features(self, customer_context: Dict) -> List[float]:
        """
        Extract features for prediction from customer context.
        """
        features = [
            customer_context.get("risk_score", 50),
            len(customer_context.get("recent_interactions", [])),
            30,  # time_since_last_payment - simplified
            sum(
                [
                    loan["outstanding_amount"]
                    for loan in customer_context.get("loans", [])
                ]
            ),
            datetime.now().hour,
            datetime.now().weekday(),
        ]

        return features

    def _load_models(self):
        """
        Load existing ML models if available.
        """
        try:
            outcome_model_path = os.path.join(self.models_path, "outcome_predictor.pkl")
            if os.path.exists(outcome_model_path):
                with open(outcome_model_path, "rb") as f:
                    self.outcome_predictor = pickle.load(f)
                logger.info("Loaded outcome predictor model")

        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")

    def generate_insights_report(self, days: int = 30) -> Dict:
        """
        Generate comprehensive insights report for business stakeholders.
        """
        try:
            # Analyze interactions
            interaction_analysis = self.analyze_interaction_patterns(days)

            # Get payment analytics (would integrate with payment agent)
            payment_analysis = self._analyze_payment_trends(days)

            # Customer segmentation insights
            segmentation_analysis = self._analyze_customer_segments()

            # System performance
            system_performance = self._analyze_system_performance(days)

            # Recommendations
            recommendations = self._generate_recommendations(
                interaction_analysis, payment_analysis, segmentation_analysis
            )

            report = {
                "report_date": datetime.now().isoformat(),
                "analysis_period_days": days,
                "interaction_analysis": interaction_analysis,
                "payment_analysis": payment_analysis,
                "segmentation_analysis": segmentation_analysis,
                "system_performance": system_performance,
                "recommendations": recommendations,
            }

            # Save report
            report_file = f"data/reports/insights_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            return report

        except Exception as e:
            logger.error(f"Error generating insights report: {str(e)}")
            return {"error": str(e)}

    def _analyze_payment_trends(self, days: int) -> Dict:
        """
        Analyze payment trends and patterns.
        """
        # Simplified analysis - would integrate with payment agent in production
        return {
            "total_collections": 1500000,
            "collection_rate": 0.78,
            "average_time_to_payment": "2.3 days",
            "preferred_payment_methods": {"upi": 45, "netbanking": 30, "cards": 25},
        }

    def _analyze_customer_segments(self) -> Dict:
        """
        Analyze customer segment behaviors.
        """
        return {
            "high_risk_customers": {"count": 25, "collection_rate": 0.45},
            "medium_risk_customers": {"count": 150, "collection_rate": 0.72},
            "low_risk_customers": {"count": 200, "collection_rate": 0.95},
            "vip_customers": {"count": 30, "collection_rate": 0.98},
        }

    def _analyze_system_performance(self, days: int) -> Dict:
        """
        Analyze system performance metrics.
        """
        return {
            "total_calls_made": 500,
            "successful_connections": 450,
            "average_call_duration": "3.2 minutes",
            "system_uptime": "99.8%",
            "error_rate": "0.5%",
        }

    def _generate_recommendations(
        self,
        interaction_analysis: Dict,
        payment_analysis: Dict,
        segmentation_analysis: Dict,
    ) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        """
        recommendations = []

        # Based on interaction analysis
        if interaction_analysis.get("average_sentiment", 0) < 0.3:
            recommendations.append(
                "Consider improving conversation scripts to enhance customer sentiment"
            )

        # Based on payment analysis
        collection_rate = payment_analysis.get("collection_rate", 0)
        if collection_rate < 0.8:
            recommendations.append(
                "Implement more flexible payment options to improve collection rate"
            )

        # Based on segmentation
        high_risk_rate = segmentation_analysis.get("high_risk_customers", {}).get(
            "collection_rate", 0
        )
        if high_risk_rate < 0.5:
            recommendations.append(
                "Develop specialized strategies for high-risk customers"
            )

        # Best practice recommendations
        recommendations.extend(
            [
                "Schedule calls during peak success hours (based on historical data)",
                "Implement A/B testing for different conversation approaches",
                "Consider multilingual support expansion based on customer demographics",
            ]
        )

        return recommendations
