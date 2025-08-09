# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Overview

**VocalIQ** - Enterprise-grade AI telephone assistant platform for business communication automation.

## 📁 Project Structure

```
vocaliq-voice-agent/
├── backend/
│   ├── api/
│   │   ├── core/              # Config, Database, Security
│   │   ├── models/            # SQLModel entities
│   │   ├── routes/            # API endpoints
│   │   │   └── admin/         # Admin-specific routes
│   │   ├── services/          # Business logic
│   │   └── repositories/      # Data access layer
│   ├── alembic/               # Database migrations
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/
│   │   │   ├── auth/          # Login pages (Admin/Customer)
│   │   │   └── admin/         # Admin dashboard pages
│   │   ├── layouts/           # AdminLayout, DashboardLayout
│   │   ├── services/          # API client
│   │   └── stores/            # Zustand state management
│   │       └── authStore.ts   # Auth with role-based access
│   └── package.json
├── docker-compose.yml         # Container orchestration
└── Makefile                   # Development commands
```

## 🆕 Recent Updates (Admin Dashboard)

### Admin Portal Features:
1. **Separate Login System**
   - `/admin/login` - Admin portal access
   - `/login` - Customer portal access
   - Role-based authentication (admin/customer)

2. **Admin Dashboard** (`/admin/dashboard`)
   - Service Quick Links to all external platforms
   - System statistics overview
   - Quick action buttons

3. **API Configuration Center** (`/admin/api-config`)
   - Centralized API key management
   - Service status indicators
   - Direct links to service dashboards:
     - OpenAI Platform
     - ElevenLabs Console
     - Twilio Dashboard
     - Weaviate Cloud

4. **Customer Settings Cleaned**
   - API keys removed from customer settings
   - Only company-specific settings remain
   - Admin notification for API changes

## 🛠️ Development Commands

```bash
# Development
make up                # Start all services
make down              # Stop services
make logs              # View logs
make test              # Run tests

# Database
make db-init           # Initialize database
make db-migrate        # Create migration
make db-upgrade        # Apply migrations

# Frontend Development
cd frontend
npm run dev            # Start dev server (port 5173)
npm run build          # Production build
npm run lint           # Run linter
```

## 🔑 Important Files

### Backend
- `api/core/config.py` - 150+ configuration parameters
- `api/core/database.py` - Async SQLAlchemy setup
- `api/services/voice_pipeline.py` - Audio processing pipeline
- `api/services/openai_service.py` - GPT-4 integration
- `api/routes/admin/company_management.py` - Multi-tenant management

### Frontend
- `src/stores/authStore.ts` - Authentication with roles
- `src/pages/admin/AdminDashboard.tsx` - Admin overview with quick links
- `src/pages/admin/ApiConfiguration.tsx` - API key management
- `src/layouts/AdminLayout.tsx` - Admin navigation
- `src/pages/auth/AdminLogin.tsx` - Admin login page
- `src/pages/auth/CustomerLogin.tsx` - Customer login page

## 🏗️ Architecture

### Voice Processing Pipeline
```
Call → Twilio → WebSocket → Audio Buffer
        ↓
   μ-law Decode → Whisper STT → GPT-4 → ElevenLabs TTS
        ↓
   μ-law Encode → Twilio → Caller
```

### Authentication Flow
- JWT with access/refresh tokens
- Role-based access (admin/customer)
- Session management per role
- Protected routes

### Tech Stack
- **Backend**: FastAPI, Python 3.11+, SQLModel, Alembic
- **Frontend**: React 19, TypeScript, Vite, Zustand, Tailwind CSS
- **Databases**: PostgreSQL, Redis, Weaviate
- **Services**: OpenAI GPT-4, Twilio, ElevenLabs
- **Infrastructure**: Docker, Docker Compose

## 🚀 Getting Started

1. **Clone and setup**
   ```bash
   git clone https://github.com/MarcelGaertner1234/vocaliq-voice-agent
   cd vocaliq-voice-agent
   cp env.example .env
   ```

2. **Configure environment**
   - Add API keys to `.env`
   - Or use Admin Portal to configure after login

3. **Start services**
   ```bash
   make setup
   make up
   make db-init
   ```

4. **Access portals**
   - Customer: http://localhost:5173/login
   - Admin: http://localhost:5173/admin/login
   - API Docs: http://localhost:8001/docs

## 🔐 Default Admin Credentials

```
Username: admin
Password: Check ADMIN_PASSWORD in .env
```

## 📝 Notes for Development

- API keys are now managed ONLY in Admin Portal
- Customer settings only contain company-specific configs
- Use `make` commands for common tasks
- Frontend uses Vite for fast HMR
- Backend supports hot-reload in development

## 🐛 Common Issues

1. **Auth issues**: Clear localStorage and re-login
2. **API connection**: Check services are running with `docker ps`
3. **Database**: Run `make db-upgrade` for migrations
4. **Frontend build**: Clear node_modules and reinstall

## 🔗 External Service Links

Quick access for admins:
- OpenAI: https://platform.openai.com
- ElevenLabs: https://elevenlabs.io
- Twilio: https://console.twilio.com
- Weaviate: https://console.weaviate.cloud