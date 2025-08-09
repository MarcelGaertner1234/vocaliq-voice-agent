from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.database import get_session
from api.models.database import SystemConfig

router = APIRouter(prefix="/settings", tags=["Settings"])


class SettingsUpdate(BaseModel):
    data: Dict[str, Any]


@router.get("")
async def get_settings_api(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(
            select(SystemConfig).where(SystemConfig.key == "settings")
        )
        row = result.scalar_one_or_none()
        if not row:
            # Default minimal Settings, falls keine vorhanden
            default_settings = {
                "companyName": "VocalIQ Demo Company",
                "phoneNumber": "+49 30 12345678",
                "openaiApiKey": "",
                "elevenLabsApiKey": "",
                "twilioAccountSid": "",
                "twilioAuthToken": "",
                "voiceId": "Antoni",
                "language": "de-DE",
                "maxCallDuration": "300",
                "enableRecording": True,
                "enableNotifications": True,
                "agentEnabled": True,
                "schedule": {
                    "monday": [{"start": "09:00", "end": "17:00"}],
                    "tuesday": [{"start": "09:00", "end": "17:00"}],
                    "wednesday": [{"start": "09:00", "end": "17:00"}],
                    "thursday": [{"start": "09:00", "end": "17:00"}],
                    "friday": [{"start": "09:00", "end": "17:00"}],
                    "saturday": [],
                    "sunday": []
                },
                "timezone": "Europe/Berlin",
            }
            return default_settings
        import json
        return json.loads(row.value)
    except Exception as e:
        raise HTTPException(500, f"Failed to load settings: {e}")


@router.put("")
async def update_settings_api(payload: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    try:
        import json
        result = await session.execute(
            select(SystemConfig).where(SystemConfig.key == "settings")
        )
        row = result.scalar_one_or_none()
        if not row:
            row = SystemConfig(
                key="settings",
                value=json.dumps(payload),
                description="Frontend settings",
                is_system=False,
                value_type="json",
                category="frontend"
            )
            session.add(row)
        else:
            row.value = json.dumps(payload)
            session.add(row)
        await session.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, f"Failed to update settings: {e}")


class TestConnectionRequest(BaseModel):
    service: str
    credentials: Dict[str, Any]


@router.post("/test-connection")
async def test_connection(req: TestConnectionRequest):
    service = req.service.lower()
    try:
        if service == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=req.credentials.get("api_key") or req.credentials.get("openaiApiKey"))
            # Lightweight call
            await client.models.list()
            return {"success": True}
        if service == "elevenlabs":
            import httpx
            api_key = req.credentials.get("api_key") or req.credentials.get("elevenLabsApiKey")
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": api_key})
                r.raise_for_status()
            return {"success": True}
        if service == "twilio":
            from twilio.rest import Client
            client = Client(req.credentials.get("account_sid"), req.credentials.get("auth_token"))
            # Check account fetch
            _ = client.api.accounts(req.credentials.get("account_sid")).fetch()
            return {"success": True}
        return {"success": False}
    except Exception:
        return {"success": False} 