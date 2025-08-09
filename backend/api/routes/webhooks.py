"""
Webhooks API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Dict, Any
from datetime import datetime
import httpx
import asyncio
import json

from ..database import get_session
from ..models.webhook import (
    Webhook, 
    WebhookCreate, 
    WebhookUpdate, 
    WebhookResponse,
    WebhookTestRequest,
    WebhookLog
)
from ..auth import get_current_user

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

async def trigger_webhook(
    webhook: Webhook, 
    event: str, 
    payload: Dict[str, Any],
    session: Session
):
    """Trigger a webhook with retry logic"""
    log = WebhookLog(
        webhook_id=webhook.id,
        event=event,
        payload=payload
    )
    
    start_time = datetime.utcnow()
    
    async with httpx.AsyncClient() as client:
        for attempt in range(webhook.retry_count):
            try:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=webhook.headers,
                    timeout=webhook.timeout_seconds
                )
                
                log.response_status = response.status_code
                log.response_body = response.text[:1000]  # Limit response size
                log.success = response.status_code < 400
                
                if log.success:
                    webhook.success_count += 1
                    break
                    
            except Exception as e:
                log.error_message = str(e)
                if attempt == webhook.retry_count - 1:
                    webhook.failure_count += 1
                    log.success = False
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    end_time = datetime.utcnow()
    log.duration_ms = int((end_time - start_time).total_seconds() * 1000)
    
    webhook.last_triggered = datetime.utcnow()
    
    session.add(log)
    session.add(webhook)
    session.commit()

@router.get("/", response_model=List[WebhookResponse])
async def get_webhooks(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all webhooks"""
    if current_user.get("role") != "admin":
        # Filter by company for non-admin users
        statement = select(Webhook).where(
            Webhook.company_id == current_user.get("company_id")
        )
    else:
        statement = select(Webhook)
    
    webhooks = session.exec(statement).all()
    
    return [
        WebhookResponse(
            **webhook.dict(),
            success_rate=webhook.success_rate
        ) 
        for webhook in webhooks
    ]

@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific webhook"""
    webhook = session.get(Webhook, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Check access rights
    if current_user.get("role") != "admin" and webhook.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return WebhookResponse(
        **webhook.dict(),
        success_rate=webhook.success_rate
    )

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new webhook (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    webhook = Webhook(**webhook_data.dict())
    session.add(webhook)
    session.commit()
    session.refresh(webhook)
    
    return WebhookResponse(
        **webhook.dict(),
        success_rate=webhook.success_rate
    )

@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_update: WebhookUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a webhook (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    webhook = session.get(Webhook, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Update fields
    update_data = webhook_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    webhook.updated_at = datetime.utcnow()
    
    session.add(webhook)
    session.commit()
    session.refresh(webhook)
    
    return WebhookResponse(
        **webhook.dict(),
        success_rate=webhook.success_rate
    )

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a webhook (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    webhook = session.get(Webhook, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Delete associated logs
    logs = session.exec(
        select(WebhookLog).where(WebhookLog.webhook_id == webhook_id)
    ).all()
    
    for log in logs:
        session.delete(log)
    
    session.delete(webhook)
    session.commit()
    
    return {"message": "Webhook deleted successfully"}

@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    test_request: WebhookTestRequest = WebhookTestRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Test a webhook (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    webhook = session.get(Webhook, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Default test payload
    test_payload = test_request.payload or {
        "event": "test",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "message": "This is a test webhook",
            "webhook_id": webhook_id,
            "webhook_name": webhook.name
        }
    }
    
    # Trigger webhook in background
    background_tasks.add_task(
        trigger_webhook,
        webhook,
        "test",
        test_payload,
        session
    )
    
    return {
        "message": f"Test webhook sent to {webhook.url}",
        "payload": test_payload
    }

@router.get("/{webhook_id}/logs")
async def get_webhook_logs(
    webhook_id: str,
    limit: int = 50,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook execution logs (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    webhook = session.get(Webhook, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    statement = (
        select(WebhookLog)
        .where(WebhookLog.webhook_id == webhook_id)
        .order_by(WebhookLog.executed_at.desc())
        .limit(limit)
    )
    
    logs = session.exec(statement).all()
    
    return logs