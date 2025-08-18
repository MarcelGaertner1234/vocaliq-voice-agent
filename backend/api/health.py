"""
Health Check Endpoint für Render.com
Minimal memory footprint für Free Tier
"""
from fastapi import APIRouter, status
from typing import Dict
import psutil
import os

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict:
    """Simple health check for Render monitoring"""
    try:
        # Memory usage (wichtig für Free Tier Monitoring)
        memory = psutil.virtual_memory()
        memory_usage_mb = (memory.total - memory.available) / 1024 / 1024
        
        return {
            "status": "healthy",
            "service": "vocaliq-api",
            "memory_usage_mb": round(memory_usage_mb, 2),
            "memory_limit_mb": 512,  # Render Free Tier
            "memory_percent": round(memory.percent, 2),
            "environment": os.getenv("ENV", "development")
        }
    except:
        # Fallback wenn psutil nicht verfügbar
        return {
            "status": "healthy",
            "service": "vocaliq-api"
        }