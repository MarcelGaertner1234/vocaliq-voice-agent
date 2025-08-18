# Upstash Redis Setup für VocalIQ (KOSTENLOS)

## 🔴 Upstash Redis - Kostenloser Plan

### Was ist Upstash?
- **Serverless Redis** - Keine Server-Verwaltung
- **Pay-per-request** - Kostenlos bis 10,000 Commands/Tag
- **Global** - Edge Locations weltweit
- **Kein Sleep** - Immer aktiv (nicht wie Render DB)

## 📋 Schritt-für-Schritt Setup

### 1. Account erstellen
1. Gehe zu **[upstash.com](https://upstash.com)**
2. Click **"Sign Up"**
3. Mit GitHub oder Email registrieren
4. Email bestätigen

### 2. Redis Database erstellen
1. Im Dashboard: **"Create Database"**
2. **Name:** `vocaliq-redis`
3. **Type:** Regional (nicht Global)
4. **Region:** `eu-west-1` (Frankfurt) oder `us-east-1`
5. **Eviction:** Enable (automatisches Löschen alter Daten)
6. Click **"Create"**

### 3. Connection Details kopieren

Nach Erstellung siehst du:
```
UPSTASH_REDIS_REST_URL=https://xxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxxxxxxxxxxxx
```

**ODER Classic Redis URL:**
```
redis://default:password@xxxxx.upstash.io:port
```

### 4. In Render.com einfügen

1. Gehe zu deinem Render Service
2. **Environment** → **Add Environment Variable**
3. Füge ein:
   ```
   Key: REDIS_URL
   Value: redis://default:xxxxx@xxxxx.upstash.io:6379
   ```

## 🔧 Python Code Anpassung

### Für Upstash REST API (empfohlen):
```python
# api/core/redis_client.py
import httpx
import os
from typing import Optional

class UpstashRedis:
    def __init__(self):
        self.url = os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }
    
    async def get(self, key: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/get/{key}",
                headers=self.headers
            )
            return response.json().get("result")
    
    async def set(self, key: str, value: str, ex: int = None):
        params = {"EX": ex} if ex else {}
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.url}/set/{key}",
                headers=self.headers,
                json={"value": value, **params}
            )
```

### Oder klassische Redis Connection:
```python
# Funktioniert mit bestehendem Code!
import redis
import os

# Upstash URL Format
REDIS_URL = os.getenv("REDIS_URL")
# redis://default:password@xxxxx.upstash.io:6379

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=None  # Wichtig für Upstash SSL
)
```

## 📊 Free Tier Limits

| Feature | Free Limit | Für VocalIQ |
|---------|------------|-------------|
| Commands/Tag | 10,000 | ✅ Ausreichend |
| Bandwidth | 256 MB/Tag | ✅ Genug |
| Max DB Size | 256 MB | ✅ Reicht |
| Connections | 1000 | ✅ Mehr als genug |
| Persistence | ✅ Ja | Daten bleiben |

## 🚀 Vorteile gegenüber Render Redis

1. **Kein 90-Tage Limit** (Render DB wird gelöscht)
2. **Immer aktiv** (kein Cold Start)
3. **Global Edge Network**
4. **REST API** (funktioniert überall)
5. **Kostenlos für immer** (bei <10k requests)

## 🔐 Sicherheit

- ✅ SSL/TLS verschlüsselt
- ✅ Token-basierte Auth
- ✅ IP Whitelist möglich
- ✅ Read-only Tokens verfügbar

## 📝 Environment Variables für Render

Füge diese in Render ein:
```env
# Option 1: REST API (empfohlen)
UPSTASH_REDIS_REST_URL=https://xxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxxxxxxxxxxxx

# Option 2: Redis Protocol
REDIS_URL=redis://default:xxxxx@xxxxx.upstash.io:6379
```

## ✅ Testen

```python
# Test Script
import redis
import os

redis_url = "redis://default:xxxxx@xxxxx.upstash.io:6379"
r = redis.from_url(redis_url, ssl_cert_reqs=None)

# Test
r.set("test", "VocalIQ works!")
print(r.get("test"))  # Should print: VocalIQ works!
```

---

**Fertig!** Upstash Redis ist jetzt eingerichtet und kostenlos nutzbar! 🎉