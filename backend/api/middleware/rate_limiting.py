"""
VocalIQ Rate-Limiting Middleware
Schutz vor API-Missbrauch mit Redis-basiertem Rate-Limiting
"""
import time
import hashlib
from typing import Dict, Optional, Tuple
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import logging
from contextlib import asynccontextmanager

from api.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Redis Client für Rate-Limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting will be disabled.")
    redis_client = None


class RateLimiter:
    """Advanced Rate Limiter mit verschiedenen Strategien"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.local_cache = {}  # Fallback bei Redis-Ausfall
        self.cache_cleanup_time = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Eindeutige Client-Identifikation"""
        # Priorität: API-Key > JWT-Token > IP-Adresse
        
        # 1. API-Key aus Header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
        
        # 2. JWT-Token aus Authorization Header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return f"jwt:{hashlib.sha256(token.encode()).hexdigest()[:16]}"
        
        # 3. IP-Adresse (mit X-Forwarded-For Support)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _get_rate_limit_key(self, client_id: str, endpoint: str, window: str) -> str:
        """Rate-Limit-Key generieren"""
        return f"rate_limit:{client_id}:{endpoint}:{window}"
    
    def _parse_rate_limit(self, rate_limit_str: str) -> Tuple[int, int]:
        """Parse Rate-Limit String (z.B. "100/minute")"""
        try:
            count, period = rate_limit_str.split("/")
            count = int(count)
            
            period_seconds = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400
            }
            
            return count, period_seconds.get(period, 60)
        except Exception:
            return 100, 60  # Default: 100 requests per minute
    
    def _sliding_window_counter(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> Tuple[bool, int, int]:
        """Sliding Window Counter Algorithm"""
        current_time = int(time.time())
        window_start = current_time - window
        
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                
                # Remove expired entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current requests
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                
                # Set expiration
                pipe.expire(key, window + 10)
                
                results = pipe.execute()
                current_count = results[1] + 1
                
                if current_count <= limit:
                    remaining = limit - current_count
                    return True, remaining, window
                else:
                    # Remove the request we just added since we're over limit
                    self.redis.zrem(key, str(current_time))
                    return False, 0, window
                    
            except Exception as e:
                logger.error(f"Redis error in rate limiting: {e}")
                # Fallback to local cache
                return self._local_fallback(key, limit, window, current_time)
        else:
            return self._local_fallback(key, limit, window, current_time)
    
    def _local_fallback(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        current_time: int
    ) -> Tuple[bool, int, int]:
        """Fallback auf lokalen Cache wenn Redis nicht verfügbar"""
        # Cleanup old entries periodically
        if current_time - self.cache_cleanup_time > 300:  # Every 5 minutes
            self._cleanup_local_cache(current_time)
            self.cache_cleanup_time = current_time
        
        if key not in self.local_cache:
            self.local_cache[key] = []
        
        # Remove expired requests
        window_start = current_time - window
        self.local_cache[key] = [
            req_time for req_time in self.local_cache[key] 
            if req_time > window_start
        ]
        
        current_count = len(self.local_cache[key])
        
        if current_count < limit:
            self.local_cache[key].append(current_time)
            remaining = limit - current_count - 1
            return True, remaining, window
        else:
            return False, 0, window
    
    def _cleanup_local_cache(self, current_time: int):
        """Lokalen Cache aufräumen"""
        for key in list(self.local_cache.keys()):
            # Remove entries older than 1 hour
            self.local_cache[key] = [
                req_time for req_time in self.local_cache[key]
                if current_time - req_time < 3600
            ]
            # Remove empty entries
            if not self.local_cache[key]:
                del self.local_cache[key]
    
    def check_rate_limit(
        self, 
        request: Request, 
        rate_limit: str
    ) -> Tuple[bool, Dict[str, int]]:
        """Rate-Limit prüfen"""
        if not settings.RATE_LIMIT_ENABLED:
            return True, {"remaining": 9999, "reset": 3600}
        
        client_id = self._get_client_id(request)
        endpoint = request.url.path
        limit, window = self._parse_rate_limit(rate_limit)
        
        # Create unique key for this endpoint and time window
        window_id = int(time.time()) // window
        key = self._get_rate_limit_key(client_id, endpoint, str(window_id))
        
        allowed, remaining, reset_time = self._sliding_window_counter(
            key, limit, window
        )
        
        headers = {
            "remaining": remaining,
            "reset": reset_time
        }
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id} on {endpoint}: "
                f"{limit} requests per {window}s"
            )
        
        return allowed, headers


# Global Rate Limiter Instance
rate_limiter = RateLimiter(redis_client)


def get_endpoint_rate_limit(path: str) -> str:
    """Bestimme Rate-Limit basierend auf Endpoint"""
    endpoint_limits = {
        # Authentication endpoints
        "/api/auth/login": "10/minute",
        "/api/auth/refresh": "30/minute",
        
        # Call endpoints (resource-intensive)
        "/api/calls/": "20/minute",
        "/api/calls/outbound": "10/minute",
        
        # Audio processing (sehr resource-intensive)
        "/api/audio/transcribe": "5/minute",
        "/api/audio/synthesize": "10/minute",
        
        # AI conversation
        "/api/ai/conversation": "50/minute",
        
        # Webhooks (hoher Durchsatz erlaubt)
        "/api/webhooks/": "200/minute",
        
        # General API endpoints
        "/api/users/": "100/minute",
        "/api/organizations/": "100/minute",
        
        # Analytics (read-heavy)
        "/api/analytics/": "200/minute",
    }
    
    # Find matching pattern
    for pattern, limit in endpoint_limits.items():
        if path.startswith(pattern):
            return limit
    
    # Default rate limit
    return settings.RATE_LIMIT_GENERAL


async def rate_limit_middleware(request: Request, call_next):
    """Rate-Limiting Middleware für FastAPI"""
    # Skip rate limiting for health checks and docs
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        response = await call_next(request)
        return response
    
    # Get rate limit for this endpoint
    rate_limit = get_endpoint_rate_limit(request.url.path)
    
    # Check rate limit
    allowed, headers = rate_limiter.check_rate_limit(request, rate_limit)
    
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate Limit Exceeded",
                "message": f"Too many requests. Rate limit: {rate_limit}",
                "retry_after": headers["reset"]
            },
            headers={
                "X-RateLimit-Remaining": str(headers["remaining"]),
                "X-RateLimit-Reset": str(headers["reset"]),
                "Retry-After": str(headers["reset"])
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to response
    response.headers["X-RateLimit-Remaining"] = str(headers["remaining"])
    response.headers["X-RateLimit-Reset"] = str(headers["reset"])
    
    return response


class RateLimitDependency:
    """Dependency für spezifische Rate-Limits"""
    
    def __init__(self, rate_limit: str):
        self.rate_limit = rate_limit
    
    async def __call__(self, request: Request):
        """Rate-Limit-Check als Dependency"""
        allowed, headers = rate_limiter.check_rate_limit(request, self.rate_limit)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Rate limit: {self.rate_limit}",
                    "retry_after": headers["reset"]
                },
                headers={
                    "X-RateLimit-Remaining": str(headers["remaining"]),
                    "X-RateLimit-Reset": str(headers["reset"]),
                    "Retry-After": str(headers["reset"])
                }
            )
        
        return headers


# Predefined Rate Limit Dependencies
strict_rate_limit = RateLimitDependency("5/minute")    # Für kritische Operationen
medium_rate_limit = RateLimitDependency("30/minute")   # Für normale Operationen
lenient_rate_limit = RateLimitDependency("200/minute") # Für Read-Only Operationen