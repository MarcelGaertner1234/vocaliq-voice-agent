"""
Scheduled Tasks API Routes
Endpoints zur Verwaltung von automatisierten Aufgaben
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from api.services.scheduled_tasks import scheduled_tasks
from api.core.auth import require_admin

router = APIRouter(
    prefix="/api/admin/scheduled-tasks",
    tags=["scheduled-tasks"],
    dependencies=[Depends(require_admin)]
)


@router.get("/status")
async def get_scheduled_tasks_status():
    """
    Gibt den Status aller geplanten Aufgaben zurück
    
    Returns:
        Liste aller Jobs mit Status und nächster Ausführungszeit
    """
    return scheduled_tasks.get_job_status()


@router.post("/trigger/{job_id}")
async def trigger_scheduled_task(job_id: str):
    """
    Triggert eine geplante Aufgabe manuell
    
    Args:
        job_id: ID der Aufgabe (z.B. 'daily_follow_ups')
        
    Returns:
        Success status
    """
    success = await scheduled_tasks.trigger_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} nicht gefunden"
        )
    
    return {
        "success": True,
        "message": f"Job {job_id} wurde manuell getriggert"
    }


@router.post("/follow-ups/execute-now")
async def execute_follow_ups_now():
    """
    Führt alle fälligen Follow-Ups sofort aus
    Admin-only Endpoint für manuelle Ausführung
    """
    await scheduled_tasks._execute_daily_follow_ups()
    
    return {
        "success": True,
        "message": "Follow-Ups werden ausgeführt"
    }


@router.post("/reactivations/execute-now")
async def execute_reactivations_now():
    """
    Führt Lead Reaktivierungen sofort aus
    Admin-only Endpoint für manuelle Ausführung
    """
    await scheduled_tasks._execute_weekly_reactivations()
    
    return {
        "success": True,
        "message": "Reaktivierungen werden geplant"
    }


@router.post("/scores/update-now")
async def update_lead_scores_now():
    """
    Aktualisiert alle Lead Scores sofort
    Admin-only Endpoint für manuelle Ausführung
    """
    await scheduled_tasks._update_lead_scores()
    
    return {
        "success": True,
        "message": "Lead Scores werden aktualisiert"
    }


@router.post("/report/generate-now")
async def generate_report_now():
    """
    Generiert Performance Report sofort
    Admin-only Endpoint für manuelle Ausführung
    """
    await scheduled_tasks._generate_weekly_report()
    
    return {
        "success": True,
        "message": "Report wird generiert"
    }