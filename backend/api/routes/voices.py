"""
Voice Management Routes with Real ElevenLabs Integration
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
import hashlib
from pathlib import Path
import httpx
from api.core.config import get_settings

router = APIRouter(prefix="/voices", tags=["Voices"])
logger = logging.getLogger(__name__)
settings = get_settings()

# TTS Cache Pfad (muss zu routes/audio.py passen)
import os
TTS_CACHE_DIR = Path(os.getcwd()) / "storage" / "tts_cache"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Available German voices from ElevenLabs
GERMAN_VOICES = [
    {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "language": "de"},
    {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "language": "de"},
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "language": "de"},
    {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "language": "de"},
    {"voice_id": "N2lVS1w4EtoT3dr4eOWO", "name": "Callum", "language": "de"},
    {"voice_id": "ODq5zmih8GrVes37Dizd", "name": "Patrick", "language": "de"},
    {"voice_id": "ThT5KcBeYPX3keUQqHPh", "name": "Harry", "language": "de"},
    {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "language": "de"},
    {"voice_id": "XB0fDUnXU5powFXDhCwa", "name": "Charlotte", "language": "de"},
    {"voice_id": "XrExE9yKIg1WjnnlVkGX", "name": "Matilda", "language": "de"},
    {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "language": "de"},
    {"voice_id": "pMsXgVXv3BLzUgSXRplE", "name": "Serena", "language": "de"},
    {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "language": "de"},
    {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "language": "de"},
    {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "language": "de"},
    {"voice_id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", "language": "de"},
    {"voice_id": "nPczCjzI2devNBz1zQrb", "name": "Brian", "language": "de"},
    {"voice_id": "g5CIjZEefAph4nQFvHAz", "name": "Lily", "language": "de"},
    {"voice_id": "SAz9YHcvj6GT2YYXdXww", "name": "River", "language": "de"},
    {"voice_id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie", "language": "de"},
    {"voice_id": "TX3LPaxmHKxFdv7VOQHJ", "name": "Liam", "language": "de"},
    {"voice_id": "pFZP5JQG7iQjIQuC4Bku", "name": "Lily", "language": "de"},
    {"voice_id": "SOYHLrjzK2X1ezoPC6cr", "name": "Harry", "language": "de"}
]

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "ErXwobaYiN019PkySvjV"  # Default: Antoni
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0

class ChatRequest(BaseModel):
    message: str
    voice_id: str = "ErXwobaYiN019PkySvjV"  # Default: Antoni

# Import ElevenLabs service
try:
    from api.services.elevenlabs_service import elevenlabs_service
    from api.models.schemas import TTSRequest as ServiceTTSRequest, TTSResponse
    ELEVENLABS_AVAILABLE = True
    logger.info("✅ ElevenLabs service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ ElevenLabs service not available: {e}")
    ELEVENLABS_AVAILABLE = False

# Import OpenAI service for chat
try:
    from api.services.openai_service import openai_service
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ OpenAI service not available: {e}")
    OPENAI_AVAILABLE = False

@router.get("/all")
async def get_all_voices() -> List[Dict[str, Any]]:
    """Hole alle verfügbaren ElevenLabs-Stimmen (inkl. preview_url).
    Fällt auf statische Liste zurück, wenn kein API-Key konfiguriert ist.
    """
    try:
        api_key = getattr(settings, "ELEVENLABS_API_KEY", None)
        if not api_key:
            logger.warning("ElevenLabs API key not configured - returning static voices list")
            # Ergänze statische Liste minimal mit None-Previews
            return [{**v, "preview_url": None} for v in GERMAN_VOICES]

        headers = {"xi-api-key": api_key}
        url = "https://api.elevenlabs.io/v1/voices"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            voices = data.get("voices", [])

        result: List[Dict[str, Any]] = []
        for voice in voices:
            result.append({
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "category": voice.get("category"),
                "description": voice.get("description"),
                "labels": voice.get("labels", {}),
                "preview_url": voice.get("preview_url"),
                "language": voice.get("labels", {}).get("language", None)
            })
        return result
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching voices from ElevenLabs: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch voices from ElevenLabs")
    except Exception as e:
        logger.error(f"Unexpected error fetching voices: {e}")
        # Fallback: statische Liste
        return [{**v, "preview_url": None} for v in GERMAN_VOICES]

@router.get("/list")
async def get_voices_list() -> List[Dict[str, Any]]:
    """Alias zu /voices/all: Liste aller Stimmen inkl. preview_url (Fallback statisch)."""
    try:
        api_key = getattr(settings, "ELEVENLABS_API_KEY", None)
        if not api_key:
            return [{**v, "preview_url": None} for v in GERMAN_VOICES]
        headers = {"xi-api-key": api_key}
        url = "https://api.elevenlabs.io/v1/voices"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            voices = data.get("voices", [])
        return [
            {
                "voice_id": v.get("voice_id"),
                "name": v.get("name"),
                "category": v.get("category"),
                "description": v.get("description"),
                "labels": v.get("labels", {}),
                "preview_url": v.get("preview_url"),
                "language": (v.get("labels") or {}).get("language")
            }
            for v in voices
        ]
    except Exception:
        return [{**v, "preview_url": None} for v in GERMAN_VOICES]

def _generate_cache_key(text: str, voice_id: str) -> str:
    """Generate cache key for audio files"""
    content = f"{text}:{voice_id}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]

@router.get("/recommended")
async def get_recommended_voices(language: str = Query("de", description="Language code")) -> List[Dict[str, Any]]:
    """Get recommended voices for a language"""
    try:
        if language == "de":
            return GERMAN_VOICES[:6]  # Return top 6 German voices
        else:
            # Return some English voices as fallback
            return [
                {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "language": "en"},
                {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "language": "en"}
            ]
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
async def generate_tts(request: TTSRequest) -> Dict[str, Any]:
    """Generate TTS audio using ElevenLabs (direkt via HTTP, mit Cache)."""
    try:
        logger.info(f"Generating TTS for: {request.text[:50]}... with voice {request.voice_id}")

        api_key = getattr(settings, "ELEVENLABS_API_KEY", None)
        voice_id = request.voice_id

        # Cache-Key generieren
        cache_key_content = f"{request.text}:{voice_id}:{request.stability}:{request.similarity_boost}:{request.style}"
        cache_key = hashlib.sha256(cache_key_content.encode()).hexdigest()[:16]
        cache_file = TTS_CACHE_DIR / f"{cache_key}.mp3"

        # Cache verwenden, falls vorhanden
        if cache_file.exists():
            logger.info(f"💾 Using cached TTS audio: {cache_key}")
            return {
                "audio_url": f"/api/audio/tts/{cache_key}.mp3",
                "duration": 0.0,  # unbekannt
                "voice_id": voice_id,
                "cached": True,
                "format": "mp3"
            }

        if api_key:
            # Echte ElevenLabs API verwenden
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            payload = {
                "text": request.text,
                "model_id": getattr(settings, "ELEVENLABS_MODEL", "eleven_multilingual_v2"),
                "voice_settings": {
                    "stability": request.stability,
                    "similarity_boost": request.similarity_boost,
                    "style": request.style,
                    "use_speaker_boost": True
                }
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                audio_bytes = resp.content

            # In Cache schreiben
            cache_file.write_bytes(audio_bytes)
            logger.info(f"✅ Generated real TTS audio via ElevenLabs: {cache_key}")

            return {
                "audio_url": f"/api/audio/tts/{cache_key}.mp3",
                "duration": 0.0,
                "voice_id": voice_id,
                "cached": False,
                "format": "mp3"
            }

        # Fallback: Platzhalter-Audio
        logger.warning("Using placeholder audio (ElevenLabs not available)")
        return {
            "audio_url": f"/api/audio/tts/sample_{voice_id}.mp3",
            "duration": 3.5,
            "voice_id": voice_id,
            "cached": False,
            "warning": "Using placeholder audio"
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"ElevenLabs HTTP error: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=502, detail="TTS service error")
    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def voice_chat(
    voice_id: str = Query("ErXwobaYiN019PkySvjV"),
    message: str = Query(...)
) -> Dict[str, Any]:
    """Process chat message and return AI response with audio"""
    try:
        logger.info(f"Chat request: {message[:50]}... with voice {voice_id}")
        
        # Generate AI response
        reply = ""
        if OPENAI_AVAILABLE:
            try:
                # Use real OpenAI for response
                from api.models.schemas import ConversationRequest
                
                conversation_request = ConversationRequest(
                    message=message,
                    conversation_id="demo_chat",
                    system_prompt="""Du bist ein freundlicher KI-Assistent von VocalIQ. 
                    Antworte auf Deutsch, sei hilfsbereit und professionell. 
                    Halte deine Antworten kurz und prägnant (max 2-3 Sätze).""",
                    max_tokens=150,
                    temperature=0.7
                )
                
                response = await openai_service.create_conversation(
                    request=conversation_request,
                    user_id="demo_user"
                )
                reply = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                logger.warning(f"OpenAI failed, using fallback: {e}")
        
        # Fallback responses if OpenAI fails
        if not reply:
            ai_responses = {
                "Was ist VocalIQ?": "VocalIQ ist eine intelligente Voice-Agent-Plattform für Business-Telefonie. Wir ermöglichen natürliche Gespräche zwischen KI und Kunden über Telefon.",
                "Hallo": "Hallo! Ich bin Ihr VocalIQ Assistent. Wie kann ich Ihnen heute helfen?",
                "Guten Tag": "Guten Tag! Schön, dass Sie da sind. Wie kann ich Ihnen bei VocalIQ weiterhelfen?",
                "default": "Ich bin Ihr VocalIQ Assistent. Ich kann Ihnen bei allen Fragen zu unserer Voice-Agent-Plattform helfen."
            }
            
            # Find matching response or use default
            for key in ai_responses:
                if key.lower() in message.lower():
                    reply = ai_responses[key]
                    break
            if not reply:
                reply = ai_responses["default"]
        
        # Generate TTS for the reply
        audio_url = None
        if ELEVENLABS_AVAILABLE and elevenlabs_service.api_key:
            try:
                # Generate TTS
                tts_request = TTSRequest(
                    text=reply,
                    voice_id=voice_id,
                    stability=0.5,
                    similarity_boost=0.75
                )
                tts_response = await generate_tts(tts_request)
                audio_url = tts_response["audio_url"]
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")
        
        # Fallback audio URL
        if not audio_url:
            cache_key = _generate_cache_key(reply, voice_id)
            audio_url = f"/api/audio/tts/{cache_key}.mp3"
        
        return {
            "reply": reply,
            "audio_url": audio_url,
            "voice_id": voice_id,
            "duration": 5.0
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_voices() -> List[Dict[str, Any]]:
    """List all available voices"""
    return GERMAN_VOICES

@router.get("/{voice_id}")
async def get_voice(voice_id: str) -> Dict[str, Any]:
    """Get details for a specific voice"""
    for voice in GERMAN_VOICES:
        if voice["voice_id"] == voice_id:
            return voice
    raise HTTPException(status_code=404, detail="Voice not found")