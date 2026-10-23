"""
MAUSAM — FastAPI Application Entry Point
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_indexes, ping_db
from app.api.v1 import router as api_v1_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info(f"MAUSAM starting — env={settings.APP_ENV} version={settings.APP_VERSION}")
    try:
        init_indexes()
        logger.info("Database indexes initialized")
    except Exception as e:
        logger.warning(f"Index init warning (non-fatal in serverless): {e}")
    yield
    logger.info("MAUSAM shutting down")


app = FastAPI(
    title="MAUSAM API",
    description="AI Cash-Flow Intelligence Platform for Indian MSMEs",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ─── REQUEST LOGGING ─────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# ─── GLOBAL ERROR HANDLER ────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred."},
    )


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────
@app.get("/api/v1/health", tags=["health"])
async def health_check():
    db_ok = ping_db()
    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "connected" if db_ok else "unreachable",
        "demo_mode": settings.DEMO_MODE,
        "integrations": {
            "bedrock": settings.BEDROCK_ENABLED,
            "textract": settings.TEXTRACT_ENABLED,
            "translate": settings.TRANSLATE_ENABLED,
            "polly": settings.POLLY_ENABLED,
            "kms_signing": settings.KMS_SIGNING_ENABLED,
            "cognito": settings.COGNITO_ENABLED,
        },
    }


# ─── ROUTES ───────────────────────────────────────────────────────────────────
app.include_router(api_v1_router, prefix="/api/v1")
