"""
VocalIQ Call Management Routes
Twilio-basierte Voice-Call-Verwaltung
"""
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel

from api.core.security import get_current_user_token, TokenPayload, require_scopes
from api.models.schemas import CallRequest, CallResponse, CallStatus, APIResponse, ErrorResponse
from api.services.twilio_service import twilio_service
from api.middleware.rate_limiting import medium_rate_limit
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from api.core.database import get_session
from api.repositories.call_repository import CallRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["Call Management"])


class CallWebhookData(BaseModel):
    """Twilio Webhook Data"""
    CallSid: str
    CallStatus: str
    From: str
    To: str
    Direction: str
    CallDuration: str = "0"
    RecordingUrl: str = ""


class TwiMLResponse(BaseModel):
    """TwiML Response Wrapper"""
    twiml: str


class CallRecordResponse(BaseModel):
    id: int
    phone: str
    direction: str
    status: str
    duration: str
    timestamp: str
    transcript: str | None = None
    customerName: str | None = None
    intent: str | None = None


@router.post("/outbound", response_model=CallResponse)
async def create_outbound_call(
    call_request: CallRequest,
    token: TokenPayload = Depends(require_scopes(["calls", "admin"]))
):
    """
    Erstelle einen ausgehenden Anruf
    """
    try:
        logger.info(
            f"🚀 Creating outbound call from user {token.user_id} "
            f"to {call_request.to_number}"
        )
        # Create call via Twilio
        call_data = await twilio_service.create_outbound_call(
            to_number=call_request.to_number,
            from_number=call_request.from_number,
            webhook_url=f"{settings.API_BASE_URL}/api/calls/twiml/voice_start",
            timeout=30
        )
        # Map to our response format
        call_response = CallResponse(
            id=call_data["call_sid"],
            status=CallStatus.INITIATED,
            direction="outbound",
            from_number=call_data["from"],
            to_number=call_data["to"],
            duration=None,
            cost=None,
            created_at=call_data["created_at"]
        )
        return call_response
    except Exception as e:
        logger.error(f"Failed to create outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create call: {str(e)}"
        )


@router.get("/", response_model=list[CallRecordResponse])
async def list_calls(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    token: TokenPayload = Depends(require_scopes(["calls", "user"]))
):
    """
    Liste der letzten Anrufe (für Dashboard/History)
    """
    repo = CallRepository(session)
    calls = await repo.get_calls_by_organization(
        organization_id=token.organization_id or 1,
        limit=limit
    )
    def _fmt_duration(seconds: int | None) -> str:
        if not seconds:
            return "0:00"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    results: list[CallRecordResponse] = []
    for c in calls:
        results.append(CallRecordResponse(
            id=c.id,
            phone=c.from_number if c.direction.value == "inbound" else c.to_number,
            direction=c.direction.value,
            status=(
                "completed" if c.status.value == "completed" else
                "failed" if c.status.value == "failed" else
                "in-progress"
            ),
            duration=_fmt_duration(c.duration_seconds),
            timestamp=(c.created_at.isoformat() if getattr(c, "created_at", None) else (c.start_time.isoformat() if c.start_time else datetime.utcnow().isoformat())),
            transcript=c.transcription or "",
            customerName=getattr(c, "caller_name", None),
            intent=None
        ))
    return results

# zusätzliche Route ohne Slash (für /api/calls), aus OpenAPI ausgeblendet
router.add_api_route(
    path="",
    endpoint=list_calls,
    methods=["GET"],
    include_in_schema=False
)


@router.get("/{id:int}", response_model=CallRecordResponse)
async def get_call_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    token: TokenPayload = Depends(require_scopes(["calls", "user"]))
):
    repo = CallRepository(session)
    c = await repo.get_by_id(id)
    if not c:
        raise HTTPException(status_code=404, detail="Call not found")
    def _fmt_duration(seconds: int | None) -> str:
        if not seconds:
            return "0:00"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    return CallRecordResponse(
        id=c.id,
        phone=c.from_number if c.direction.value == "inbound" else c.to_number,
        direction=c.direction.value,
        status=(
            "completed" if c.status.value == "completed" else
            "failed" if c.status.value == "failed" else
            "in-progress"
        ),
        duration=_fmt_duration(c.duration_seconds),
        timestamp=(c.created_at.isoformat() if getattr(c, "created_at", None) else (c.start_time.isoformat() if c.start_time else datetime.utcnow().isoformat())),
        transcript=c.transcription or "",
        customerName=getattr(c, "caller_name", None),
        intent=None
    )


@router.get("/{call_sid}", response_model=CallResponse)
async def get_call_info(
    call_sid: str,
    token: TokenPayload = Depends(require_scopes(["calls", "user"]))
):
    """
    Hole Call-Informationen
    """
    try:
        call_info = await twilio_service.get_call_info(call_sid)
        if not call_info:
            raise HTTPException(status_code=404, detail="Call not found")
        call_response = CallResponse(
            id=call_info["sid"],
            status=CallStatus(call_info["status"]),
            direction=call_info["direction"],
            from_number=call_info["from"],
            to_number=call_info["to"],
            duration=call_info["duration"],
            cost=None,
            created_at=call_info["start_time"]
        )
        return call_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch call information"
        )


@router.post("/{call_sid}/hangup")
async def hangup_call(
    call_sid: str,
    token: TokenPayload = Depends(require_scopes(["calls", "admin"]))
):
    """
    Beende einen aktiven Anruf
    """
    try:
        success = await twilio_service.hangup_call(call_sid)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to hang up call"
            )
        
        return {"message": "Call terminated successfully", "call_sid": call_sid}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error hanging up call {call_sid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate call"
        )


# Twilio Webhook Endpoints (No authentication required)
@router.post("/webhooks/call_status")
async def twilio_call_status_webhook(request: Request):
    """
    Twilio Call Status Webhook
    """
    try:
        # Parse form data
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate Twilio signature if enabled
        if hasattr(twilio_service, 'validate_webhook'):
            signature = request.headers.get("X-Twilio-Signature", "")
            url = str(request.url)
            
            if not twilio_service.validate_webhook(url, webhook_data, signature):
                logger.warning(f"Invalid Twilio webhook signature from {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid webhook signature"
                )
        
        # Process call status update
        call_sid = webhook_data.get("CallSid")
        call_status = webhook_data.get("CallStatus")
        
        if not call_sid or not call_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required webhook parameters"
            )
        
        # Handle status update
        call_info = await twilio_service.handle_call_status_update(
            call_sid=call_sid,
            call_status=call_status,
            call_data=webhook_data
        )
        
        logger.info(f"📞 Processed call status webhook: {call_sid} -> {call_status}")
        
        # Return empty response (Twilio expects 200)
        return Response(status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing call status webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/twiml/voice_start", response_class=Response)
async def voice_start_twiml(request: Request):
    """
    TwiML Response für Call-Start
    """
    try:
        # Parse Twilio request data
        form_data = await request.form()
        call_data = dict(form_data)
        
        call_sid = call_data.get("CallSid")
        from_number = call_data.get("From")
        to_number = call_data.get("To")
        
        logger.info(f"🎵 Starting voice call {call_sid} from {from_number} to {to_number}")
        
        # Generate TwiML for bidirectional streaming
        twiml = twilio_service.generate_voice_twiml(
            message="Hallo! Ich bin Ihr VocalIQ Assistent. Wie kann ich Ihnen helfen?",
            enable_streaming=True
        )
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error generating voice TwiML: {str(e)}")
        
        # Fallback TwiML
        fallback_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="de-DE">
        Entschuldigung, es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.
    </Say>
    <Hangup/>
</Response>'''
        
        return Response(content=fallback_twiml, media_type="application/xml")


# WebSocket Handler für Media-Streaming
@router.websocket("/ws/media-stream")
async def websocket_media_stream(websocket: WebSocket):
    """
    WebSocket-Endpoint für Twilio Media-Streaming
    """
    await websocket.accept()
    
    logger.info("🎧 WebSocket media stream connected")
    
    try:
        while True:
            # Receive data from Twilio
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                event = message.get("event")
                stream_sid = message.get("streamSid")
                
                if event == "connected":
                    logger.info("📱 Twilio media stream connected")
                    
                elif event == "start":
                    # Stream started
                    call_sid = message.get("start", {}).get("callSid")
                    tracks = message.get("start", {}).get("tracks", ["inbound"])
                    
                    await twilio_service.websocket_handler.handle_stream_start(
                        stream_sid, call_sid, tracks[0]
                    )
                    
                elif event == "media":
                    # Audio data received
                    media = message.get("media", {})
                    await twilio_service.websocket_handler.handle_media_packet(
                        stream_sid, media
                    )
                    
                elif event == "stop":
                    # Stream stopped
                    await twilio_service.websocket_handler.handle_stream_stop(stream_sid)
                    
                else:
                    logger.debug(f"Unknown WebSocket event: {event}")
                    
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from WebSocket")
                continue
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket media stream disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@router.get("/health")
async def calls_health():
    """
    Call Service Health Check
    """
    # Check Twilio connection
    twilio_status = "healthy" if twilio_service.client else "not_configured"
    
    return {
        "status": "healthy",
        "service": "call_management",
        "twilio": twilio_status,
        "active_streams": len(twilio_service.websocket_handler.active_streams),
        "timestamp": datetime.utcnow().isoformat()
    }


# Import settings at the end to avoid circular imports
from api.core.config import get_settings
from datetime import datetime
settings = get_settings()