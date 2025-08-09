from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
async def get_system_status() -> List[dict]:
    now = datetime.now(timezone.utc).isoformat()
    status = []

    # API is running if this handler is hit
    status.append({"service": "API", "status": "connected", "lastCheck": now})

    # Database health
    try:
        from api.core.database import health_check as db_health_check
        db = await db_health_check()
        status.append({
            "service": "Database",
            "status": "connected" if db.get("status") == "healthy" else "disconnected",
            "lastCheck": now
        })
    except Exception:
        status.append({"service": "Database", "status": "disconnected", "lastCheck": now})

    # OpenAI health
    try:
        from api.services.openai_service import openai_service
        openai = await openai_service.health_check()
        status.append({
            "service": "OpenAI",
            "status": "connected" if openai.get("status") == "healthy" else "disconnected",
            "lastCheck": now
        })
    except Exception:
        status.append({"service": "OpenAI", "status": "disconnected", "lastCheck": now})

    # ElevenLabs health
    try:
        from api.services.elevenlabs_service import elevenlabs_service
        el = await elevenlabs_service.health_check()
        status.append({
            "service": "ElevenLabs",
            "status": "connected" if el.get("status") == "healthy" else "disconnected",
            "lastCheck": now
        })
    except Exception:
        status.append({"service": "ElevenLabs", "status": "disconnected", "lastCheck": now})

    return status


@router.get("/stats")
async def get_system_stats(session: AsyncSession = Depends(get_session)) -> dict:
    """Return simple KPI stats for dashboard."""
    from sqlalchemy import text
    try:
        # Total calls today
        result = await session.execute(text(
            """
            SELECT COUNT(*) AS total_calls,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_calls,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_calls,
                   AVG(duration_seconds) AS avg_duration
            FROM call_logs
            WHERE created_at::date = CURRENT_DATE
            """
        ))
        row = result.first()
        total_calls = int(row.total_calls or 0)
        completed = int(row.completed_calls or 0)
        failed = int(row.failed_calls or 0)
        avg_duration_seconds = int(row.avg_duration or 0)
        # Format mm:ss
        minutes = avg_duration_seconds // 60
        seconds = avg_duration_seconds % 60
        avg_duration = f"{minutes}:{seconds:02d}"
        successful_rate = round((completed / total_calls) * 100, 0) if total_calls > 0 else 0
        return {
            "totalCallsToday": total_calls,
            "avgCallDuration": avg_duration,
            "successfulCalls": successful_rate,
            "failedCalls": failed,
        }
    except Exception:
        # Fallback defaults
        return {
            "totalCallsToday": 0,
            "avgCallDuration": "0:00",
            "successfulCalls": 0,
            "failedCalls": 0,
        } 