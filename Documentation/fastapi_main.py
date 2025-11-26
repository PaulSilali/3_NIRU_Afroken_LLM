"""
AfroKen LLM - Monolithic FastAPI Application
Main Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# Import routers
from app.api import v1_router
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import setup_logging, log_request
from app.core.database import Database
from app.core.cache import Cache
from app.settings import Settings

# Configure logging
logger = logging.getLogger(__name__)
settings = Settings()

# Global instances
db = None
cache = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager
    Handles startup and shutdown events
    """
    # ================== STARTUP ==================
    global db, cache
    
    try:
        # Initialize database
        db = Database(settings)
        await db.connect()
        logger.info("✅ Database connected")
        
        # Initialize cache
        cache = Cache(settings)
        await cache.connect()
        logger.info("✅ Redis cache connected")
        
        # Load LLM models (lazy load on first request)
        logger.info("✅ LLM initialization deferred to first request")
        
        logger.info("🚀 AfroKen LLM backend started successfully")
    
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # ================== SHUTDOWN ==================
    try:
        if db:
            await db.disconnect()
            logger.info("✅ Database disconnected")
        
        if cache:
            await cache.disconnect()
            logger.info("✅ Redis cache disconnected")
        
        logger.info("🛑 AfroKen LLM backend shut down gracefully")
    
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")
        raise


# Create FastAPI application
app = FastAPI(
    title="AfroKen LLM - Citizen Service Copilot",
    description="AI-powered government service assistant for Kenya",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Total-Pages"]
)

# Trust proxy headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Setup exception handlers
setup_exception_handlers(app)

# Setup logging middleware
setup_logging(app)


# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    response = await call_next(request)
    await log_request(request, response)
    return response


# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Returns: Service health status
    """
    return {
        "status": "healthy",
        "service": "AfroKen LLM Backend",
        "version": "1.0.0",
        "timestamp": None  # Will be set by middleware
    }


@app.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    Returns 503 if not ready
    """
    try:
        # Check database
        if db:
            async with db.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        
        # Check cache
        if cache:
            await cache.ping()
        
        return {"status": "ready"}
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint
    """
    # Return Prometheus formatted metrics
    return "# HELP afroken_requests_total Total requests\n"


# ============================================================================
# API ROUTES
# ============================================================================

# Include v1 routes
app.include_router(
    v1_router.router,
    prefix="/api/v1",
    tags=["v1"]
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "name": "AfroKen LLM",
        "description": "AI-powered Citizen Service Copilot for Kenya",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "ready": "/ready"
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "Unknown error"
        }
    )


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_db() -> Database:
    """Get database instance"""
    return db


async def get_cache() -> Cache:
    """Get cache instance"""
    return cache


# Expose for dependency injection in routers
app.dependency_overrides = {
    "db": get_db,
    "cache": get_cache
}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level="info"
    )
