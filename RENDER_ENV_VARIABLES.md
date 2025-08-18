# Render.com Environment Variables

## WICHTIG: Diese Variablen müssen in Render gesetzt werden!

Gehe zu deinem Backend Service in Render → "Environment" Tab und füge diese Variablen hinzu:

### 1. Database (PFLICHT)
```
DATABASE_URL = postgresql://vocaliq:nrK6l37eQbSThq1Tg9bHS9rz8gksRQDQ@dpg-d2hk4rm3jp1c738gpvu0-a.oregon-postgres.render.com/vocaliq
```
**WICHTIG**: Stelle sicher, dass die URL mit `.oregon-postgres.render.com` endet (externe URL)!

### 2. Redis (PFLICHT)
```
REDIS_URL = redis://default:AWpXAAIncDE0NDVjZDc5OGJiZjY0ZTM5YjI4MzMzYTk5MTIxNmJkY3AxMjcyMjM@square-parrot-27223.upstash.io:6379
```

### 3. Security (OPTIONAL - haben jetzt Defaults)
```
SECRET_KEY = your-secret-key-here-min-32-chars
JWT_SECRET_KEY = your-secret-key-here-min-32-chars  
ADMIN_PASSWORD = ein-sicheres-admin-passwort
ENCRYPTION_KEY = ToDHON5kuY7-roFy6KRzNxN0HMlnoEKZRs-PkK_oB30=
```
**Hinweis:** Diese haben jetzt Default-Werte, sollten aber in Production überschrieben werden!

### 4. API Keys (PFLICHT für Funktionalität)
```
OPENAI_API_KEY = sk-proj-...
ELEVENLABS_API_KEY = ...
```

### 5. Twilio (Optional, für Telefonie)
```
TWILIO_ACCOUNT_SID = ...
TWILIO_AUTH_TOKEN = ...
```

### 6. System Settings (Optional)
```
ENVIRONMENT = production
LOG_LEVEL = info
CORS_ORIGINS = https://your-frontend-domain.onrender.com
```

## Überprüfung in Render:

1. Gehe zu deinem Backend Service
2. Klicke auf "Environment" Tab
3. Stelle sicher, dass ALLE Pflicht-Variablen gesetzt sind
4. **PORT** wird automatisch von Render gesetzt - NICHT manuell setzen!

## Häufige Fehler:

❌ **FALSCH**: `DATABASE_URL` mit internem Host (dpg-xxx-a/vocaliq)
✅ **RICHTIG**: `DATABASE_URL` mit externem Host (dpg-xxx-a.oregon-postgres.render.com/vocaliq)

❌ **FALSCH**: PORT manuell setzen
✅ **RICHTIG**: PORT wird von Render automatisch gesetzt

❌ **FALSCH**: ENCRYPTION_KEY als PORT verwenden
✅ **RICHTIG**: ENCRYPTION_KEY ist eine separate Variable