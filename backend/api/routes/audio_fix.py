"""
Audio File Serving Fix
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging

router = APIRouter(prefix="/audio", tags=["Audio"])
logger = logging.getLogger(__name__)

# Path to TTS cache
TTS_CACHE_DIR = "/app/storage/tts_cache"

@router.get("/tts/{file_name}")
async def serve_audio_file(file_name: str):
    """Serve cached TTS audio files"""
    
    # Security: Ensure no path traversal
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    file_path = os.path.join(TTS_CACHE_DIR, file_name)
    
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    logger.info(f"Serving audio file: {file_name}")
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Accept-Ranges": "bytes"
        }
    )