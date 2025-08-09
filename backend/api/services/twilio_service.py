"""
Twilio Service
Handles Twilio-specific operations and validations
"""

import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse
from twilio.base.exceptions import TwilioRestException

from api.core.config import get_settings

logger = logging.getLogger(__name__)

class TwilioService:
    """
    Service for Twilio operations
    """
    
    def __init__(self):
        settings = get_settings()
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        # Initialize Twilio client if credentials are available
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.validator = RequestValidator(self.auth_token)
        else:
            self.client = None
            self.validator = None
            logger.warning("Twilio credentials not configured")

        # Simple websocket handler facade (delegates to VoicePipelineService)
        try:
            from api.services.voice_pipeline import VoicePipelineService
            self._voice_pipeline = VoicePipelineService()
            self.websocket_handler = self._WebSocketHandler(self._voice_pipeline)
        except Exception as e:
            logger.warning(f"Voice pipeline not available: {e}")
            self._voice_pipeline = None
            self.websocket_handler = None
    
    def validate_request(self, url: str, params: Dict[str, Any], signature: str) -> bool:
        """
        Validate that a request came from Twilio
        """
        if not self.validator:
            logger.warning("Twilio validator not initialized, skipping validation")
            return True  # Skip validation in development
            
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error validating Twilio request: {str(e)}")
            return False

    # Backwards-compatible wrapper expected by routes
    def validate_webhook(self, url: str, params: Dict[str, Any], signature: str) -> bool:
        return self.validate_request(url, params, signature)
    
    def create_error_response(self, message: str = "An error occurred") -> str:
        """
        Create a TwiML error response
        """
        response = VoiceResponse()
        response.say(message, voice="alice")
        response.hangup()
        return str(response)
        
    def create_greeting_response(self, webhook_url: str) -> str:
        """
        Create a TwiML greeting response with WebSocket stream
        """
        response = VoiceResponse()
        
        # Initial greeting
        response.say(
            "Hello\! Welcome to VocalIQ. I'm your AI assistant. How can I help you today?",
            voice="alice"
        )
        
        # Connect to WebSocket
        connect = response.connect()
        connect.stream(url=webhook_url)
        
        return str(response)

    async def create_outbound_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        webhook_url: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Create an outbound call via Twilio"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        try:
            from_num = from_number or self.phone_number
            call = self.client.calls.create(
                to=to_number,
                from_=from_num,
                url=webhook_url or ""
            )
            return {
                "call_sid": call.sid,
                "from": from_num,
                "to": to_number,
                "created_at": getattr(call, 'date_created', None).isoformat() if getattr(call, 'date_created', None) else None
            }
        except TwilioRestException as e:
            logger.error(f"Twilio create call failed: {e}")
            raise

    async def hangup_call(self, call_sid: str) -> bool:
        """Terminate an active call"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        try:
            call = self.client.calls(call_sid).update(status="completed")
            return call.status == "completed"
        except TwilioRestException as e:
            logger.error(f"Twilio hangup failed: {e}")
            return False

    class _WebSocketHandler:
        """Minimal handler delegating to VoicePipelineService"""
        def __init__(self, voice_pipeline: "VoicePipelineService"):
            self.voice_pipeline = voice_pipeline
            self.active_streams: Dict[str, Dict[str, Any]] = {}

        async def handle_stream_start(self, stream_sid: str, call_sid: str, track: str):
            session_id = f"{call_sid}_{stream_sid}"
            await self.voice_pipeline.initialize_session(session_id=session_id, call_sid=call_sid, from_number="unknown")
            self.active_streams[stream_sid] = {"session_id": session_id, "call_sid": call_sid, "track": track}

        async def handle_media_packet(self, stream_sid: str, media: Dict[str, Any]):
            import base64
            session = self.active_streams.get(stream_sid)
            if not session:
                return
            payload = media.get("payload")
            if not payload:
                return
            audio_bytes = base64.b64decode(payload)
            response_ulaw = await self.voice_pipeline.process_audio(session_id=session["session_id"], audio_bytes=audio_bytes)
            # Returning audio is handled by the websocket endpoint itself
            return response_ulaw

        async def handle_stream_stop(self, stream_sid: str):
            session = self.active_streams.pop(stream_sid, None)
            if session:
                await self.voice_pipeline.cleanup_session(session["session_id"])
            
    async def get_call_info(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a call from Twilio
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return None
            
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "from": call.from_,
                "to": call.to,
                "status": call.status,
                "direction": call.direction,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None
            }
        except Exception as e:
            logger.error(f"Error fetching call info: {str(e)}")
            return None
            
    async def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send an SMS message
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
            
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            logger.info(f"SMS sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
            
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to E.164 format
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present
        if len(digits) == 10:  # US number without country code
            digits = '1' + digits
            
        # Add + prefix
        if not digits.startswith('+'):
            digits = '+' + digits
            
        return digits

# Create singleton instance
twilio_service = TwilioService()
