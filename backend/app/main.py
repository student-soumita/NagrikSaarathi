"""
NagrikSaarathi (नागरिक सारथी) — FastAPI Backend Application

A secure, multilingual government-service application assistance platform
supporting the 22 Eighth Schedule Indian languages.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.routers import (
    admin,
    assist,
    auth,
    dashboard,
    department,
    health,
    help,
    languages,
    schemes,
    sessions,
    voice,
)


from backend.app.database import get_engine
from backend.app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and graceful shutdown."""
    settings = get_settings()
    # Initialize all database tables safely
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic if any


def create_app() -> FastAPI:
    """Application factory for NagrikSaarathi."""
    settings = get_settings()

    app = FastAPI(
        title="NagrikSaarathi API (नागरिक सारथी)",
        description=(
            "Multilingual government-service application assistance platform.\n\n"
            "Features:\n"
            "- Full support for all 22 official Indian languages.\n"
            "- Anonymous, consent-based barrier analytics.\n"
            "- 3-layer language engine (Stored guidance, Provider adapter, Safe fallback).\n"
            "- Ephemeral voice services with strict capability enforcement.\n\n"
            "DISCLAIMER: NagrikSaarathi provides citizen guidance; it does NOT submit applications "
            "directly to official government systems."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register API routers under /api prefix
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(languages.router, prefix="/api")
    app.include_router(schemes.router, prefix="/api")
    app.include_router(sessions.router, prefix="/api")
    app.include_router(assist.router, prefix="/api")
    app.include_router(help.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(department.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    app.include_router(voice.router, prefix="/api")

    return app


app = create_app()
