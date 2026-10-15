"""
NagrikSaarathi — Database Test Suite

Covers:
 1.  Fresh database creation
 2.  Migration application (via metadata.create_all for unit-test speed)
 3.  Seeding all 22 languages
 4.  Unique language-code constraint
 5.  Foreign-key constraints
 6.  Idempotent seed execution
 7.  Translation-review status separate from language availability
 8.  No application-answer fields in analytics records
 9.  Demo-data labelling
10.  Check constraints on enums
11.  Privacy — AssistedSession and SessionEvent column audit
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models import (
    AssistedSession,
    Base,
    FormField,
    GovernmentScheme,
    Language,
    SessionEvent,
    TranslationReview,
)
from backend.app.seed import LANGUAGES, seed
from backend.app.config import Settings
from backend.app.database import get_engine, get_session_factory, reset_engine


# ── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _isolate_engine():
    """Reset the module-level cached engine before and after every test."""
    reset_engine()
    yield
    reset_engine()


@pytest.fixture()
def db_url(tmp_path) -> str:
    """Return a SQLite URL in the tmp directory."""
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture()
def engine(db_url):
    eng = create_engine(db_url, echo=False)

    @event.listens_for(eng, "connect")
    def _fk(dbapi_conn, _cr):
        dbapi_conn.execute("PRAGMA foreign_keys=ON;")

    return eng


@pytest.fixture()
def tables(engine):
    """Create all tables, yield, then drop."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def session(engine, tables):
    """Provide a transactional Session that rolls back after the test."""
    with Session(engine) as sess:
        yield sess


@pytest.fixture()
def seeded_session(db_url, tmp_path):
    """Run the full seed and return a usable session."""
    os.environ["DATABASE_URL"] = db_url
    settings = Settings(database_url=db_url)
    eng = get_engine(settings)
    Base.metadata.create_all(eng)
    factory = get_session_factory(settings)
    seed()
    with factory() as sess:
        yield sess


# ── 1. Fresh database creation ──────────────────────────────────────────

class TestFreshDatabase:
    def test_create_all_tables(self, engine):
        Base.metadata.create_all(engine)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected = {
            "languages",
            "government_schemes",
            "form_fields",
            "assisted_sessions",
            "session_events",
            "translation_reviews",
        }
        assert expected.issubset(tables), f"Missing tables: {expected - tables}"

    def test_tables_empty_after_creation(self, session):
        for model in (Language, GovernmentScheme, FormField, AssistedSession, SessionEvent, TranslationReview):
            count = session.execute(select(model)).all()
            assert len(count) == 0


# ── 2. Migration / schema consistency ──────────────────────────────────

class TestSchemaConsistency:
    def test_column_names_match_model(self, engine, tables):
        inspector = inspect(engine)
        lang_cols = {c["name"] for c in inspector.get_columns("languages")}
        expected = {
            "id", "language_code", "english_name", "native_name",
            "writing_system", "direction", "enabled",
            "supports_text", "supports_speech_recognition", "supports_text_to_speech",
        }
        assert expected == lang_cols

    def test_assisted_session_columns(self, engine, tables):
        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("assisted_sessions")}
        expected = {
            "id", "scheme_id", "selected_language", "channel",
            "status", "analytics_consent", "is_demo",
            "started_at", "ended_at",
        }
        assert expected == cols

    def test_session_event_columns(self, engine, tables):
        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("session_events")}
        expected = {
            "id", "session_id", "field_key", "event_type",
            "barrier_category", "resolution_status",
            "language_code", "created_at",
        }
        assert expected == cols

    def test_alembic_migrations_apply_and_downgrade(self, tmp_path):
        from alembic import command
        from alembic.config import Config

        mig_db_path = tmp_path / "alembic_test.db"
        mig_db_url = f"sqlite:///{mig_db_path}"
        os.environ["DATABASE_URL"] = mig_db_url

        alembic_ini_path = "backend/alembic.ini" if os.path.exists("backend/alembic.ini") else "alembic.ini"
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", mig_db_url)

        # 1. Apply upgrade to head
        command.upgrade(alembic_cfg, "head")

        mig_eng = create_engine(mig_db_url)
        inspector = inspect(mig_eng)
        mig_tables = set(inspector.get_table_names())
        expected = {
            "languages",
            "government_schemes",
            "form_fields",
            "assisted_sessions",
            "session_events",
            "translation_reviews",
            "alembic_version",
        }
        assert expected.issubset(mig_tables)

        # 2. Test downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector_after = inspect(mig_eng)
        tables_after = set(inspector_after.get_table_names())
        assert "languages" not in tables_after
        assert "assisted_sessions" not in tables_after
        mig_eng.dispose()


# ── 3. Seed all 22 languages ──────────────────────────────────────────

class TestLanguageSeed:
    def test_seed_populates_22_languages(self, seeded_session):
        langs = seeded_session.execute(select(Language)).scalars().all()
        assert len(langs) == 22

    def test_all_22_codes_present(self, seeded_session):
        codes = {
            row[0]
            for row in seeded_session.execute(select(Language.language_code)).all()
        }
        expected_codes = {ld["language_code"] for ld in LANGUAGES}
        assert codes == expected_codes

    def test_all_languages_enabled(self, seeded_session):
        disabled = seeded_session.execute(
            select(Language).where(Language.enabled == False)  # noqa: E712
        ).scalars().all()
        assert len(disabled) == 0

    def test_rtl_languages(self, seeded_session):
        rtl = seeded_session.execute(
            select(Language.language_code).where(Language.direction == "rtl")
        ).scalars().all()
        assert set(rtl) == {"ks", "sd", "ur"}

    def test_all_support_text(self, seeded_session):
        no_text = seeded_session.execute(
            select(Language).where(Language.supports_text == False)  # noqa: E712
        ).scalars().all()
        assert len(no_text) == 0


# ── 4. Unique language codes ──────────────────────────────────────────

class TestUniqueConstraints:
    def test_duplicate_language_code_rejected(self, session):
        session.add(Language(
            language_code="hi", english_name="Hindi", native_name="हिन्दी",
            writing_system="Devanagari", direction="ltr",
        ))
        session.flush()
        session.add(Language(
            language_code="hi", english_name="Hindi Dup", native_name="हिन्दी",
            writing_system="Devanagari", direction="ltr",
        ))
        with pytest.raises(IntegrityError):
            session.flush()

    def test_duplicate_field_key_in_scheme_rejected(self, session):
        scheme = GovernmentScheme(
            slug="test-scheme", display_name="Test",
            is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        session.add(FormField(
            scheme_id=scheme.id, field_key="name",
            labels_by_language={}, explanations_by_language={},
            instructions_by_language={}, validation_rules={},
        ))
        session.flush()
        session.add(FormField(
            scheme_id=scheme.id, field_key="name",
            labels_by_language={}, explanations_by_language={},
            instructions_by_language={}, validation_rules={},
        ))
        with pytest.raises(IntegrityError):
            session.flush()


# ── 5. Foreign-key constraints ────────────────────────────────────────

class TestForeignKeys:
    def test_form_field_requires_valid_scheme(self, session):
        session.add(FormField(
            scheme_id=99999, field_key="orphan",
            labels_by_language={}, explanations_by_language={},
            instructions_by_language={}, validation_rules={},
        ))
        with pytest.raises(IntegrityError):
            session.flush()

    def test_session_event_requires_valid_session(self, session):
        session.add(SessionEvent(
            session_id="nonexistent-uuid",
            event_type="help_requested",
        ))
        with pytest.raises(IntegrityError):
            session.flush()

    def test_cascade_delete_scheme_removes_fields(self, session):
        scheme = GovernmentScheme(
            slug="del-test", display_name="Delete Test",
            is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        session.add(FormField(
            scheme_id=scheme.id, field_key="f1",
            labels_by_language={}, explanations_by_language={},
            instructions_by_language={}, validation_rules={},
        ))
        session.flush()
        session.delete(scheme)
        session.flush()
        remaining = session.execute(
            select(FormField).where(FormField.field_key == "f1")
        ).scalars().all()
        assert len(remaining) == 0


# ── 6. Idempotent seed ────────────────────────────────────────────────

class TestIdempotentSeed:
    def test_seed_twice_produces_same_counts(self, db_url):
        os.environ["DATABASE_URL"] = db_url
        settings = Settings(database_url=db_url)
        eng = get_engine(settings)
        Base.metadata.create_all(eng)
        factory = get_session_factory(settings)

        seed()
        with factory() as s:
            lang_count_1 = len(s.execute(select(Language)).scalars().all())
            scheme_count_1 = len(s.execute(select(GovernmentScheme)).scalars().all())

        # Re-seed
        reset_engine()
        eng2 = get_engine(Settings(database_url=db_url))
        factory2 = get_session_factory(Settings(database_url=db_url))
        seed()
        with factory2() as s:
            lang_count_2 = len(s.execute(select(Language)).scalars().all())
            scheme_count_2 = len(s.execute(select(GovernmentScheme)).scalars().all())

        assert lang_count_1 == lang_count_2 == 22
        assert scheme_count_1 == scheme_count_2 == 1


# ── 7. Translation-review status vs language availability ─────────────

class TestTranslationReview:
    def test_draft_translations_exist(self, seeded_session):
        drafts = seeded_session.execute(
            select(TranslationReview).where(
                TranslationReview.translation_status == "draft"
            )
        ).scalars().all()
        assert len(drafts) > 0, "Expected some draft translations"

    def test_approved_translations_exist(self, seeded_session):
        approved = seeded_session.execute(
            select(TranslationReview).where(
                TranslationReview.translation_status == "approved"
            )
        ).scalars().all()
        assert len(approved) > 0, "Expected some approved translations"

    def test_draft_language_still_enabled(self, seeded_session):
        """A language can be enabled even if its translations are draft."""
        draft_codes = {
            row[0]
            for row in seeded_session.execute(
                select(TranslationReview.language_code).where(
                    TranslationReview.translation_status == "draft"
                )
            ).all()
        }
        for code in draft_codes:
            lang = seeded_session.execute(
                select(Language).where(Language.language_code == code)
            ).scalar_one_or_none()
            if lang:
                assert lang.enabled is True, (
                    f"Language {code} has draft translations but is disabled"
                )

    def test_review_status_values(self, session):
        """Only draft / reviewed / approved are accepted."""
        tr = TranslationReview(
            resource_type="test", resource_key="k1",
            language_code="hi", translation_status="approved",
        )
        session.add(tr)
        session.flush()  # should succeed

        # Invalid status
        tr_bad = TranslationReview(
            resource_type="test", resource_key="k2",
            language_code="hi", translation_status="invalid_status",
        )
        session.add(tr_bad)
        with pytest.raises(IntegrityError):
            session.flush()


# ── 8. No application-answer fields in analytics records ─────────────

class TestPrivacyColumns:
    """Verify that AssistedSession and SessionEvent have NO columns that
    could hold citizen PII or form answers."""

    PII_COLUMN_NAMES = {
        "name", "first_name", "last_name", "full_name",
        "phone", "phone_number", "mobile",
        "email", "email_address",
        "address", "street", "city", "pin_code", "postal_code",
        "aadhaar", "aadhar", "pan", "voter_id", "passport",
        "bank_account", "ifsc", "upi",
        "password", "secret",
        "answer", "form_answer", "field_value", "user_input",
        "document", "upload", "attachment",
        "voice_recording", "audio",
    }

    def test_assisted_session_has_no_pii_columns(self, engine, tables):
        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("assisted_sessions")}
        overlap = cols & self.PII_COLUMN_NAMES
        assert not overlap, f"PII columns found in assisted_sessions: {overlap}"

    def test_session_event_has_no_pii_columns(self, engine, tables):
        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("session_events")}
        overlap = cols & self.PII_COLUMN_NAMES
        assert not overlap, f"PII columns found in session_events: {overlap}"


# ── 9. Demo-data labelling ───────────────────────────────────────────

class TestDemoLabelling:
    def test_demo_scheme_is_marked(self, seeded_session):
        schemes = seeded_session.execute(select(GovernmentScheme)).scalars().all()
        for s in schemes:
            assert s.is_demo is True

    def test_demo_sessions_are_marked(self, seeded_session):
        sessions = seeded_session.execute(select(AssistedSession)).scalars().all()
        assert len(sessions) > 0
        for s in sessions:
            assert s.is_demo is True, f"Session {s.id} is not marked as demo"

    def test_demo_scheme_description_contains_disclaimer(self, seeded_session):
        scheme = seeded_session.execute(
            select(GovernmentScheme).where(
                GovernmentScheme.slug == "demo-scholarship-application"
            )
        ).scalar_one()
        assert "FICTIONAL" in scheme.description.upper() or "DEMO" in scheme.description.upper()


# ── 10. Check constraints ────────────────────────────────────────────

class TestCheckConstraints:
    def test_invalid_session_status_rejected(self, session):
        scheme = GovernmentScheme(
            slug="ck-test", display_name="CK Test", is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        s = AssistedSession(
            id=str(uuid.uuid4()),
            scheme_id=scheme.id,
            selected_language="hi",
            status="invalid_status",
            analytics_consent=False,
            is_demo=True,
        )
        session.add(s)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_invalid_channel_rejected(self, session):
        scheme = GovernmentScheme(
            slug="ch-test", display_name="CH Test", is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        s = AssistedSession(
            id=str(uuid.uuid4()),
            scheme_id=scheme.id,
            selected_language="hi",
            channel="sms",
            analytics_consent=False,
            is_demo=True,
        )
        session.add(s)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_invalid_event_type_rejected(self, session):
        scheme = GovernmentScheme(
            slug="ev-test", display_name="EV Test", is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        sess_obj = AssistedSession(
            id=str(uuid.uuid4()),
            scheme_id=scheme.id,
            selected_language="hi",
            analytics_consent=True,
            is_demo=True,
        )
        session.add(sess_obj)
        session.flush()
        ev = SessionEvent(
            session_id=sess_obj.id,
            event_type="invalid_event",
        )
        session.add(ev)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_invalid_direction_rejected(self, session):
        session.add(Language(
            language_code="xx", english_name="Test", native_name="Test",
            writing_system="Latin", direction="bidi",
        ))
        with pytest.raises(IntegrityError):
            session.flush()


# ── 11. Additional model tests ────────────────────────────────────────

class TestModelBehavior:
    def test_government_scheme_defaults(self, session):
        scheme = GovernmentScheme(
            slug="defaults-test", display_name="Defaults",
            is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        assert scheme.id is not None
        assert scheme.created_at is not None

    def test_form_field_json_storage(self, session):
        scheme = GovernmentScheme(
            slug="json-test", display_name="JSON Test",
            is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        field = FormField(
            scheme_id=scheme.id,
            field_key="test_field",
            labels_by_language={"hi": "परीक्षा", "bn": "পরীক্ষা"},
            explanations_by_language={"hi": "यह एक परीक्षण है"},
            instructions_by_language={},
            validation_rules={"min_length": 1},
        )
        session.add(field)
        session.flush()
        # Re-fetch and verify JSON round-trips
        fetched = session.execute(
            select(FormField).where(FormField.id == field.id)
        ).scalar_one()
        assert fetched.labels_by_language["hi"] == "परीक्षा"
        assert fetched.labels_by_language["bn"] == "পরীক্ষা"
        assert fetched.validation_rules["min_length"] == 1

    def test_session_uuid_default(self, session):
        scheme = GovernmentScheme(
            slug="uuid-test", display_name="UUID Test",
            is_demo=True, is_active=True,
        )
        session.add(scheme)
        session.flush()
        s = AssistedSession(
            scheme_id=scheme.id,
            selected_language="ta",
            analytics_consent=False,
            is_demo=True,
        )
        session.add(s)
        session.flush()
        # Should be a valid UUID
        parsed = uuid.UUID(s.id)
        assert parsed.version == 4

    def test_localized_labels_use_language_codes_as_keys(self, seeded_session):
        """JSON keys should be stable language codes, not English names."""
        fields = seeded_session.execute(select(FormField)).scalars().all()
        assert len(fields) > 0
        for f in fields:
            for key in f.labels_by_language:
                # Keys must be short codes, not full names
                assert len(key) <= 10, f"Label key '{key}' looks like a name, not a code"
