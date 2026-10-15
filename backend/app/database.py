"""
NagrikSaarathi — Database Engine & Session Factory

Provides a single ``get_engine`` / ``get_session`` entry-point so that
every part of the application (migrations, seeds, tests) uses the same
wiring.  Supports both SQLite (local dev) and PostgreSQL (production).
"""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import Settings, get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _apply_sqlite_pragmas(engine: Engine) -> None:
    """Enable WAL mode and foreign-key enforcement on SQLite."""

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):  # noqa: ANN001
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def get_engine(settings: Settings | None = None) -> Engine:
    """Return (and cache) the global SQLAlchemy engine."""
    global _engine
    if _engine is not None:
        return _engine
    settings = settings or get_settings()
    _engine = create_engine(
        settings.database_url,
        echo=settings.echo_sql,
        future=True,
    )
    if settings.database_url.startswith("sqlite"):
        _apply_sqlite_pragmas(_engine)
    return _engine


def get_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    """Return (and cache) the global session factory."""
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    engine = get_engine(settings)
    _SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return _SessionLocal


def reset_engine() -> None:
    """Dispose of the cached engine — useful for tests."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_db():
    """FastAPI dependency yielding a database session."""
    factory = get_session_factory()
    with factory() as session:
        yield session
