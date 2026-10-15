"""
NagrikSaarathi — Application Configuration

Reads configuration from the environment with secure defaults.
Falls back to local SQLite for development.
Never logs or exposes sensitive API keys or credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_PATH = _PROJECT_ROOT / "nagarik_saarathi.db"
_DEFAULT_DB_URL = f"sqlite:///{_DEFAULT_DB_PATH.as_posix()}"


@dataclass(frozen=True)
class Settings:
    """Immutable application settings resolved once at startup."""

    # Database
    database_url: str = field(
        default_factory=lambda: os.environ.get(
            "DATABASE_URL",
            _DEFAULT_DB_URL,
        )
    )
    echo_sql: bool = field(
        default_factory=lambda: os.environ.get("ECHO_SQL", "").lower() in ("1", "true", "yes")
    )

    # Security & Access Control
    app_env: str = field(
        default_factory=lambda: os.environ.get("APP_ENV", "development").lower()
    )
    demo_mode: bool = field(
        default_factory=lambda: os.environ.get("DEMO_MODE", "true").lower() in ("1", "true", "yes")
    )
    admin_api_key: str = field(
        default_factory=lambda: os.environ.get("ADMIN_API_KEY", "demo-nagrik-admin-key-2026")
    )
    frontend_origins: str = field(
        default_factory=lambda: os.environ.get(
            "FRONTEND_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178,http://localhost:5179,http://localhost:5180,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5179",
        )
    )

    # Multilingual Provider (e.g., BHASHINI / external)
    bhashini_endpoint: str | None = field(
        default_factory=lambda: os.environ.get("BHASHINI_ENDPOINT") or None
    )
    bhashini_api_key: str | None = field(
        default_factory=lambda: os.environ.get("BHASHINI_API_KEY") or None
    )
    bhashini_user_id: str | None = field(
        default_factory=lambda: os.environ.get("BHASHINI_USER_ID") or None
    )
    bhashini_pipeline_id: str | None = field(
        default_factory=lambda: os.environ.get("BHASHINI_PIPELINE_ID") or None
    )
    provider_timeout_seconds: float = field(
        default_factory=lambda: float(os.environ.get("LANGUAGE_PROVIDER_TIMEOUT_SECONDS", "5.0"))
    )

    # Voice upload limits
    max_voice_payload_bytes: int = field(
        default_factory=lambda: int(os.environ.get("MAX_VOICE_PAYLOAD_BYTES", str(2 * 1024 * 1024)))
    )

    # Seed-data controls
    seed_demo_sessions: int = 12
    seed_demo_events_per_session: int = 6

    @property
    def cors_origins_list(self) -> List[str]:
        """Return parsed list of allowed CORS origins."""
        if not self.frontend_origins:
            return ["*"]
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


def get_settings() -> Settings:
    """Return an application-wide Settings instance."""
    return Settings()
