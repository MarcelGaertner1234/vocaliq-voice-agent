"""
VocalIQ OpenAI Service
Integration mit OpenAI GPT-4 und Whisper für AI-Conversation und Speech-to-Text
"""
import asyncio
import logging
import base64
import io
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import httpx
import aiofiles
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from api.core.config import get_settings
from api.models.schemas import ConversationRequest, ConversationResponse, TranscriptionRequest, TranscriptionResponse

settings = get_settings()
logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI Service für AI-Conversations und Speech-to-Text"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                organization=settings.OPENAI_ORGANIZATION
            )
        
        # Conversation history cache
        self.conversation_cache: Dict[str, List[Dict[str, str]]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # System prompts für verschiedene Szenarien
        self.system_prompts = {
            "default": """Du bist VocalIQ, ein professioneller AI-Assistent für Geschäftstelefonie. 
Du hilfst bei Kundenanfragen, Terminbuchungen und allgemeinen Geschäftsangelegenheiten.

Wichtige Regeln:
- Sei freundlich, höflich und professionell
- Halte Antworten prägnant (max. 100 Wörter)
- Sprich Deutsch, es sei denn der Kunde wünscht eine andere Sprache
- Bei komplexen Anfragen leite zu einem menschlichen Mitarbeiter weiter
- Sammle relevante Informationen für Rückrufe oder Termine
- Verwende keine Umgangssprache oder Slang""",
            
            "appointment": """Du bist ein Terminplanungs-Assistent.
Deine Aufgabe ist es, Termine zu vereinbaren und relevante Informationen zu sammeln.

Informationen die du benötigst:
- Name und Kontaktdaten des Kunden
- Gewünschter Termin (Datum und Uhrzeit)
- Grund für den Termin
- Besondere Anforderungen oder Wünsche

Sei effizient aber freundlich. Bestätige alle Angaben bevor du den Termin als vereinbart betrachtest.""",
            
            "customer_support": """Du bist ein Kundenservice-Assistent.
Hilf bei Problemen, Beschwerden und allgemeinen Kundenanfragen.

Vorgehen:
- Höre aktiv zu und zeige Verständnis
- Stelle gezielte Nachfragen um das Problem zu verstehen
- Biete praktikable Lösungen an
- Bei technischen Problemen oder Beschwerden: sammle Details und leite weiter
- Bleibe stets höflich, auch bei schwierigen Kunden""",
            
            "sales": """Du bist ein Verkaufs-Assistent.
Deine Aufgabe ist es, Interesse zu wecken und qualifizierte Leads zu generieren.

Ziele:
- Bedarf des Kunden ermitteln
- Passende Lösungen aufzeigen
- Vertrauen aufbauen ohne aufdringlich zu sein
- Kontaktdaten sammeln für Follow-up
- Bei konkretem Interesse: Termin mit Verkaufsteam vereinbaren

Sei informativ aber nicht überwältigend. Höre mehr zu als du sprichst."""
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def create_conversation(
        self, 
        request: ConversationRequest,
        conversation_id: Optional[str] = None,
        prompt_type: str = "default"
    ) -> ConversationResponse:
        """
        AI-Conversation mit GPT-4
        """
        if not self.client:
            raise ValueError("OpenAI client not configured")
        
        try:
            # Build conversation history
            messages = await self._build_conversation_messages(
                request, conversation_id, prompt_type
            )
            
            logger.info(f"🤖 Creating conversation with {len(messages)} messages")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6
            )
            
            # Extract response
            ai_message = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Cache conversation if conversation_id provided
            if conversation_id:
                await self._update_conversation_cache(
                    conversation_id, 
                    request.message, 
                    ai_message
                )
            
            logger.info(
                f"✅ Conversation completed: {usage['total_tokens']} tokens used"
            )
            
            return ConversationResponse(
                message=ai_message,
                usage=usage,
                model=settings.OPENAI_MODEL,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            logger.error(f"OpenAI conversation error: {str(e)}")
            raise
    
    async def _build_conversation_messages(
        self, 
        request: ConversationRequest,
        conversation_id: Optional[str],
        prompt_type: str
    ) -> List[Dict[str, str]]:
        """Build message array für OpenAI API"""
        messages = []
        
        # System prompt
        system_prompt = request.system_prompt or self.system_prompts.get(prompt_type, self.system_prompts["default"])
        messages.append({"role": "system", "content": system_prompt})
        
        # Conversation history from cache or request
        if conversation_id and conversation_id in self.conversation_cache:
            # Use cached conversation
            cached_messages = self.conversation_cache[conversation_id]
            messages.extend(cached_messages[-20:])  # Limit to last 20 messages
        elif request.context:
            # Use provided context
            messages.extend(request.context[-20:])  # Limit to last 20 messages
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        return messages
    
    async def _update_conversation_cache(
        self, 
        conversation_id: str, 
        user_message: str, 
        ai_message: str
    ):
        """Update conversation cache"""
        if conversation_id not in self.conversation_cache:
            self.conversation_cache[conversation_id] = []
        
        # Add messages to cache
        self.conversation_cache[conversation_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_message}
        ])
        
        # Keep only last 50 messages
        if len(self.conversation_cache[conversation_id]) > 50:
            self.conversation_cache[conversation_id] = self.conversation_cache[conversation_id][-50:]
        
        # Update timestamp
        self.cache_timestamps[conversation_id] = datetime.utcnow()
        
        # Cleanup old conversations (older than 1 hour)
        await self._cleanup_conversation_cache()
    
    async def _cleanup_conversation_cache(self):
        """Cleanup alte Conversation-Caches"""
        current_time = datetime.utcnow()
        expired_conversations = []
        
        for conv_id, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > timedelta(hours=1):
                expired_conversations.append(conv_id)
        
        for conv_id in expired_conversations:
            self.conversation_cache.pop(conv_id, None)
            self.cache_timestamps.pop(conv_id, None)
            
        if expired_conversations:
            logger.info(f"🧹 Cleaned up {len(expired_conversations)} expired conversations")
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(Exception)
    )
    async def transcribe_audio(
        self, 
        audio_data: bytes,
        language: str = "de",
        format: str = "wav"
    ) -> TranscriptionResponse:
        """
        Speech-to-Text mit OpenAI Whisper
        """
        if not self.client:
            raise ValueError("OpenAI client not configured")
        
        try:
            logger.info(f"🎤 Transcribing {len(audio_data)} bytes of {format} audio")
            
            # Create audio file in memory
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{format}"
            
            # Call Whisper API
            response = await self.client.audio.transcriptions.create(
                model=settings.WHISPER_MODEL,
                file=audio_file,
                language=language if language != "auto" else None,
                response_format="verbose_json",
                temperature=0
            )
            
            # Calculate confidence (Whisper doesn't provide confidence directly)
            # We estimate based on the presence of multiple segments and word count
            segments = getattr(response, 'segments', [])
            confidence = 0.85 if len(segments) > 0 else 0.5
            
            # Count words
            word_count = len(response.text.split()) if response.text else 0
            
            logger.info(f"✅ Transcription completed: '{response.text[:50]}...' ({word_count} words)")
            
            return TranscriptionResponse(
                transcript=response.text,
                confidence=confidence,
                language=response.language,
                duration=response.duration,
                word_count=word_count
            )
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            raise
    
    async def transcribe_audio_from_url(
        self, 
        audio_url: str,
        language: str = "de"
    ) -> TranscriptionResponse:
        """
        Speech-to-Text von Audio-URL
        """
        try:
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                audio_data = response.content
            
            # Detect format from URL
            format = "wav"
            if ".mp3" in audio_url.lower():
                format = "mp3"
            elif ".ogg" in audio_url.lower():
                format = "ogg"
            elif ".webm" in audio_url.lower():
                format = "webm"
            
            return await self.transcribe_audio(audio_data, language, format)
            
        except Exception as e:
            logger.error(f"Error transcribing from URL {audio_url}: {str(e)}")
            raise
    
    async def create_streaming_conversation(
        self, 
        request: ConversationRequest,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streaming AI-Conversation für Real-time Responses
        """
        if not self.client:
            raise ValueError("OpenAI client not configured")
        
        try:
            messages = await self._build_conversation_messages(
                request, conversation_id, "default"
            )
            
            logger.info(f"🌊 Starting streaming conversation")
            
            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Cache the complete response
            if conversation_id and full_response:
                await self._update_conversation_cache(
                    conversation_id,
                    request.message,
                    full_response
                )
            
        except Exception as e:
            logger.error(f"Streaming conversation error: {str(e)}")
            raise
    
    def clear_conversation_cache(self, conversation_id: str):
        """Clear conversation cache für einen Benutzer"""
        self.conversation_cache.pop(conversation_id, None)
        self.cache_timestamps.pop(conversation_id, None)
        logger.info(f"🗑️ Cleared conversation cache for {conversation_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health Check für OpenAI Service"""
        if not self.client:
            return {
                "status": "not_configured",
                "error": "OpenAI API key not set"
            }
        
        try:
            # Test mit einer kleinen Anfrage
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "model": settings.OPENAI_MODEL,
                "cached_conversations": len(self.conversation_cache),
                "test_response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global Service Instance
openai_service = OpenAIService()