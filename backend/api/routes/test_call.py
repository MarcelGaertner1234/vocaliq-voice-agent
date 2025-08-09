"""
Test Call API Routes for Testing Voice Agent
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import uuid

from ..database import get_session
from ..auth import get_current_user
from ..services.voice_pipeline import VoicePipeline

router = APIRouter(prefix="/api/test-call", tags=["Test Call"])

# Store active test calls
active_test_calls: Dict[str, Dict[str, Any]] = {}

class TestCallService:
    """Service for managing test calls"""
    
    @staticmethod
    async def start_test_call(user_id: str, scenario: str = "general") -> Dict[str, Any]:
        """Start a new test call"""
        call_id = str(uuid.uuid4())
        
        # Initialize test call
        test_call = {
            "id": call_id,
            "user_id": user_id,
            "status": "connecting",
            "scenario": scenario,
            "started_at": datetime.utcnow().isoformat(),
            "duration": 0,
            "transcript": []
        }
        
        active_test_calls[call_id] = test_call
        
        # Simulate connection
        await asyncio.sleep(2)
        test_call["status"] = "active"
        
        # Add initial agent greeting based on scenario
        greetings = {
            "general": "Hello! Thank you for calling. How can I help you today?",
            "reservation": "Hello! Thank you for calling. Would you like to make a reservation?",
            "business_hours": "Hello! You've reached our business. How can I assist you with our hours or services?",
            "technical_support": "Hello! This is technical support. What issue can I help you with today?",
            "emergency": "Emergency response activated. Please state the nature of your emergency."
        }
        
        greeting = greetings.get(scenario, greetings["general"])
        test_call["transcript"].append({
            "speaker": "agent",
            "text": greeting,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return test_call
    
    @staticmethod
    async def end_test_call(call_id: str) -> Dict[str, Any]:
        """End a test call"""
        if call_id not in active_test_calls:
            raise ValueError("Test call not found")
        
        test_call = active_test_calls[call_id]
        test_call["status"] = "ending"
        
        # Add goodbye message
        test_call["transcript"].append({
            "speaker": "agent",
            "text": "Thank you for calling. Goodbye!",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await asyncio.sleep(1)
        
        test_call["status"] = "ended"
        test_call["ended_at"] = datetime.utcnow().isoformat()
        
        # Calculate duration
        started = datetime.fromisoformat(test_call["started_at"])
        ended = datetime.fromisoformat(test_call["ended_at"])
        test_call["duration"] = int((ended - started).total_seconds())
        
        # Remove from active calls
        del active_test_calls[call_id]
        
        return test_call
    
    @staticmethod
    async def add_user_input(call_id: str, text: str) -> Dict[str, Any]:
        """Add user input to test call"""
        if call_id not in active_test_calls:
            raise ValueError("Test call not found")
        
        test_call = active_test_calls[call_id]
        
        # Add user message
        test_call["transcript"].append({
            "speaker": "user",
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Simulate agent response
        await asyncio.sleep(1)
        
        # Generate response based on input
        response = await TestCallService.generate_response(text, test_call["scenario"])
        
        test_call["transcript"].append({
            "speaker": "agent",
            "text": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return test_call
    
    @staticmethod
    async def generate_response(user_input: str, scenario: str) -> str:
        """Generate agent response based on user input"""
        user_input_lower = user_input.lower()
        
        # Scenario-specific responses
        if scenario == "reservation":
            if "table" in user_input_lower or "reservation" in user_input_lower:
                return "Certainly! For how many people would you like to make a reservation?"
            elif any(num in user_input_lower for num in ["2", "3", "4", "5", "6"]):
                return "Perfect! What date and time would you prefer?"
            elif "tonight" in user_input_lower or "today" in user_input_lower:
                return "Let me check availability for tonight. We have tables available at 7 PM and 8:30 PM. Which would you prefer?"
        
        elif scenario == "business_hours":
            if "hours" in user_input_lower or "open" in user_input_lower:
                return "We're open Monday through Friday from 9 AM to 6 PM, and Saturdays from 10 AM to 4 PM. We're closed on Sundays."
        
        elif scenario == "technical_support":
            if "problem" in user_input_lower or "issue" in user_input_lower:
                return "I understand you're experiencing an issue. Can you describe what's happening in more detail?"
            elif "password" in user_input_lower:
                return "I can help you reset your password. Please provide your account email address."
        
        # Default responses
        if "yes" in user_input_lower:
            return "Great! How can I assist you further?"
        elif "no" in user_input_lower:
            return "I understand. Is there anything else I can help you with?"
        elif "thank" in user_input_lower:
            return "You're welcome! Is there anything else you need?"
        elif "bye" in user_input_lower or "goodbye" in user_input_lower:
            return "Thank you for calling. Have a great day!"
        else:
            return "I understand. Let me help you with that. Could you provide more details?"

@router.post("/start")
async def start_test_call(
    scenario: str = "general",
    current_user: dict = Depends(get_current_user)
):
    """Start a new test call"""
    try:
        test_call = await TestCallService.start_test_call(
            user_id=current_user.get("id", "unknown"),
            scenario=scenario
        )
        return test_call
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{call_id}/end")
async def end_test_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a test call"""
    try:
        test_call = await TestCallService.end_test_call(call_id)
        return test_call
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{call_id}/status")
async def get_test_call_status(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get test call status"""
    if call_id not in active_test_calls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test call not found"
        )
    
    test_call = active_test_calls[call_id]
    
    # Calculate current duration
    if test_call["status"] == "active":
        started = datetime.fromisoformat(test_call["started_at"])
        test_call["duration"] = int((datetime.utcnow() - started).total_seconds())
    
    return test_call

@router.post("/{call_id}/input")
async def add_user_input(
    call_id: str,
    input_data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Add user input to test call"""
    try:
        text = input_data.get("text", "")
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text input is required"
            )
        
        test_call = await TestCallService.add_user_input(call_id, text)
        return test_call
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.websocket("/ws/{call_id}")
async def test_call_websocket(
    websocket: WebSocket,
    call_id: str
):
    """WebSocket for real-time test call updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic updates
            if call_id in active_test_calls:
                test_call = active_test_calls[call_id]
                
                # Update duration
                if test_call["status"] == "active":
                    started = datetime.fromisoformat(test_call["started_at"])
                    test_call["duration"] = int((datetime.utcnow() - started).total_seconds())
                
                await websocket.send_json({
                    "type": "update",
                    "data": test_call
                })
            else:
                await websocket.send_json({
                    "type": "ended",
                    "data": {"message": "Call has ended"}
                })
                break
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

@router.post("/emergency-stop")
async def emergency_stop(
    current_user: dict = Depends(get_current_user)
):
    """Emergency stop all test calls"""
    stopped_calls = []
    
    for call_id in list(active_test_calls.keys()):
        try:
            test_call = await TestCallService.end_test_call(call_id)
            stopped_calls.append(call_id)
        except:
            pass
    
    return {
        "message": f"Emergency stop executed. {len(stopped_calls)} calls terminated.",
        "stopped_calls": stopped_calls,
        "timestamp": datetime.utcnow().isoformat()
    }