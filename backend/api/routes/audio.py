"""
Audio File Serving Routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
import os
import logging
from pathlib import Path
import base64

router = APIRouter(prefix="/audio", tags=["Audio"])
logger = logging.getLogger(__name__)

# Path to TTS cache directory
TTS_CACHE_DIR = Path("/app/storage/tts_cache")

# Create a simple audio waveform as placeholder
def generate_placeholder_audio():
    """Generate a simple sine wave audio file as placeholder"""
    import struct
    import math
    
    # Audio parameters
    sample_rate = 44100
    duration = 2.0  # seconds
    frequency = 440  # A4 note
    
    # Generate samples
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Generate a sine wave with envelope
        envelope = min(1.0, min(t * 4, (duration - t) * 4))  # Fade in/out
        sample = envelope * 0.3 * math.sin(2 * math.pi * frequency * t)
        # Convert to 16-bit integer
        samples.append(int(sample * 32767))
    
    # Create WAV file header
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + num_samples * 2,
        b'WAVE',
        b'fmt ',
        16,  # Subchunk size
        1,   # Audio format (PCM)
        1,   # Number of channels
        sample_rate,
        sample_rate * 2,  # Byte rate
        2,   # Block align
        16,  # Bits per sample
        b'data',
        num_samples * 2
    )
    
    # Pack samples
    wav_data = b''.join(struct.pack('<h', s) for s in samples)
    
    return wav_header + wav_data

@router.get("/tts/{file_name}")
async def serve_audio_file(file_name: str):
    """Serve cached TTS audio files or generate placeholder"""
    
    # Security: Ensure no path traversal
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    # Ensure cache directory exists
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    file_path = TTS_CACHE_DIR / file_name
    
    # Check if actual file exists
    if file_path.exists() and file_path.is_file():
        logger.info(f"✅ Serving real TTS audio: {file_name}")
        return FileResponse(
            str(file_path),  # Convert Path to string
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Accept-Ranges": "bytes",
                "Content-Type": "audio/mpeg",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cross-Origin-Resource-Policy": "cross-origin",
                "Timing-Allow-Origin": "*",
            }
        )
    
    # Check if it's a sample file request (for backwards compatibility)
    if file_name.startswith("sample_"):
        logger.info(f"⚠️ Generating placeholder audio for sample: {file_name}")
        audio_data = generate_placeholder_audio()
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Cache-Control": "no-cache",
                "Content-Disposition": f'inline; filename="{file_name}"',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Cross-Origin-Resource-Policy": "cross-origin",
                "Timing-Allow-Origin": "*",
            }
        )
    
    logger.warning(f"❌ Audio file not found: {file_name}")
    raise HTTPException(status_code=404, detail=f"Audio file not found: {file_name}")

@router.get("/sample/{voice_id}")
async def get_voice_sample(voice_id: str):
    """Get a sample audio for a specific voice"""
    
    # Map voice IDs to sample text
    voice_samples = {
        "21m00Tcm4TlvDq8ikWAM": "Hallo, ich bin Rachel von VocalIQ.",
        "ErXwobaYiN019PkySvjV": "Hallo, ich bin Antoni von VocalIQ.",
        "EXAVITQu4vr4xnSDxMaL": "Hallo, ich bin Bella von VocalIQ.",
        "MF3mGyEYCl7XYWbV9V6O": "Hallo, ich bin Elli von VocalIQ.",
        "N2lVS1w4EtoT3dr4eOWO": "Hallo, ich bin Callum von VocalIQ.",
        "XB0fDUnXU5powFXDhCwa": "Hallo, ich bin Charlotte von VocalIQ.",
        "TX3LPaxmHKxFdv7VOQHJ": "Hallo, ich bin Liam von VocalIQ."
    }
    
    # For now, return placeholder audio
    audio_data = generate_placeholder_audio()
    
    return Response(
        content=audio_data,
        media_type="audio/wav",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="sample_{voice_id}.wav"',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cross-Origin-Resource-Policy": "cross-origin",
            "Timing-Allow-Origin": "*",
        }
    )