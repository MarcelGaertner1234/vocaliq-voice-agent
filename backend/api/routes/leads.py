from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
from api.services.notification_service import NotificationService
from api.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leads", tags=["Leads"])

notification_service = NotificationService()
settings = get_settings()

class LeadPayload(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=120)
    message: str = Field(..., min_length=10, max_length=2000)
    source: Optional[str] = Field("landing", max_length=50)

class LeadResponse(BaseModel):
    success: bool
    message: str
    delivery: str

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_lead(payload: LeadPayload, request: Request):
    """
    Nimmt Leads von der Landing-Page entgegen.
    - Validiert Basisdaten
    - Versendet optional eine E-Mail an ADMIN_EMAIL (falls SMTP konfiguriert)
    - Loggt den Lead immer serverseitig
    """
    try:
        # Simple anti-spam heuristics
        if payload.message.count("http") > 3 or len(payload.message.split()) < 3:
            raise HTTPException(status_code=400, detail="Ungültige Anfrage")

        admin_email = getattr(settings, "ADMIN_EMAIL", None)
        delivered = False

        # Optional: E-Mail senden, falls SMTP und Admin-Mail vorhanden
        if admin_email and notification_service.smtp_host:
            try:
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                import aiosmtplib

                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"Neuer Lead: {payload.name} ({payload.company or '—'})"
                msg["From"] = getattr(settings, "SMTP_FROM_EMAIL", "noreply@vocaliq.de")
                msg["To"] = admin_email

                body = (
                    f"Quelle: {payload.source}\n"
                    f"Name: {payload.name}\n"
                    f"E-Mail: {payload.email}\n"
                    f"Unternehmen: {payload.company or '—'}\n\n"
                    f"Nachricht:\n{payload.message}\n"
                )
                msg.attach(MIMEText(body, "plain"))

                async with aiosmtplib.SMTP(
                    hostname=notification_service.smtp_host,
                    port=notification_service.smtp_port,
                    use_tls=True,
                ) as smtp:
                    if notification_service.smtp_user and notification_service.smtp_password:
                        await smtp.login(notification_service.smtp_user, notification_service.smtp_password)
                    await smtp.send_message(msg)
                delivered = True
            except Exception as e:
                logger.warning(f"Lead email delivery failed: {e}")
                delivered = False

        # Immer loggen
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "Lead received | ip=%s | name=%s | email=%s | company=%s | source=%s | %d chars",
            client_ip,
            payload.name,
            payload.email,
            payload.company or "",
            payload.source,
            len(payload.message),
        )

        return LeadResponse(
            success=True,
            message="Danke! Wir melden uns zeitnah.",
            delivery="email" if delivered else "logged",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lead processing failed: {e}")
        raise HTTPException(status_code=500, detail="Interner Fehler") 