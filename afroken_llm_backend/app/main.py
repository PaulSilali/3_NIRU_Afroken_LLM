"""
Main FastAPI application for the AfroKen LLM backend.

This module:
- Creates the ASGI app instance.
- Sets up CORS.
- Registers API routers.
- Exposes health/readiness/metrics endpoints.
- Initializes the database and a global async lock on startup.
- Preloads RAG resources for faster first query.
"""

import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.db import init_db
from app.api.routes import auth, chat, admin, ussd

# Preload RAG resources on startup
try:
    from app.api.routes.chat import _load_rag_resources
    from app.utils.embeddings_fallback import get_embedding as preload_embedding
    # Preload embedding model
    _ = preload_embedding("preload")
except Exception as e:
    print(f"Warning: Could not preload RAG resources: {e}")


# Prometheus counter that increments for every HTTP request received by the app.
REQUEST_COUNT = Counter("afroken_requests_total", "Total requests")
# Prometheus histogram tracking latency (in seconds) for HTTP requests.
REQUEST_LATENCY = Histogram("afroken_request_latency_seconds", "Request latency seconds")


# Create the FastAPI application with a title and version for OpenAPI docs.
app = FastAPI(title="AfroKen LLM API", version="0.1.0")


# Register CORS middleware so that browsers can call this API from web frontends.
app.add_middleware(
    CORSMiddleware,
    # Allow any origin in development, but lock down to a specific domain in production.
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative port
        "http://localhost:5174",  # Vite alternative
        "*"  # Allow all in development
    ] if settings.ENV == "development" else ["https://your.gov.domain"],
    # Allow cookies / auth headers to be sent cross-origin if needed.
    allow_credentials=True,
    # Allow all HTTP methods (GET, POST, PUT, etc.).
    allow_methods=["*"],
    # Allow all request headers (e.g. Authorization, Content-Type).
    allow_headers=["*"],
)


# Routers
# Mount authentication-related endpoints under `/api/v1/auth`.
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# Mount chat / LLM interaction endpoints under `/api/v1/chat`.
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
# Mount admin/document ingestion endpoints under `/api/v1/admin`.
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
# Mount USSD integration endpoints under `/api/v1/ussd`.
app.include_router(ussd.router, prefix="/api/v1/ussd", tags=["ussd"])


@app.on_event("startup")
async def on_startup() -> None:
    """
    FastAPI startup hook.

    - Initializes the database schema (creates tables if missing).
    - Creates and stores a global asyncio lock in `app.state` that can be shared
      by other parts of the application to serialize access to a single LLM,
      if required.
    - Preloads RAG resources for faster first query.
    """

    # Run table creation against the configured database.
    init_db()
    # Store a global async lock that can be used to guard model access.
    app.state.model_lock = asyncio.Lock()
    
    # Preload RAG resources
    try:
        _load_rag_resources()
        print("✓ RAG resources preloaded")
    except Exception as e:
        print(f"⚠ RAG resources not available: {e}")
    
    # Log a simple startup message for debugging/observability.
    print("AfroKen backend startup complete")


@app.get("/health")
async def health():
    """
    Lightweight liveness endpoint.

    Returns a static JSON body indicating that the service process is up.
    """

    return {"status": "healthy", "service": "AfroKen Backend", "version": "0.1.0"}


@app.get("/ready")
async def ready():
    """
    Readiness endpoint.

    In a full deployment you could verify dependencies here (DB, Redis, MinIO, etc.)
    and only return 200 once they respond correctly.
    """

    try:
        # Here you could ping DB/Redis/MinIO if desired; for now we assume ready.
        return {"status": "ready"}
    except Exception as exc:  # pragma: no cover - defensive
        # In case of unexpected errors, expose a 503 with error details for debugging.
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "error": str(exc)}
        )


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics scrape endpoint.

    Exposes internal counters/histograms for monitoring systems to consume.
    """

    # Generate the latest metrics snapshot in Prometheus text format.
    data = generate_latest()
    # Wrap it in a standard `Response` with the appropriate content type.
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    """
    HTTP middleware that wraps every request to record metrics.

    - Increments a global request counter.
    - Measures how long the request took and records it in a histogram.
    """

    # Increment the global request counter for every incoming request.
    REQUEST_COUNT.inc()
    # `time()` is a context manager: code inside the block is measured for duration.
    with REQUEST_LATENCY.time():
        # Delegate to the next middleware / route handler.
        response = await call_next(request)
    # Return the (possibly modified) response object back to the client.
    return response
