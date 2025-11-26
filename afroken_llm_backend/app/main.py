import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.db import init_db
from app.api.routes import auth, chat, admin, ussd


REQUEST_COUNT = Counter("afroken_requests_total", "Total requests")
REQUEST_LATENCY = Histogram("afroken_request_latency_seconds", "Request latency seconds")


app = FastAPI(title="AfroKen LLM API", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "development" else ["https://your.gov.domain"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(ussd.router, prefix="/api/v1/ussd", tags=["ussd"])


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    app.state.model_lock = asyncio.Lock()
    print("AfroKen backend startup complete")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AfroKen Backend", "version": "0.1.0"}


@app.get("/ready")
async def ready():
    try:
        # Here you could ping DB/Redis/MinIO if desired
        return {"status": "ready"}
    except Exception as exc:  # pragma: no cover - defensive
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "error": str(exc)}
        )


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response



