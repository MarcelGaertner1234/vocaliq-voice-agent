# VocalIQ Deployment Plan 🚀

## ✅ Backup Status
- **Backup erstellt:** `vocaliq-backup-20250818-160157.tar.gz` (48MB)
- **Speicherort:** `/Users/marcelgaertner/Desktop/`
- **Zeitstempel:** 2025-08-18 16:01:57

## 📋 Deployment Schritte

### Schritt 1: Environment Vorbereitung ⚙️

#### 1.1 Production .env Datei erstellen
```bash
cd /Users/marcelgaertner/Desktop/Ki\ voice\ Agenten\ \!\ /vocaliq-setup-docs
cp .env.example .env.production
```

**Wichtige Environment Variables:**
```env
# API Keys (REQUIRED)
OPENAI_API_KEY=your-production-key
ELEVENLABS_API_KEY=your-production-key
TWILIO_ACCOUNT_SID=your-production-sid
TWILIO_AUTH_TOKEN=your-production-token

# Security (REQUIRED - change these!)
JWT_SECRET_KEY=generate-strong-secret-key-here
ENCRYPTION_KEY=ToDHON5kuY7-roFy6KRzNxN0HMlnoEKZRs-PkK_oB30=

# Database
DATABASE_URL=postgresql://vocaliq:your-secure-password@db:5432/vocaliq
REDIS_URL=redis://redis:6379

# Weaviate
WEAVIATE_URL=http://weaviate:8080
WEAVIATE_API_KEY=your-weaviate-key

# Production Domain
DOMAIN=your-domain.com
SSL_EMAIL=admin@your-domain.com

# CORS (production URLs)
CORS_ORIGINS=["https://your-domain.com"]
```

### Schritt 2: Docker Production Setup 🐳

#### 2.1 Production Docker Compose
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - api
    restart: always

  api:
    build: 
      context: ./backend
      dockerfile: Dockerfile.production
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./backend:/app
      - uploads:/app/uploads
    depends_on:
      - db
      - redis
      - weaviate
    restart: always

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: vocaliq
      POSTGRES_USER: vocaliq
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: always

  weaviate:
    image: semitechnologies/weaviate:latest
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-openai'
      OPENAI_APIKEY: ${OPENAI_API_KEY}
    volumes:
      - weaviate_data:/var/lib/weaviate
    restart: always

volumes:
  postgres_data:
  redis_data:
  weaviate_data:
  uploads:
```

### Schritt 3: SSL/HTTPS Setup 🔒

#### 3.1 Certbot für Let's Encrypt
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### 3.2 Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

### Schritt 4: Build & Deploy 🚀

#### 4.1 Frontend Build
```bash
cd frontend
npm install
npm run build
```

#### 4.2 Backend Dockerfile
```dockerfile
# backend/Dockerfile.production
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations on startup
RUN alembic upgrade head

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.3 Deploy Commands
```bash
# Build and start services
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Database migrations
docker-compose -f docker-compose.production.yml exec api alembic upgrade head
```

### Schritt 5: Testing & Monitoring 🔍

#### 5.1 Health Checks
```bash
# API Health
curl https://your-domain.com/api/health

# WebSocket Test
wscat -c wss://your-domain.com/ws/voice-chat

# Database Connection
docker-compose -f docker-compose.production.yml exec api python -c "from api.database import engine; print('DB OK')"
```

#### 5.2 Monitoring Setup
- **Logs:** Docker logs aggregation
- **Metrics:** Prometheus + Grafana
- **Uptime:** UptimeRobot or similar
- **Error Tracking:** Sentry integration

### Schritt 6: Twilio Configuration 📞

#### 6.1 Update Twilio Webhook URLs
```bash
# In Twilio Console
Voice URL: https://your-domain.com/api/twilio/voice
Status Callback: https://your-domain.com/api/twilio/status
```

#### 6.2 Test Phone Integration
```bash
# Make test call to your Twilio number
# Check logs for connection
docker-compose -f docker-compose.production.yml logs -f api | grep "twilio"
```

## 🔧 Rollback Plan

Falls etwas schief geht:
```bash
# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Restore from backup
tar -xzf vocaliq-backup-20250818-160157.tar.gz

# Restart with old configuration
docker-compose up -d
```

## 📝 Post-Deployment Checklist

- [ ] SSL Certificate aktiv
- [ ] Frontend erreichbar
- [ ] API Endpoints funktionieren
- [ ] WebSocket Verbindung stabil
- [ ] Twilio Integration funktioniert
- [ ] Database Verbindung stabil
- [ ] Redis Cache aktiv
- [ ] Weaviate Vector DB läuft
- [ ] Logs werden gesammelt
- [ ] Monitoring aktiv
- [ ] Backup-Strategie implementiert

## 🚨 Wichtige Hinweise

1. **API Keys:** Stelle sicher, dass alle Production API Keys eingetragen sind
2. **Domain:** Ersetze `your-domain.com` mit deiner echten Domain
3. **SSL:** Let's Encrypt Zertifikate müssen alle 90 Tage erneuert werden
4. **Backups:** Tägliche automatische Backups einrichten
5. **Monitoring:** Alerts für kritische Fehler konfigurieren

## 📞 Support Kontakte

- **Twilio Support:** support@twilio.com
- **ElevenLabs:** support@elevenlabs.io
- **OpenAI:** support@openai.com

---

Ready to deploy! 🚀 Folge den Schritten der Reihe nach.