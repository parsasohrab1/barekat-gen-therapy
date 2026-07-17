from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.api.v1 import auth, compliance, design, jobs, lab, models, molecules, predict, synthetic
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import setup_logging

setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            environment=settings.ENVIRONMENT,
            traces_sample_rate=0.1,
        )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="پلتفرم end-to-end طراحی و بهینه‌سازی ناقل‌های ژنی",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(design.router, prefix="/api/v1/design", tags=["design"])
app.include_router(predict.router, prefix="/api/v1/predict", tags=["predict"])
app.include_router(synthetic.router, prefix="/api/v1/synthetic", tags=["synthetic"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(lab.router, prefix="/api/v1/lab", tags=["lab"])
app.include_router(molecules.router, prefix="/api/v1/molecules", tags=["molecules"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])


def _check_database() -> str:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


def _check_redis() -> str:
    try:
        import redis

        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        client.ping()
        return "ok"
    except Exception:
        return "error"


def _check_qdrant() -> str:
    if not settings.QDRANT_ENABLED:
        return "disabled"
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=settings.QDRANT_URL, timeout=2)
        client.get_collections()
        return "ok"
    except Exception:
        return "error"


@app.get("/api/v1/health")
def health_check():
    db_status = _check_database()
    redis_status = _check_redis()
    qdrant_status = _check_qdrant()
    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall,
        "version": settings.VERSION,
        "auth_enabled": settings.AUTH_ENABLED,
        "services": {
            "database": db_status,
            "redis": redis_status,
            "qdrant": qdrant_status,
        },
    }
