"""
VocalIQ Twilio Service
Twilio-Integration für Voice-Calls mit WebSocket-Support
"""
import json
import base64
import asyncio
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from twilio.rest import Client as TwilioClient
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Stream
from fastapi import HTTPException, status
import aiofiles
import hashlib
import hmac

from api.core.config import get_settings
from api.models.schemas import CallRequest, CallStatus, CallDirection, AudioFormat

settings = get_settings()
logger = logging.getLogger(__name__)


class TwilioWebSocketHandler:
    """WebSocket-Handler für Twilio Audio-Streams"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_buffers: Dict[str, List[bytes]] = {}
    
    async def handle_stream_start(self, stream_sid: str, call_sid: str, track: str):
        """Handle Twilio Stream Start"""
        logger.info(f"🎵 Audio stream started: {stream_sid} for call {call_sid}")
        
        self.active_streams[stream_sid] = {
            "call_sid": call_sid,
            "track": track,
            "started_at": datetime.utcnow(),
            "bytes_received": 0,
            "packets_count": 0
        }
        
        self.stream_buffers[stream_sid] = []
    
    async def handle_media_packet(self, stream_sid: str, payload: Dict[str, Any]):
        """Handle incoming audio packets"""
        if stream_sid not in self.active_streams:
            logger.warning(f"Received media for unknown stream: {stream_sid}")
            return
        
        try:
            # Decode base64 audio data (μ-law format)
            audio_data = base64.b64decode(payload.get("payload", ""))
            
            # Buffer the audio data
            self.stream_buffers[stream_sid].append(audio_data)
            
            # Update stream stats
            stream_info = self.active_streams[stream_sid]
            stream_info["bytes_received"] += len(audio_data)
            stream_info["packets_count"] += 1
            
            # Process audio in chunks (every 1 second ≈ 160 packets)
            if stream_info["packets_count"] % 160 == 0:
                await self._process_audio_chunk(stream_sid)
            
            logger.debug(f"📦 Media packet for {stream_sid}: {len(audio_data)} bytes")
            
        except Exception as e:
            logger.error(f"Error handling media packet for {stream_sid}: {str(e)}")
    
    async def handle_stream_stop(self, stream_sid: str):
        """Handle Twilio Stream Stop"""
        if stream_sid not in self.active_streams:
            return
        
        logger.info(f"🛑 Audio stream stopped: {stream_sid}")
        
        # Process remaining audio
        await self._process_audio_chunk(stream_sid, final=True)
        
        # Cleanup
        stream_info = self.active_streams.pop(stream_sid, {})
        self.stream_buffers.pop(stream_sid, [])
        
        logger.info(
            f"Stream {stream_sid} stats: "
            f"{stream_info.get('bytes_received', 0)} bytes, "
            f"{stream_info.get('packets_count', 0)} packets"
        )
    
    async def _process_audio_chunk(self, stream_sid: str, final: bool = False):
        """Process buffered audio chunk"""
        if stream_sid not in self.stream_buffers:
            return
        
        audio_buffer = self.stream_buffers[stream_sid]
        if not audio_buffer:
            return
        
        try:
            # Combine all audio packets
            combined_audio = b''.join(audio_buffer)
            
            # Clear buffer
            self.stream_buffers[stream_sid] = []
            
            # TODO: Send to speech-to-text service (OpenAI Whisper)
            # TODO: Process with AI conversation service
            # TODO: Generate response with TTS
            # TODO: Send audio back to Twilio
            
            logger.info(
                f"🎧 Processing audio chunk for {stream_sid}: "
                f"{len(combined_audio)} bytes"
            )
            
            # Placeholder for audio processing
            if len(combined_audio) > 0:
                await self._placeholder_audio_processing(stream_sid, combined_audio)
            
        except Exception as e:
            logger.error(f"Error processing audio chunk for {stream_sid}: {str(e)}")
    
    async def _placeholder_audio_processing(self, stream_sid: str, audio_data: bytes):
        """Placeholder für Audio-Processing (wird später durch AI-Services ersetzt)"""
        # Simuliere Audio-Processing
        await asyncio.sleep(0.1)
        
        # In echter Implementierung:
        # 1. Audio zu Whisper API senden
        # 2. Text zu OpenAI GPT-4 senden
        # 3. Antwort zu ElevenLabs TTS senden
        # 4. Generated Audio zurück zu Twilio senden
        
        logger.debug(f"🤖 [PLACEHOLDER] Processed {len(audio_data)} bytes for {stream_sid}")


class TwilioService:
    """Hauptklasse für Twilio-Integration"""
    
    def __init__(self):
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            self.client = None
            self.validator = None
        else:
            self.client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        
        self.websocket_handler = TwilioWebSocketHandler()
    
    def validate_webhook(self, url: str, params: Dict[str, str], signature: str) -> bool:
        """Validiere Twilio Webhook-Signature"""
        if not self.validator or not settings.TWILIO_WEBHOOK_VALIDATE:
            return True
        
        return self.validator.validate(url, params, signature)
    
    async def create_outbound_call(
        self, 
        to_number: str, 
        from_number: Optional[str] = None,
        webhook_url: str = "",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Erstelle ausgehenden Anruf"""
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Twilio service not configured"
            )
        
        try:
            # Use configured Twilio number if none provided
            from_number = from_number or settings.TWILIO_PHONE_NUMBER
            if not from_number:
                raise ValueError("No from_number configured")
            
            # Create TwiML for call
            twiml_url = f"{webhook_url}/twiml/voice_start"
            
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=twiml_url,
                status_callback=f"{webhook_url}/webhooks/call_status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                timeout=timeout,
                record=False  # We'll handle recording via streaming
            )
            
            logger.info(f"📞 Created outbound call {call.sid} to {to_number}")
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": "outbound",
                "to": to_number,
                "from": from_number,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create outbound call: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create call: {str(e)}"
            )
    
    def generate_voice_twiml(
        self, 
        message: Optional[str] = None,
        enable_streaming: bool = True
    ) -> str:
        """Generiere TwiML für Voice-Response"""
        response = VoiceResponse()
        
        if message:
            # Say the message
            response.say(message, voice="alice", language="de-DE")
        
        if enable_streaming:
            # Start bidirectional audio streaming
            start = response.connect()
            stream = Stream(
                url=f"wss://{settings.API_BASE_URL.replace('http://', '').replace('https://', '')}/ws/media-stream",
                track="both_tracks"
            )
            start.append(stream)
        else:
            # Gather input or hang up
            response.hangup()
        
        return str(response)
    
    def generate_gather_twiml(
        self,
        message: str,
        num_digits: int = 1,
        timeout: int = 10,
        action_url: str = ""
    ) -> str:
        """Generiere TwiML für Input-Gathering"""
        response = VoiceResponse()
        
        gather = response.gather(
            num_digits=num_digits,
            timeout=timeout,
            action=action_url
        )
        gather.say(message, voice="alice", language="de-DE")
        
        # Fallback if no input
        response.say("Keine Eingabe erhalten. Auf Wiederhören.", voice="alice", language="de-DE")
        response.hangup()
        
        return str(response)
    
    async def handle_call_status_update(
        self, 
        call_sid: str, 
        call_status: str,
        call_data: Dict[str, Any]
    ):
        """Handle Call-Status Updates von Twilio"""
        logger.info(f"📱 Call {call_sid} status update: {call_status}")
        
        # Map Twilio status to our CallStatus enum
        status_mapping = {
            "queued": CallStatus.INITIATED,
            "initiated": CallStatus.INITIATED,
            "ringing": CallStatus.RINGING,
            "in-progress": CallStatus.ANSWERED,
            "completed": CallStatus.COMPLETED,
            "failed": CallStatus.FAILED,
            "busy": CallStatus.BUSY,
            "no-answer": CallStatus.NO_ANSWER,
            "canceled": CallStatus.CANCELLED
        }
        
        mapped_status = status_mapping.get(call_status, CallStatus.FAILED)
        
        # TODO: Update call record in database
        # TODO: Trigger webhooks if configured
        # TODO: Update analytics
        
        call_info = {
            "call_sid": call_sid,
            "status": mapped_status.value,
            "twilio_status": call_status,
            "updated_at": datetime.utcnow().isoformat(),
            **call_data
        }
        
        logger.info(f"📊 Call info updated: {call_info}")
        
        return call_info
    
    async def get_call_info(self, call_sid: str) -> Dict[str, Any]:
        """Hole Call-Informationen von Twilio"""
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Twilio service not configured"
            )
        
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from": call.from_,
                "to": call.to,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "duration": call.duration,
                "price": float(call.price) if call.price else None,
                "price_unit": call.price_unit
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch call info for {call_sid}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call not found: {call_sid}"
            )
    
    async def hangup_call(self, call_sid: str) -> bool:
        """Beende einen aktiven Anruf"""
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Twilio service not configured"
            )
        
        try:
            call = self.client.calls(call_sid).update(status="completed")
            logger.info(f"📱 Hung up call {call_sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hang up call {call_sid}: {str(e)}")
            return False


# Global Service Instance
twilio_service = TwilioService()