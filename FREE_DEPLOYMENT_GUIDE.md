# 🚀 VocalIQ Kostenlose Deployment Anleitung

## Komplette Schritt-für-Schritt Anleitung für Render.com (FREE)

### ✅ Was du bekommst (KOSTENLOS):
- Live Website mit HTTPS
- Automatische Deploys von GitHub
- PostgreSQL Datenbank (90 Tage)
- Redis Cache (Upstash)
- Keine Kreditkarte nötig!

---

## 📝 Vorbereitung

### 1. Checklist - Was du brauchst:
- [ ] GitHub Account
- [ ] Render.com Account (hast du schon ✅)
- [ ] OpenAI API Key
- [ ] ElevenLabs API Key
- [ ] Twilio Credentials (optional)

### 2. GitHub Repository erstellen

#### Option A: Neues Repository
```bash
# In deinem Terminal
cd "/Users/marcelgaertner/Desktop/Ki voice Agenten ! /vocaliq-setup-docs"

# Git initialisieren
git init

# GitHub Repository erstellen (mit GitHub CLI)
gh repo create vocaliq-app --public --source=. --remote=origin --push
```

#### Option B: Manuell auf GitHub.com
1. Gehe zu github.com
2. Click **"New Repository"**
3. Name: `vocaliq-app`
4. Public (für Free Deployment)
5. **Create Repository**

6. Dann im Terminal:
```bash
cd "/Users/marcelgaertner/Desktop/Ki voice Agenten ! /vocaliq-setup-docs"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/DEIN_USERNAME/vocaliq-app.git
git push -u origin main
```

---

## 🔧 Schritt 1: Upstash Redis einrichten (5 Min)

1. **Gehe zu [upstash.com](https://upstash.com)**
2. **Sign Up** (mit GitHub)
3. **Create Database**:
   - Name: `vocaliq-redis`
   - Type: Regional
   - Region: EU-West-1 (Frankfurt)
4. **Kopiere die Redis URL** (sieht so aus):
   ```
   redis://default:xxxxx@xxxxx.upstash.io:6379
   ```

---

## 🎯 Schritt 2: Render Services erstellen

### A. PostgreSQL Database (zuerst!)

1. In Render Dashboard: **"New +"** → **"PostgreSQL"**
2. Settings:
   ```
   Name: vocaliq-db
   Database: vocaliq
   User: vocaliq
   Region: Frankfurt (eu-central)
   Plan: FREE
   ```
3. Click **"Create Database"**
4. **WICHTIG:** Kopiere die `Internal Database URL` für später

### B. Web Service (Backend + Frontend)

1. **"New +"** → **"Web Service"**
2. **"Connect GitHub"** → Autorisieren
3. **Select Repository:** `vocaliq-app`
4. Settings eingeben:
   ```
   Name: vocaliq-app
   Region: Frankfurt (eu-central)
   Branch: main
   Root Directory: (leer lassen)
   Runtime: Docker
   Plan: FREE ($0/month) ← WICHTIG!
   ```

5. **Environment Variables** (Click "Advanced" → "Add Environment Variable"):
   
   ```env
   # Database (aus Schritt A)
   DATABASE_URL = [Internal Database URL von oben]
   
   # Redis (aus Upstash)
   REDIS_URL = redis://default:xxxxx@xxxxx.upstash.io:6379
   
   # API Keys
   OPENAI_API_KEY = sk-...
   ELEVENLABS_API_KEY = ...
   
   # Security
   JWT_SECRET_KEY = [Generate Secret klicken]
   ENCRYPTION_KEY = ToDHON5kuY7-roFy6KRzNxN0HMlnoEKZRs-PkK_oB30=
   
   # App Settings
   PORT = 8000
   ENV = production
   
   # Twilio (optional)
   TWILIO_ACCOUNT_SID = (später)
   TWILIO_AUTH_TOKEN = (später)
   ```

6. Click **"Create Web Service"**

---

## 📦 Schritt 3: Deployment Files anpassen

### 1. render.yaml updaten
Öffne `render.yaml` und ändere:
```yaml
repo: https://github.com/DEIN_USERNAME/vocaliq-app
```

### 2. Git Push
```bash
git add .
git commit -m "Add Render deployment config"
git push origin main
```

---

## ⏳ Schritt 4: Warten und Beobachten

1. **Render Dashboard** → Dein Service
2. **"Logs"** Tab öffnen
3. Warte ~5-10 Minuten für ersten Build
4. Status wird grün: **"Live"** ✅

---

## 🌐 Schritt 5: Testen

1. Deine App URL: `https://vocaliq-app.onrender.com`
2. API Health Check: `https://vocaliq-app.onrender.com/api/health`
3. Frontend sollte laden!

---

## 🚨 Troubleshooting

### "Build failed"
- Check Logs Tab
- Meistens: Fehlende Environment Variable

### "502 Bad Gateway"
- Service startet noch (dauert 1-2 Min)
- Free Tier: Erster Start nach Sleep dauert 30 Sek

### "Database Connection Error"
- DATABASE_URL richtig kopiert?
- Internal URL verwenden, nicht External

### Frontend lädt nicht
- CORS_ORIGINS in Environment Variables checken
- Frontend Build Logs prüfen

---

## 📱 Schritt 6: Twilio Setup (Optional)

1. In Twilio Console:
   - Voice URL: `https://vocaliq-app.onrender.com/api/twilio/voice`
   - Status Callback: `https://vocaliq-app.onrender.com/api/twilio/status`

2. In Render Environment Variables:
   - TWILIO_ACCOUNT_SID hinzufügen
   - TWILIO_AUTH_TOKEN hinzufügen

---

## 🎉 FERTIG!

### Was funktioniert jetzt:
- ✅ Live Website mit HTTPS
- ✅ API läuft
- ✅ Database verbunden
- ✅ Redis Cache aktiv
- ✅ Auto-Deploy bei Git Push

### Free Tier Limits:
- Service schläft nach 15 Min Inaktivität
- Erster Request danach: ~30 Sek
- PostgreSQL: 90 Tage (dann neu erstellen)
- 512MB RAM (reicht für VocalIQ)

### Nächste Schritte:
1. Custom Domain hinzufügen (optional)
2. Monitoring einrichten
3. Backup Strategie planen

---

## 🆘 Hilfe

### Render Status
- Check: [status.render.com](https://status.render.com)

### Logs anschauen
```bash
# In Render Dashboard
Services → vocaliq-app → Logs
```

### Environment Variables ändern
```bash
Services → vocaliq-app → Environment → Edit
# Service startet automatisch neu
```

---

**Glückwunsch! VocalIQ läuft jetzt KOSTENLOS in der Cloud! 🚀**