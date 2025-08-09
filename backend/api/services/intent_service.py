"""
Intent Recognition Service
Identifies user intentions and extracts entities from voice transcripts
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser
import spacy

from openai import AsyncOpenAI
from api.models.company import Company, CompanyIntent
from api.core.config import get_settings
from api.core.database import get_session
from sqlmodel import select

logger = logging.getLogger(__name__)

class IntentService:
    """
    Service for recognizing intents and extracting entities
    """
    
    def __init__(self):
        settings = get_settings()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Load spaCy model for entity extraction (install: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not loaded. Entity extraction may be limited.")
            self.nlp = None
    
    async def recognize_intent(
        self,
        company: Company,
        transcript: str,
        conversation_context: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Recognize intent and extract entities from transcript
        """
        # Get company's custom intents
        async with get_session() as session:
            result = await session.execute(
                select(CompanyIntent)
                .where(CompanyIntent.company_id == company.id)
                .where(CompanyIntent.is_enabled == True)
                .order_by(CompanyIntent.priority.desc())
            )
            company_intents = result.scalars().all()
        
        # First, try rule-based matching for high-confidence intents
        rule_based_result = self._rule_based_matching(transcript, company_intents)
        if rule_based_result and rule_based_result["confidence"] > 0.8:
            # Extract entities
            entities = await self._extract_entities(transcript, rule_based_result["intent"])
            return {
                "intent": rule_based_result["intent"],
                "confidence": rule_based_result["confidence"],
                "entities": entities,
                "method": "rule_based"
            }
        
        # Fall back to GPT-4 for intent classification
        gpt_result = await self._gpt_intent_classification(
            transcript,
            company_intents,
            conversation_context
        )
        
        # Extract entities
        entities = await self._extract_entities(transcript, gpt_result["intent"])
        
        return {
            "intent": gpt_result["intent"],
            "confidence": gpt_result["confidence"],
            "entities": entities,
            "method": "gpt4"
        }
    
    def _rule_based_matching(
        self,
        transcript: str,
        company_intents: List[CompanyIntent]
    ) -> Optional[Dict[str, Any]]:
        """
        Rule-based intent matching using keywords
        """
        transcript_lower = transcript.lower()
        best_match = None
        best_score = 0
        
        for intent in company_intents:
            if not intent.keywords:
                continue
            
            # Count matching keywords
            matches = sum(1 for keyword in intent.keywords if keyword.lower() in transcript_lower)
            
            if matches > 0:
                score = matches / len(intent.keywords)
                if score > best_score:
                    best_score = score
                    best_match = intent
        
        if best_match and best_score > 0.5:
            return {
                "intent": best_match.intent_name,
                "confidence": min(best_score * 1.2, 1.0)  # Boost confidence slightly
            }
        
        return None
    
    async def _gpt_intent_classification(
        self,
        transcript: str,
        company_intents: List[CompanyIntent],
        conversation_context: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Use GPT-4 for intent classification
        """
        # Prepare intent descriptions
        intent_descriptions = []
        for intent in company_intents:
            desc = f"- {intent.intent_name}: {intent.description or 'No description'}"
            if intent.example_phrases:
                desc += f" (Examples: {', '.join(intent.example_phrases[:3])})"
            intent_descriptions.append(desc)
        
        # Build prompt
        prompt = f"""
        Classify the following user transcript into one of these intents:
        
        {chr(10).join(intent_descriptions)}
        
        If none of the intents match well, use "general_inquiry".
        
        User transcript: "{transcript}"
        
        Respond with JSON:
        {{
            "intent": "intent_name",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }}
        """
        
        # Add conversation context if available
        messages = []
        if conversation_context:
            messages.extend(conversation_context[-5:])  # Last 5 messages for context
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=200,
                temperature=0
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "intent": result.get("intent", "general_inquiry"),
                "confidence": result.get("confidence", 0.5)
            }
            
        except Exception as e:
            logger.error(f"Error in GPT intent classification: {e}")
            return {
                "intent": "general_inquiry",
                "confidence": 0.3
            }
    
    async def _extract_entities(
        self,
        transcript: str,
        intent: str
    ) -> Dict[str, Any]:
        """
        Extract entities based on intent type
        """
        entities = {}
        
        # Extract common entities
        entities.update(self._extract_datetime(transcript))
        entities.update(self._extract_phone_number(transcript))
        entities.update(self._extract_email(transcript))
        entities.update(self._extract_numbers(transcript))
        
        # Intent-specific extraction
        if intent in ["make_reservation", "book_appointment"]:
            entities.update(await self._extract_reservation_entities(transcript))
        elif intent == "check_order":
            entities.update(self._extract_order_entities(transcript))
        
        # Use spaCy for named entities if available
        if self.nlp:
            doc = self.nlp(transcript)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["customer_name"] = ent.text
                elif ent.label_ == "ORG":
                    entities["organization"] = ent.text
                elif ent.label_ == "LOC" or ent.label_ == "GPE":
                    entities["location"] = ent.text
        
        return entities
    
    def _extract_datetime(self, text: str) -> Dict[str, Any]:
        """
        Extract date and time entities
        """
        entities = {}
        
        # Common date/time patterns
        patterns = {
            "time": [
                r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?\b',
                r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',
                r'\b(noon|midnight|morning|afternoon|evening)\b'
            ],
            "date": [
                r'\b(today|tomorrow|tonight)\b',
                r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\b'
            ]
        }
        
        text_lower = text.lower()
        
        # Extract time
        for pattern in patterns["time"]:
            match = re.search(pattern, text_lower)
            if match:
                entities["time"] = match.group()
                break
        
        # Extract date
        for pattern in patterns["date"]:
            match = re.search(pattern, text_lower)
            if match:
                date_str = match.group()
                
                # Convert relative dates
                if date_str == "today":
                    entities["date"] = datetime.now().date().isoformat()
                elif date_str == "tomorrow":
                    entities["date"] = (datetime.now() + timedelta(days=1)).date().isoformat()
                elif date_str == "tonight":
                    entities["date"] = datetime.now().date().isoformat()
                    entities["time"] = "evening"
                else:
                    entities["date"] = date_str
                break
        
        # Try parsing with dateutil
        try:
            parsed = parser.parse(text, fuzzy=True)
            if not entities.get("date"):
                entities["date"] = parsed.date().isoformat()
            if not entities.get("time"):
                entities["time"] = parsed.time().isoformat()
        except:
            pass
        
        return entities
    
    def _extract_phone_number(self, text: str) -> Dict[str, Any]:
        """
        Extract phone numbers
        """
        pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        match = re.search(pattern, text)
        if match:
            return {"phone_number": match.group()}
        return {}
    
    def _extract_email(self, text: str) -> Dict[str, Any]:
        """
        Extract email addresses
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        if match:
            return {"email": match.group()}
        return {}
    
    def _extract_numbers(self, text: str) -> Dict[str, Any]:
        """
        Extract numeric entities
        """
        entities = {}
        
        # Party size for reservations
        party_patterns = [
            r'\b(\d+)\s*(?:people|persons|guests)\b',
            r'\b(?:party of|table for)\s*(\d+)\b',
            r'\b(\d+)\s*(?:of us)\b'
        ]
        
        for pattern in party_patterns:
            match = re.search(pattern, text.lower())
            if match:
                entities["party_size"] = int(match.group(1))
                break
        
        # Duration
        duration_pattern = r'\b(\d+)\s*(?:hour|hr|minute|min)s?\b'
        match = re.search(duration_pattern, text.lower())
        if match:
            entities["duration"] = match.group()
        
        return entities
    
    async def _extract_reservation_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract reservation-specific entities
        """
        entities = {}
        
        # Special requests
        special_keywords = ["allerg", "wheelchair", "window", "outside", "quiet", "birthday", "anniversary"]
        special_requests = []
        text_lower = text.lower()
        
        for keyword in special_keywords:
            if keyword in text_lower:
                # Extract the sentence containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        special_requests.append(sentence.strip())
        
        if special_requests:
            entities["special_requests"] = " ".join(special_requests)
        
        # Seating preference
        if "outside" in text_lower or "patio" in text_lower:
            entities["seating_preference"] = "outdoor"
        elif "inside" in text_lower:
            entities["seating_preference"] = "indoor"
        elif "bar" in text_lower:
            entities["seating_preference"] = "bar"
        
        return entities
    
    def _extract_order_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract order-related entities
        """
        entities = {}
        
        # Order number pattern
        order_pattern = r'\b(?:order\s*#?\s*)?([A-Z0-9]{4,})\b'
        match = re.search(order_pattern, text.upper())
        if match:
            entities["order_number"] = match.group(1)
        
        return entities
    
    async def get_intent_response_template(
        self,
        intent: str,
        entities: Dict[str, Any]
    ) -> str:
        """
        Get a response template based on intent and entities
        """
        templates = {
            "make_reservation": self._reservation_template,
            "check_hours": self._hours_template,
            "menu_inquiry": self._menu_template,
            "general_inquiry": self._general_template
        }
        
        template_func = templates.get(intent, self._general_template)
        return template_func(entities)
    
    def _reservation_template(self, entities: Dict[str, Any]) -> str:
        """
        Template for reservation confirmation
        """
        parts = ["I'll help you make a reservation."]
        
        if entities.get("date"):
            parts.append(f"For {entities['date']}")
        if entities.get("time"):
            parts.append(f"at {entities['time']}")
        if entities.get("party_size"):
            parts.append(f"for {entities['party_size']} people")
        
        if len(parts) > 1:
            parts.append("Is that correct?")
        else:
            parts = ["I'll help you make a reservation. What date and time would you like?"]
        
        return " ".join(parts)
    
    def _hours_template(self, entities: Dict[str, Any]) -> str:
        """
        Template for business hours
        """
        return "Let me check our business hours for you."
    
    def _menu_template(self, entities: Dict[str, Any]) -> str:
        """
        Template for menu inquiries
        """
        return "I'll help you with our menu information."
    
    def _general_template(self, entities: Dict[str, Any]) -> str:
        """
        General template
        """
        return "How can I assist you today?"