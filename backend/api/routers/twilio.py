"""
Twilio Voice Integration Router
Handles incoming calls, WebSocket connections, and voice streaming
"""

import json
import base64
import asyncio
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.request_validator import RequestValidator
import logging
from pydantic import BaseModel

from api.core.config import get_settings
settings = get_settings()
from api.services.voice_pipeline import VoicePipelineService
from api.services.twilio_service import TwilioService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["twilio"])

# Initialize services
voice_pipeline = VoicePipelineService()
twilio_service = TwilioService()

class CallStatus(BaseModel):
    CallSid: str
    CallStatus: str
    From: Optional[str] = None
    To: Optional[str] = None
    Direction: Optional[str] = None

@router.post("/incoming")
async def handle_incoming_call(request: Request):
    """
    Handle incoming phone calls from Twilio
    Returns TwiML to establish WebSocket connection
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "")
        from_number = form_data.get("From", "")
        to_number = form_data.get("To", "")
        
        logger.info(f"Incoming call: {call_sid} from {from_number} to {to_number}")
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Initial greeting
        response.say(
            "Hello! Welcome to VocalIQ. I'm your AI assistant. How can I help you today?",
            voice="alice"
        )
        
        # For now, just use simple response without WebSocket (for testing)
        # TODO: Re-enable WebSocket once basic call works
        response.say(
            "Thank you for calling. This is a test of the VocalIQ system. Goodbye!",
            voice="alice"
        )
        response.hangup()
        
        # # Get ngrok URL from environment or use configured base URL
        # base_url = getattr(settings, "NGROK_URL", "https://a0f5cd136d89.ngrok-free.app")
        # websocket_url = f"wss://{base_url.replace('https://', '').replace('http://', '')}/api/twilio/websocket"
        # 
        # # Connect to WebSocket for bidirectional streaming
        # connect = Connect()
        # stream = connect.stream(url=websocket_url)
        # stream.parameter(name="call_sid", value=call_sid)
        # stream.parameter(name="from_number", value=from_number)
        # response.append(connect)
        
        return Response(
            content=str(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        response = VoiceResponse()
        response.say("Sorry, I'm having trouble connecting. Please try again later.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming
    Handles bidirectional audio between Twilio and our voice pipeline
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    # Initialize session
    session_id = None
    call_sid = None
    stream_sid = None
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data["event"] == "start":
                # Initialize streaming session
                start_data = data["start"]
                stream_sid = start_data["streamSid"]
                call_sid = start_data["callSid"]
                session_id = f"{call_sid}_{stream_sid}"
                
                # Get custom parameters
                custom_params = start_data.get("customParameters", {})
                from_number = custom_params.get("from_number", "Unknown")
                
                logger.info(f"Stream started: {session_id} from {from_number}")
                
                # Initialize voice pipeline for this session
                await voice_pipeline.initialize_session(
                    session_id=session_id,
                    call_sid=call_sid,
                    from_number=from_number
                )
                
            elif data["event"] == "media":
                # Process incoming audio
                media_data = data["media"]
                audio_payload = media_data["payload"]
                
                # Decode base64 audio (μ-law 8kHz)
                audio_bytes = base64.b64decode(audio_payload)
                
                # Process audio through voice pipeline
                response_audio = await voice_pipeline.process_audio(
                    session_id=session_id,
                    audio_bytes=audio_bytes
                )
                
                # If we have response audio, send it back
                if response_audio:
                    # Encode audio to base64
                    encoded_audio = base64.b64encode(response_audio).decode('utf-8')
                    
                    # Send audio back to Twilio
                    media_message = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": encoded_audio
                        }
                    }
                    await websocket.send_text(json.dumps(media_message))
                    
            elif data["event"] == "stop":
                # Clean up session
                logger.info(f"Stream stopped: {session_id}")
                if session_id:
                    await voice_pipeline.cleanup_session(session_id)
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        if session_id:
            await voice_pipeline.cleanup_session(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if session_id:
            await voice_pipeline.cleanup_session(session_id)
    finally:
        try:
            await websocket.close()
        except:
            pass

@router.post("/status")
async def handle_call_status(request: Request):
    """
    Handle call status updates from Twilio
    """
    try:
        form_data = await request.form()
        call_status = CallStatus(
            CallSid=form_data.get("CallSid", ""),
            CallStatus=form_data.get("CallStatus", ""),
            From=form_data.get("From"),
            To=form_data.get("To"),
            Direction=form_data.get("Direction")
        )
        
        logger.info(f"Call status update: {call_status.CallSid} - {call_status.CallStatus}")
        
        # Handle different call statuses
        if call_status.CallStatus == "completed":
            # Clean up any resources
            await voice_pipeline.cleanup_session(call_status.CallSid)
            
        return Response(content="", status_code=200)
        
    except Exception as e:
        logger.error(f"Error handling call status: {str(e)}")
        return Response(content="", status_code=200)

@router.post("/fallback")
async def handle_fallback(request: Request):
    """
    Fallback handler for errors
    """
    try:
        form_data = await request.form()
        error_code = form_data.get("ErrorCode", "")
        error_message = form_data.get("ErrorMessage", "")
        
        logger.error(f"Twilio fallback triggered: {error_code} - {error_message}")
        
        response = VoiceResponse()
        response.say(
            "I apologize, but I'm experiencing technical difficulties. Please try again later.",
            voice="alice"
        )
        response.hangup()
        
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in fallback handler: {str(e)}")
        response = VoiceResponse()
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

@router.get("/test")
async def test_twilio_connection():
    """
    Test endpoint to verify Twilio router is working
    """
    return {
        "status": "ok",
        "message": "Twilio router is active",
        "endpoints": [
            "/api/twilio/incoming",
            "/api/twilio/websocket",
            "/api/twilio/status",
            "/api/twilio/fallback"
        ]
    }