"""
VocalIQ API - Hauptanwendung
Intelligente Voice-Agent-Plattform für Business-Telefonie
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter

from api.core.config import get_settings
from api.routes.auth import router as auth_router
from api.routes.calls import router as calls_router
from api.middleware.rate_limiting import rate_limit_middleware

# Settings laden
settings = get_settings()

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Anwendungsstart und -stopp Handler"""
    # Startup
    logger.info(f"🚀 Starting VocalIQ API v{settings.API_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize services
    try:
        # Database
        from api.core.database import create_database_engine, create_tables
        create_database_engine()
        await create_tables()
        logger.info("✅ Database initialized")
        
        # Health checks for external services
        from api.services.openai_service import openai_service
        from api.services.elevenlabs_service import elevenlabs_service
        
        # Initialize service health checks in background
        # (Don't block startup if services are temporarily unavailable)
        
    except Exception as e:
        logger.error(f"❌ Service initialization error: {str(e)}")
        # Continue startup even if some services fail
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down VocalIQ API")
    
    # Close database connections
    try:
        from api.core.database import close_database
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Database shutdown error: {str(e)}")


# FastAPI App erstellen
app = FastAPI(
    title="VocalIQ API",
    description="Intelligente Voice-Agent-Plattform für Business-Telefonie",
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware (Security)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_origins_list + ["localhost", "127.0.0.1"]
    )


# Rate Limiting Middleware (vor anderen Middlewares)
app.middleware("http")(rate_limit_middleware)

# Request/Response Middleware für Logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Request-Zeit messen und loggen"""
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"📨 {request.method} {request.url.path} - {request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ {request.method} {request.url.path} - Error: {str(e)} ({process_time:.3f}s)")
        raise


# Routes einbinden
# app.include_router(auth_router)
# app.include_router(calls_router)

# Twilio/Demo werden weiter unten unter dem gebündelten /api Router registriert

# Einheitlicher API-Router mit Prefix /api
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(calls_router)

# Twilio Voice Router unter /api registrieren
try:
    from api.routers.twilio import router as twilio_router
    api_router.include_router(twilio_router)
    logger.info("✅ Twilio router registered")
except ImportError as e:
    logger.warning(f"⚠️ Twilio router not available: {e}")

# Demo-Router unter /api registrieren
from api.routes.demo import router as demo_router
api_router.include_router(demo_router)

# System-Router unter /api registrieren
try:
    from api.routes.system import router as system_router
    api_router.include_router(system_router)
    logger.info("✅ System router registered")
except ImportError as e:
    logger.warning(f"⚠️ System router not available: {e}")

# Settings-Router unter /api registrieren
try:
    from api.routes.settings import router as settings_router
    api_router.include_router(settings_router)
    logger.info("✅ Settings router registered")
except ImportError as e:
    logger.warning(f"⚠️ Settings router not available: {e}")

# Knowledge-Router unter /api registrieren
try:
    from api.routes.knowledge import router as knowledge_router
    api_router.include_router(knowledge_router)
    logger.info("✅ Knowledge router registered")
except ImportError as e:
    logger.warning(f"⚠️ Knowledge router not available: {e}")

# Phone Numbers Router unter /api registrieren
try:
    from api.routes.phone_numbers import router as phone_numbers_router
    api_router.include_router(phone_numbers_router)
    logger.info("✅ Phone Numbers router registered")
except ImportError as e:
    logger.warning(f"⚠️ Phone Numbers router not available: {e}")

# Webhooks Router unter /api registrieren
try:
    from api.routes.webhooks import router as webhooks_router
    api_router.include_router(webhooks_router)
    logger.info("✅ Webhooks router registered")
except ImportError as e:
    logger.warning(f"⚠️ Webhooks router not available: {e}")

# Test Call Router unter /api registrieren
try:
    from api.routes.test_call import router as test_call_router
    api_router.include_router(test_call_router)
    logger.info("✅ Test Call router registered")
except ImportError as e:
    logger.warning(f"⚠️ Test Call router not available: {e}")

# Companies Router unter /api registrieren
try:
    from api.routes.companies import router as companies_router
    api_router.include_router(companies_router)
    logger.info("✅ Companies router registered")
except ImportError as e:
    logger.warning(f"⚠️ Companies router not available: {e}")

# Users Router unter /api registrieren
try:
    from api.routes.users import router as users_router
    api_router.include_router(users_router)
    logger.info("✅ Users router registered")
except ImportError as e:
    logger.warning(f"⚠️ Users router not available: {e}")

# Root-API-Router an App hängen
app.include_router(api_router)


# Root Endpoints
@app.get("/", tags=["Root"])
async def root():
    """API Root - Basis-Informationen"""
    return {
        "service": "VocalIQ API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "features": {
            "authentication": True,
            "voice_calls": True,
            "text_to_speech": True,
            "speech_to_text": True,
            "ai_conversation": True,
            "calendar_integration": settings.FEATURE_CALENDAR_INTEGRATION,
            "analytics": settings.FEATURE_ANALYTICS,
            "webhooks": settings.FEATURE_WEBHOOKS
        },
        "docs": f"{settings.API_BASE_URL}/docs",
        "redoc": f"{settings.API_BASE_URL}/redoc"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Comprehensive Health Check"""
    services_status = {"api": "healthy"}
    
    # Database health check
    try:
        from api.core.database import health_check as db_health_check
        db_status = await db_health_check()
        services_status["database"] = db_status["status"]
    except Exception as e:
        services_status["database"] = f"error: {str(e)}"
    
    # External services health checks (non-blocking)
    try:
        from api.services.openai_service import openai_service
        openai_status = await openai_service.health_check()
        services_status["openai"] = openai_status["status"]
    except Exception:
        services_status["openai"] = "not_configured"
    
    try:
        from api.services.elevenlabs_service import elevenlabs_service
        elevenlabs_status = await elevenlabs_service.health_check()
        services_status["elevenlabs"] = elevenlabs_status["status"]
    except Exception:
        services_status["elevenlabs"] = "not_configured"
    
    # Overall status
    overall_status = "healthy"
    if "error" in str(services_status.values()):
        overall_status = "degraded"
    if services_status.get("database") == "error":
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.API_VERSION,
        "services": services_status
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Basic Metrics für Monitoring"""
    return {
        "uptime": "unknown",  # TODO: Implementieren
        "requests_total": "unknown",  # TODO: Implementieren
        "active_calls": 0,    # TODO: Implementieren
        "error_rate": 0.0,    # TODO: Implementieren
        "response_time_avg": 0.0  # TODO: Implementieren
    }


# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 Not Found Handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource {request.url.path} was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """500 Internal Server Error Handler"""
    logger.error(f"Internal error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred" if settings.is_production else str(exc),
            "status_code": 500
        }
    ) from api.routes.voices import router as voices_router
app.include_router(voices_router, prefix="/api")
