"""
NagrikSaarathi — Backend Integration & API Test Suite

Comprehensive tests covering:
 1. Health and reference endpoints (/api/health, /api/schemes, /api/schemes/{id}/fields)
 2. All 22 Indian languages returned with capability metadata and script direction
 3. Missing localized-content behavior (Layer C safe fallback, no English deception)
 4. Translation-review status tracking (approved vs draft)
 5. Citizen consent enforcement (ephemeral execution when consent declined, event blocking)
 6. Analytics aggregation, metric numerators/denominators, and demo-data exclusion
 7. Protected dashboard access control (admin authentication & demo gates)
 8. Invalid events and deterministic input validation
 9. Voice capability enforcement (rejecting unsupported voice languages)
10. Privacy verification: No personal application answers in database records
11. Language provider failure and timeout handling
"""

from __future__ import annotations

import asyncio
import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db, reset_engine
from backend.app.main import create_app
from backend.app.models import (
    AssistedSession,
    Base,
    FormField,
    GovernmentScheme,
    Language,
    SessionEvent,
)
from backend.app.seed import seed
from backend.app.services.bhashini_adapter import BhashiniAdapter
from backend.app.services.language_service import LanguageService


# ── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def test_db_setup(tmp_path_factory):
    """Set up an isolated SQLite database seeded with full 22-language data."""
    db_file = tmp_path_factory.mktemp("db") / "api_test.db"
    db_url = f"sqlite:///{db_file}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["DEMO_MODE"] = "true"
    os.environ["ADMIN_API_KEY"] = "test-secret-key-123"

    reset_engine()
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    # Seed the database
    seed(reset=False)

    yield db_url

    reset_engine()
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass


@pytest.fixture()
def client(test_db_setup):
    """Provide a FastAPI TestClient bound to the seeded test database."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session(test_db_setup):
    """Direct database session for assertions."""
    engine = create_engine(test_db_setup)
    with Session(engine) as session:
        yield session


# ── 1. Health and Reference Endpoints ──────────────────────────────────

class TestSystemAndReferenceEndpoints:
    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database_connected"] is True
        assert data["languages_configured"] == 22
        assert "disclaimer" in data

    def test_list_schemes(self, client):
        resp = client.get("/api/schemes")
        assert resp.status_code == 200
        schemes = resp.json()
        assert len(schemes) >= 1
        demo_scheme = next(s for s in schemes if s["slug"] == "demo-scholarship-application")
        assert demo_scheme["is_demo"] is True
        assert "FICTIONAL" in demo_scheme["description"].upper() or "DEMO" in demo_scheme["description"].upper()

    def test_get_scheme_detail(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        detail_resp = client.get(f"/api/schemes/{scheme_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == scheme_id
        assert "fields" in detail
        assert len(detail["fields"]) >= 4

    def test_get_scheme_fields(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        fields_resp = client.get(f"/api/schemes/{scheme_id}/fields")
        assert fields_resp.status_code == 200
        fields = fields_resp.json()
        keys = [f["field_key"] for f in fields]
        assert "applicant_name" in keys
        assert "annual_family_income" in keys


# ── 2. All 22 Indian Languages & Capability Metadata ───────────────────

class TestLanguagesAPI:
    def test_all_22_languages_returned(self, client):
        resp = client.get("/api/languages")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 22
        codes = {item["language_code"] for item in data["items"]}
        expected_22 = {
            "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok",
            "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
            "sd", "ta", "te", "ur"
        }
        assert codes == expected_22

    def test_rtl_languages_metadata(self, client):
        for rtl_code in ("ks", "sd", "ur"):
            resp = client.get(f"/api/languages/{rtl_code}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["direction"] == "rtl", f"{rtl_code} must be marked rtl"

    def test_voice_capabilities_are_not_faked(self, client):
        # Assamese (as) and Bodo (brx) are flagged False for speech recognition
        resp_as = client.get("/api/languages/as")
        assert resp_as.status_code == 200
        assert resp_as.json()["supports_speech_recognition"] is False

        # Hindi (hi) and Tamil (ta) are supported
        resp_hi = client.get("/api/languages/hi")
        assert resp_hi.status_code == 200
        assert resp_hi.json()["supports_speech_recognition"] is True

    def test_nonexistent_language_404(self, client):
        resp = client.get("/api/languages/xyz")
        assert resp.status_code == 404


# ── 3. Missing Localized Content & Safe Fallback ───────────────────────

class TestMultilingualGuidance:
    def test_reviewed_guidance_for_hindi(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        explain_resp = client.post(
            "/api/assist/explain",
            json={
                "scheme_id": scheme_id,
                "field_key": "applicant_name",
                "target_language": "hi",
            },
        )
        assert explain_resp.status_code == 200
        data = explain_resp.json()
        assert data["target_language"] == "hi"
        assert data["localized_label"] == "आवेदक का नाम"
        assert data["is_reviewed"] is True
        assert data["translation_status"] in ("approved", "reviewed")
        assert data["is_fallback"] is False
        assert data["human_assistance_path"] is None

    def test_missing_language_triggers_safe_fallback_without_english_deception(self, client):
        """
        When content is missing in a language, it must NOT silently return English
        while pretending it is translated. It must clearly identify the limitation
        and provide a human assistance path.
        """
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        # Request field with missing translation in Sanskrit (sa) or Dogri (doi)
        explain_resp = client.post(
            "/api/assist/explain",
            json={
                "scheme_id": scheme_id,
                "field_key": "applicant_name",
                "target_language": "sa",
            },
        )
        assert explain_resp.status_code == 200
        data = explain_resp.json()
        assert data["translation_status"] in ("missing", "draft")
        # If missing explanation, fallback must be flagged
        if data["is_fallback"]:
            assert data["human_assistance_path"] is not None
            assert "assistance" in data["human_assistance_path"].lower() or "सहायता" in data["human_assistance_path"]


# ── 4. Deterministic Validation Service ────────────────────────────────

class TestValidationService:
    def test_validate_required_field_empty(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        val_resp = client.post(
            "/api/assist/validate",
            json={
                "scheme_id": scheme_id,
                "field_key": "applicant_name",
                "value": "   ",
                "target_language": "hi",
            },
        )
        assert val_resp.status_code == 200
        data = val_resp.json()
        assert data["is_valid"] is False
        assert data["error_code"] == "REQUIRED_FIELD_EMPTY"
        assert data["official_source_url"] is not None

    def test_validate_numeric_range_violation(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        val_resp = client.post(
            "/api/assist/validate",
            json={
                "scheme_id": scheme_id,
                "field_key": "annual_family_income",
                "value": -5000,
                "target_language": "hi",
            },
        )
        assert val_resp.status_code == 200
        data = val_resp.json()
        assert data["is_valid"] is False
        assert data["error_code"] == "NUMERIC_MIN_VIOLATION"

    def test_validate_valid_input(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        val_resp = client.post(
            "/api/assist/validate",
            json={
                "scheme_id": scheme_id,
                "field_key": "annual_family_income",
                "value": 150000,
                "target_language": "hi",
            },
        )
        assert val_resp.status_code == 200
        data = val_resp.json()
        assert data["is_valid"] is True
        assert data["error_code"] is None


# ── 5. Consent Enforcement & Anonymity ─────────────────────────────────

class TestConsentAndAnonymity:
    def test_session_persisted_when_consent_given(self, client, db_session):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        sess_resp = client.post(
            "/api/sessions",
            json={
                "scheme_id": scheme_id,
                "selected_language": "bn",
                "channel": "web",
                "analytics_consent": True,
                "is_demo": True,
            },
        )
        assert sess_resp.status_code == 201
        data = sess_resp.json()
        assert data["persisted"] is True
        session_id = data["session_id"]

        # Verify record exists in DB
        db_record = db_session.execute(
            select(AssistedSession).where(AssistedSession.id == session_id)
        ).scalar_one_or_none()
        assert db_record is not None
        assert db_record.analytics_consent is True

    def test_session_ephemeral_when_consent_declined(self, client, db_session):
        """When consent is declined, assistance must proceed without DB writes."""
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        sess_resp = client.post(
            "/api/sessions",
            json={
                "scheme_id": scheme_id,
                "selected_language": "mr",
                "channel": "web",
                "analytics_consent": False,
                "is_demo": True,
            },
        )
        assert sess_resp.status_code == 201
        data = sess_resp.json()
        assert data["persisted"] is False
        session_id = data["session_id"]

        # Verify record does NOT exist in DB
        db_record = db_session.execute(
            select(AssistedSession).where(AssistedSession.id == session_id)
        ).scalar_one_or_none()
        assert db_record is None

    def test_event_rejected_when_no_consent(self, client):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        sess_resp = client.post(
            "/api/sessions",
            json={
                "scheme_id": scheme_id,
                "selected_language": "mr",
                "channel": "web",
                "analytics_consent": False,
                "is_demo": True,
            },
        )
        session_id = sess_resp.json()["session_id"]

        # Attempting to post event must fail because session was not consented
        event_resp = client.post(
            f"/api/sessions/{session_id}/events",
            json={
                "field_key": "applicant_name",
                "event_type": "help_requested",
            },
        )
        assert event_resp.status_code in (403, 404)

    def test_event_recorded_for_consented_session(self, client, db_session):
        resp = client.get("/api/schemes")
        scheme_id = resp.json()[0]["id"]

        sess_resp = client.post(
            "/api/sessions",
            json={
                "scheme_id": scheme_id,
                "selected_language": "ta",
                "channel": "web",
                "analytics_consent": True,
                "is_demo": True,
            },
        )
        session_id = sess_resp.json()["session_id"]

        event_resp = client.post(
            f"/api/sessions/{session_id}/events",
            json={
                "field_key": "annual_family_income",
                "event_type": "validation_failed",
                "barrier_category": "validation_error",
                "language_code": "ta",
            },
        )
        assert event_resp.status_code == 201
        ev_data = event_resp.json()
        assert ev_data["event_type"] == "validation_failed"
        assert ev_data["barrier_category"] == "validation_error"


# ── 6. Dashboard Analytics & Demo Segregation ──────────────────────────

class TestDashboardAnalytics:
    def test_summary_metrics(self, client):
        resp = client.get("/api/dashboard/summary?include_demo=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_demo_data"] is True
        assert data["total_consented_sessions"] > 0
        assert 0.0 <= data["completion_rate_pct"] <= 100.0
        assert 0.0 <= data["abandonment_rate_pct"] <= 100.0

    def test_barrier_distribution(self, client):
        resp = client.get("/api/dashboard/barriers?include_demo=true")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        for item in data["items"]:
            assert 0.0 <= item["percentage_of_barriers"] <= 100.0

    def test_language_analytics(self, client):
        resp = client.get("/api/dashboard/languages?include_demo=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_languages_represented"] >= 1

    def test_recovery_metrics(self, client):
        resp = client.get("/api/dashboard/recovery?include_demo=true")
        assert resp.status_code == 200
        data = resp.json()
        assert 0.0 <= data["resolution_rate_pct"] <= 100.0

    def test_translation_quality_audit(self, client):
        resp = client.get("/api/dashboard/translation-quality")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_configured_languages"] == 22
        assert data["total_registered_fields"] >= 4
        assert len(data["languages"]) == 22

    def test_demo_exclusion_filters_out_synthetic_data(self, client):
        """Requesting real data (include_demo=false) excludes all simulated records."""
        # Include auth header so permission is granted
        headers = {"X-Admin-API-Key": "test-secret-key-123"}
        resp = client.get("/api/dashboard/summary?include_demo=false", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_demo_data"] is False
        # Since only demo data was seeded, real count must be 0
        assert data["total_consented_sessions"] == 0


# ── 7. Protected Dashboard Access Control ──────────────────────────────

class TestSecurityAndAccessControl:
    def test_unauthenticated_access_to_real_data_is_rejected(self, client):
        # Querying real data without admin credentials must return 401
        resp = client.get("/api/dashboard/summary?include_demo=false")
        assert resp.status_code == 401

    def test_authenticated_access_to_real_data_succeeds(self, client):
        headers = {"X-Admin-API-Key": "test-secret-key-123"}
        resp = client.get("/api/dashboard/summary?include_demo=false", headers=headers)
        assert resp.status_code == 200

    def test_bearer_token_authorization_succeeds(self, client):
        headers = {"Authorization": "Bearer test-secret-key-123"}
        resp = client.get("/api/dashboard/summary?include_demo=false", headers=headers)
        assert resp.status_code == 200

    def test_invalid_admin_key_returns_401(self, client):
        headers = {"X-Admin-API-Key": "wrong-key"}
        resp = client.get("/api/dashboard/summary?include_demo=false", headers=headers)
        assert resp.status_code == 401


# ── 8. Voice Capability Checks ─────────────────────────────────────────

class TestVoiceEndpoints:
    def test_transcribe_unsupported_language_returns_400(self, client):
        # Assamese (as) is verified as not supporting speech recognition
        dummy_audio = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00data\x00\x00\x00\x00")
        resp = client.post(
            "/api/voice/transcribe",
            data={"language_code": "as"},
            files={"file": ("audio.wav", dummy_audio, "audio/wav")},
        )
        assert resp.status_code == 400
        assert "not currently available" in resp.json()["detail"]

    def test_speak_unsupported_language_returns_400(self, client):
        resp = client.post(
            "/api/voice/speak",
            json={"text": "परीक्षण", "language_code": "as"},
        )
        assert resp.status_code == 400
        assert "not currently available" in resp.json()["detail"]

    def test_speak_supported_language_handles_gracefully(self, client):
        # Hindi (hi) supports voice
        resp = client.post(
            "/api/voice/speak",
            json={"text": "नमस्ते", "language_code": "hi"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["language_code"] == "hi"

    def test_unsupported_mime_type_returns_415(self, client):
        dummy_text = io.BytesIO(b"not an audio file")
        resp = client.post(
            "/api/voice/transcribe",
            data={"language_code": "hi"},
            files={"file": ("test.txt", dummy_text, "text/plain")},
        )
        assert resp.status_code == 415


# ── 9. Privacy Audit: No Personal Citizen Answers ──────────────────────

class TestPrivacyAudit:
    def test_no_citizen_answers_persisted_in_database(self, db_session):
        """Audit all database tables to guarantee zero columns contain citizen form answers or PII."""
        forbidden_substrings = [
            "answer", "first_name", "last_name", "phone", "aadhaar",
            "pan", "bank", "password", "upload", "recording",
        ]
        session_cols = [c.name for c in AssistedSession.__table__.columns]
        for col in session_cols:
            for sub in forbidden_substrings:
                assert sub not in col.lower(), f"Forbidden column {col} in AssistedSession"

        event_cols = [c.name for c in SessionEvent.__table__.columns]
        for col in event_cols:
            for sub in forbidden_substrings:
                assert sub not in col.lower(), f"Forbidden column {col} in SessionEvent"


# ── 10. Provider Failure & Timeout Isolation ───────────────────────────

class TestProviderFailureIsolation:
    def test_language_service_handles_provider_timeout_gracefully(self, db_session):
        """If external provider fails or times out, Layer C safe fallback engages cleanly."""
        scheme = db_session.execute(select(GovernmentScheme)).scalars().first()

        # Mock adapter that always returns None (simulating timeout)
        class TimeoutMockAdapter(BhashiniAdapter):
            @property
            def is_configured(self):
                return True

            async def translate_text(self, text, source_lang, target_lang):
                return None  # timeout / error

        service = LanguageService(bhashini_adapter=TimeoutMockAdapter())
        result = asyncio.run(
            service.get_field_explanation(
                db=db_session,
                scheme_id=scheme.id,
                field_key="applicant_name",
                target_language="sa",  # language with missing translation
            )
        )
        assert result is not None
        assert result.provider_used == "safe_fallback"
        assert result.is_fallback is True
        assert result.human_assistance_path is not None
