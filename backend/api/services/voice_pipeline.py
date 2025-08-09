"""
Voice Pipeline Service
Handles audio processing, speech-to-text, AI conversation, and text-to-speech
"""

import asyncio
import base64
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import numpy as np
import io
import wave
import audioop

import openai
from openai import AsyncOpenAI
import httpx
from pydub import AudioSegment
from pydub.utils import which

from api.core.config import get_settings

logger = logging.getLogger(__name__)

# Set ffmpeg path for pydub
AudioSegment.converter = which("ffmpeg")

class VoicePipelineService:
    """
    Manages the complete voice processing pipeline:
    1. Receive audio from Twilio (μ-law 8kHz)
    2. Convert and buffer audio
    3. Speech-to-text with Whisper
    4. Process with GPT-4
    5. Text-to-speech with ElevenLabs
    6. Send audio back to Twilio
    """
    
    def __init__(self):
        settings = get_settings()
        self.sessions: Dict[str, Dict] = {}
        self.openai_client = None
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = getattr(settings, "ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        
        # Initialize OpenAI client if API key is available
        openai_api_key = settings.OPENAI_API_KEY
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        
    async def initialize_session(self, session_id: str, call_sid: str, from_number: str):
        """Initialize a new voice session"""
        logger.info(f"Initializing session: {session_id}")
        
        self.sessions[session_id] = {
            "call_sid": call_sid,
            "from_number": from_number,
            "audio_buffer": bytearray(),
            "conversation_history": [
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant for VocalIQ. 
                    You are speaking with someone on a phone call. 
                    Keep your responses concise and conversational. 
                    Be friendly and helpful. 
                    If asked about VocalIQ, explain that it's an advanced voice AI system 
                    that enables natural conversations between humans and AI."""
                }
            ],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "processing": False
        }
        
    async def process_audio(self, session_id: str, audio_bytes: bytes) -> Optional[bytes]:
        """
        Process incoming audio and generate response
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return None
            
        session = self.sessions[session_id]
        
        # Prevent concurrent processing
        if session["processing"]:
            return None
            
        # Add audio to buffer
        session["audio_buffer"].extend(audio_bytes)
        session["last_activity"] = datetime.utcnow()
        
        # Process when we have enough audio (roughly 1-2 seconds)
        # Twilio sends 8000 samples per second, 160 samples per packet
        if len(session["audio_buffer"]) >= 16000:  # About 2 seconds
            session["processing"] = True
            
            try:
                # Extract and clear buffer
                audio_data = bytes(session["audio_buffer"])
                session["audio_buffer"].clear()
                
                # Convert μ-law to PCM
                pcm_audio = self._ulaw_to_pcm(audio_data)
                
                # Transcribe audio
                transcript = await self._transcribe_audio(pcm_audio)
                
                if transcript and transcript.strip():
                    logger.info(f"User said: {transcript}")
                    
                    # Add to conversation history
                    session["conversation_history"].append({
                        "role": "user",
                        "content": transcript
                    })
                    
                    # Generate AI response
                    ai_response = await self._generate_response(session["conversation_history"])
                    
                    if ai_response:
                        logger.info(f"AI response: {ai_response}")
                        
                        # Add to conversation history
                        session["conversation_history"].append({
                            "role": "assistant",
                            "content": ai_response
                        })
                        
                        # Convert to speech
                        audio_response = await self._text_to_speech(ai_response)
                        
                        if audio_response:
                            # Convert to μ-law for Twilio
                            ulaw_audio = self._pcm_to_ulaw(audio_response)
                            return ulaw_audio
                            
            except Exception as e:
                logger.error(f"Error processing audio: {str(e)}")
            finally:
                session["processing"] = False
                
        return None
        
    def _ulaw_to_pcm(self, ulaw_data: bytes) -> bytes:
        """Convert μ-law audio to PCM"""
        try:
            # Convert μ-law to linear PCM
            pcm_data = audioop.ulaw2lin(ulaw_data, 2)
            # Resample from 8kHz to 16kHz for better quality
            pcm_data = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)[0]
            return pcm_data
        except Exception as e:
            logger.error(f"Error converting μ-law to PCM: {str(e)}")
            return ulaw_data
            
    def _pcm_to_ulaw(self, pcm_data: bytes) -> bytes:
        """Convert PCM audio to μ-law"""
        try:
            # Resample from 16kHz to 8kHz
            pcm_data = audioop.ratecv(pcm_data, 2, 1, 16000, 8000, None)[0]
            # Convert to μ-law
            ulaw_data = audioop.lin2ulaw(pcm_data, 2)
            return ulaw_data
        except Exception as e:
            logger.error(f"Error converting PCM to μ-law: {str(e)}")
            return pcm_data
            
    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper"""
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return None
            
        try:
            # Create a WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_data)
            
            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"
            
            # Transcribe with Whisper
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_buffer,
                language="en"
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
            
    async def _generate_response(self, conversation_history: list) -> Optional[str]:
        """Generate AI response using GPT-4"""
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return "I'm sorry, but I'm not properly configured to respond right now."
            
        try:
            # Generate response with GPT-4
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=conversation_history,
                max_tokens=150,  # Keep responses concise for phone calls
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble understanding. Could you please repeat that?"
            
    async def _text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs"""
        if not self.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            # Fallback: return silence
            return bytes(8000)  # 1 second of silence
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}/stream",
                    headers={
                        "xi-api-key": self.elevenlabs_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # ElevenLabs returns MP3, we need to convert to raw PCM
                    mp3_data = response.content
                    
                    # Convert MP3 to PCM using pydub
                    audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
                    # Convert to mono, 16kHz, 16-bit PCM
                    audio = audio.set_channels(1)
                    audio = audio.set_frame_rate(16000)
                    audio = audio.set_sample_width(2)
                    
                    # Get raw PCM data
                    pcm_data = audio.raw_data
                    return pcm_data
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None
            
    async def cleanup_session(self, session_id: str):
        """Clean up session resources"""
        if session_id in self.sessions:
            logger.info(f"Cleaning up session: {session_id}")
            del self.sessions[session_id]
            
    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "call_sid": session["call_sid"],
                "from_number": session["from_number"],
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "conversation_length": len(session["conversation_history"])
            }
        return None