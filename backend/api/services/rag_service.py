"""
RAG (Retrieval Augmented Generation) Service
Combines knowledge base search with LLM generation for accurate responses
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from openai import AsyncOpenAI
from api.services.knowledge_service import KnowledgeService
from api.models.company import Company, KnowledgeBase
from api.core.config import get_settings

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG Service for generating context-aware responses
    """
    
    def __init__(self):
        settings = get_settings()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.knowledge_service = KnowledgeService()
        
    async def generate_response(
        self,
        company: Company,
        knowledge_base: KnowledgeBase,
        user_query: str,
        conversation_history: List[Dict[str, str]] = None,
        include_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG
        """
        # Get relevant context from knowledge base
        context = await self.knowledge_service.get_knowledge_context(
            knowledge_base,
            user_query,
            max_tokens=2000
        )
        
        # Build the system prompt with company context
        system_prompt = self._build_system_prompt(company, context)
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add user query
        messages.append({"role": "user", "content": user_query})
        
        # Generate response
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Search for relevant documents if sources requested
            sources = []
            if include_sources and context:
                search_results = await self.knowledge_service.search_knowledge(
                    knowledge_base,
                    user_query,
                    limit=3
                )
                sources = [
                    {
                        "document": result["document"],
                        "relevance": result["relevance_score"]
                    }
                    for result in search_results
                ]
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": bool(context),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "answer": "I apologize, but I'm having trouble accessing the information right now. Please try again.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(self, company: Company, context: str) -> str:
        """
        Build a comprehensive system prompt with company info and context
        """
        # Base prompt template
        if company.system_prompt_template:
            base_prompt = company.system_prompt_template
        else:
            base_prompt = self._get_default_prompt(company)
        
        # Add context if available
        if context:
            context_section = f"""
            
RELEVANT INFORMATION FROM KNOWLEDGE BASE:
{context}

Use the above information to answer questions accurately. If the information is not in the knowledge base, you can provide general assistance but mention that you don't have specific information about that topic.
"""
        else:
            context_section = """

Note: No specific knowledge base information is available for this query. Provide general assistance based on your training.
"""
        
        # Add business hours if configured
        business_hours_section = ""
        if company.business_hours:
            business_hours_section = f"""

BUSINESS HOURS:
{self._format_business_hours(company.business_hours)}
"""
        
        # Combine all sections
        full_prompt = f"""{base_prompt}

COMPANY INFORMATION:
- Business Name: {company.name}
- Business Type: {company.business_type}
- Voice Personality: {company.voice_personality}
- Language: {company.voice_language}
{business_hours_section}
{context_section}

INSTRUCTIONS:
1. Be helpful and {company.voice_personality}
2. Keep responses concise for phone conversations
3. If asked about appointments/reservations, check if this feature is enabled
4. Always maintain a professional tone while being friendly
5. If you don't know something, admit it and offer to help in other ways
"""
        
        return full_prompt
    
    def _get_default_prompt(self, company: Company) -> str:
        """
        Get default prompt based on business type
        """
        prompts = {
            "restaurant": """You are an AI assistant for a restaurant. You help customers with reservations, menu information, hours, and general inquiries.""",
            
            "medical": """You are an AI assistant for a medical practice. You help patients with appointment scheduling, general health information, and office policies. Always remind patients that you cannot provide medical advice.""",
            
            "retail": """You are an AI assistant for a retail business. You help customers with product information, store hours, order status, and general inquiries.""",
            
            "service": """You are an AI assistant for a service business. You help customers with appointment booking, service information, pricing, and general inquiries.""",
            
            "general": """You are an AI assistant for a business. You help customers with information, appointments, and general inquiries."""
        }
        
        return prompts.get(company.business_type, prompts["general"])
    
    def _format_business_hours(self, hours: Dict[str, Any]) -> str:
        """
        Format business hours for prompt
        """
        if not hours:
            return "Hours not specified"
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        formatted = []
        
        for day in days:
            day_hours = hours.get(day.lower())
            if day_hours:
                if day_hours == "closed":
                    formatted.append(f"{day}: Closed")
                else:
                    formatted.append(f"{day}: {day_hours}")
        
        return "\n".join(formatted)
    
    async def check_answer_quality(
        self,
        question: str,
        answer: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Evaluate if the answer is accurate based on context
        """
        prompt = f"""
        Evaluate if the answer accurately addresses the question based on the provided context.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}
        
        ANSWER:
        {answer}
        
        Provide a JSON response with:
        - "is_accurate": boolean
        - "confidence": float (0-1)
        - "issues": list of any problems
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error checking answer quality: {e}")
            return {
                "is_accurate": True,
                "confidence": 0.5,
                "issues": []
            }