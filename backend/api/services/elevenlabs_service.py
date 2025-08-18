"""
VocalIQ ElevenLabs Service
Text-to-Speech Integration mit ElevenLabs API
"""
import asyncio
import logging
import hashlib
import aiofiles
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from api.core.config import get_settings
from api.models.schemas import TTSRequest, TTSResponse

settings = get_settings()
logger = logging.getLogger(__name__)


class ElevenLabsService:
    """ElevenLabs Text-to-Speech Service mit Caching"""
    
    def __init__(self):
        if not settings.ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key not configured")
            self.api_key = None
        else:
            self.api_key = settings.ELEVENLABS_API_KEY
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.cache_dir = Path(settings.STORAGE_LOCAL_PATH) / "tts_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Voice cache
        self.voice_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_updated: Optional[datetime] = None
        
        # Audio cache (in-memory für häufig verwendete Audiodateien)
        self.audio_cache: Dict[str, bytes] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Default voice settings
        self.default_voice_settings = {
            "stability": settings.ELEVENLABS_VOICE_SETTINGS_STABILITY,
            "similarity_boost": settings.ELEVENLABS_VOICE_SETTINGS_SIMILARITY_BOOST,
            "style": 0.0,
            "use_speaker_boost": True
        }
    
    def _generate_cache_key(self, text: str, voice_id: str, settings: Dict[str, Any]) -> str:
        """Generate cache key für Audio-Files"""
        content = f"{text}:{voice_id}:{settings}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio from filesystem"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            
            if cache_file.exists():
                # Check if file is not too old (24 hours)
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - file_time < timedelta(hours=24):
                    async with aiofiles.open(cache_file, 'rb') as f:
                        audio_data = await f.read()
                    logger.info(f"💾 Using cached TTS audio: {cache_key}")
                    return audio_data
                else:
                    # Remove expired cache file
                    cache_file.unlink()
                    
        except Exception as e:
            logger.warning(f"Error accessing TTS cache {cache_key}: {str(e)}")
        
        return None
    
    async def _cache_audio(self, cache_key: str, audio_data: bytes):
        """Cache audio to filesystem"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            async with aiofiles.open(cache_file, 'wb') as f:
                await f.write(audio_data)
            logger.debug(f"💾 Cached TTS audio: {cache_key}")
        except Exception as e:
            logger.warning(f"Error caching TTS audio {cache_key}: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Text-to-Speech mit ElevenLabs API
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            # Generate cache key
            voice_settings = {
                "stability": request.stability,
                "similarity_boost": request.similarity_boost,
                "style": request.style
            }
            cache_key = self._generate_cache_key(request.text, request.voice_id, voice_settings)
            
            # Check cache first
            cached_audio = await self._get_cached_audio(cache_key)
            if cached_audio:
                return TTSResponse(
                    audio_url=f"/api/audio/tts/{cache_key}.mp3",
                    duration=len(cached_audio) / 32000,  # Rough estimate
                    format="mp3",
                    sample_rate=22050
                )
            
            logger.info(f"🎵 Synthesizing speech: '{request.text[:50]}...' with voice {request.voice_id}")
            
            # Prepare API request
            url = f"{self.base_url}/text-to-speech/{request.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            payload = {
                "text": request.text,
                "model_id": settings.ELEVENLABS_MODEL,
                "voice_settings": voice_settings
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                audio_data = response.content
            
            if not audio_data:
                raise ValueError("Empty audio response from ElevenLabs")
            
            # Cache the audio
            await self._cache_audio(cache_key, audio_data)
            
            # Calculate duration (rough estimate based on text length and speaking rate)
            words = len(request.text.split())
            estimated_duration = max(words / 2.5, 1.0)  # ~2.5 words per second
            
            logger.info(f"✅ TTS completed: {len(audio_data)} bytes, ~{estimated_duration:.1f}s")
            
            return TTSResponse(
                audio_url=f"/api/audio/tts/{cache_key}.mp3",
                duration=estimated_duration,
                format="mp3",
                sample_rate=22050
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("ElevenLabs rate limit exceeded")
                raise ValueError("TTS service temporarily unavailable due to rate limits")
            elif e.response.status_code == 401:
                logger.error("ElevenLabs API key invalid")
                raise ValueError("TTS service authentication failed")
            else:
                logger.error(f"ElevenLabs API error {e.response.status_code}: {e.response.text}")
                raise ValueError(f"TTS service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"TTS synthesis error: {str(e)}")
            raise
    
    async def get_cached_audio_file(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio file for serving"""
        return await self._get_cached_audio(cache_key)
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=3)
    )
    async def get_available_voices(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get available voices from ElevenLabs API
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        # Return cached voices if available and not too old
        if (not refresh and self.voice_cache and self.cache_updated and 
            datetime.utcnow() - self.cache_updated < timedelta(hours=6)):
            return list(self.voice_cache.values())
        
        try:
            logger.info("🎤 Fetching available voices from ElevenLabs")
            
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key, "Accept": "application/json"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                voices = data.get("voices", [])
            
            # Update cache
            self.voice_cache = {}
            for voice in voices:
                voice_info = {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", "unknown"),
                    "description": voice.get("description", ""),
                    "labels": voice.get("labels", {}),
                    "preview_url": voice.get("preview_url"),
                    "available_for_tiers": voice.get("available_for_tiers", [])
                }
                self.voice_cache[voice["voice_id"]] = voice_info
            
            self.cache_updated = datetime.utcnow()
            
            logger.info(f"✅ Loaded {len(voices)} voices from ElevenLabs")
            
            return list(self.voice_cache.values())
            
        except Exception as e:
            logger.error(f"Error fetching ElevenLabs voices: {str(e)}")
            raise
    
    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        if voice_id in self.voice_cache:
            return self.voice_cache[voice_id]
        
        # Fetch voices if not in cache
        await self.get_available_voices()
        
        if voice_id in self.voice_cache:
            return self.voice_cache[voice_id]
        else:
            raise ValueError(f"Voice {voice_id} not found")
    
    def get_recommended_voices(self, language: str = "de") -> List[Dict[str, Any]]:
        """Get recommended voices for a language"""
        if not self.voice_cache:
            return []
        
        # German voices (recommendations based on common use cases)
        german_recommendations = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel - clear female voice
            "AZnzlk1XvdvUeBnXmlld",  # Domi - professional male voice  
            "EXAVITQu4vr4xnSDxMaL",  # Bella - warm female voice
        ]
        
        english_recommendations = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "29vD33N1CtxCmqQRPOHJ",  # Drew
            "AZnzlk1XvdvUeBnXmlld",  # Domi
        ]
        
        recommendations = german_recommendations if language == "de" else english_recommendations
        
        result = []
        for voice_id in recommendations:
            if voice_id in self.voice_cache:
                result.append(self.voice_cache[voice_id])
        
        return result
    
    async def cleanup_cache(self, max_age_hours: int = 24):
        """Cleanup old cached audio files"""
        try:
            cleanup_count = 0
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for cache_file in self.cache_dir.glob("*.mp3"):
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    cleanup_count += 1
            
            if cleanup_count > 0:
                logger.info(f"🧹 Cleaned up {cleanup_count} old TTS cache files")
                
        except Exception as e:
            logger.warning(f"Error during TTS cache cleanup: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health Check für ElevenLabs Service"""
        if not self.api_key:
            return {
                "status": "not_configured",
                "error": "ElevenLabs API key not set"
            }
        
        try:
            # Test mit Voice-List-Anfrage
            voices = await self.get_available_voices()
            
            # Check cache statistics
            cache_files = list(self.cache_dir.glob("*.mp3"))
            cache_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                "status": "healthy",
                "available_voices": len(voices),
                "cached_audio_files": len(cache_files),
                "cache_size_mb": round(cache_size / 1024 / 1024, 2),
                "default_voice": settings.ELEVENLABS_VOICE_ID
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global Service Instance
elevenlabs_service = ElevenLabsService()