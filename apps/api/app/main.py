from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from sqlalchemy import text

from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import RequestLoggingMiddleware

app = FastAPI(
    title="Handelny API",
    description="API for the Handelny AI SaaS Platform",
    version="0.1.0",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.get("/api/v1/health")
async def health_check():
    checks = {"database": "unknown", "qdrant": "unknown"}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc}"

    try:
        QdrantClient(url=settings.qdrant_url).get_collections()
        checks["qdrant"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["qdrant"] = f"error: {exc}"

    overall_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ok" if overall_ok else "degraded",
        "message": "Handelny API is running",
        "checks": checks,
    }


from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")
