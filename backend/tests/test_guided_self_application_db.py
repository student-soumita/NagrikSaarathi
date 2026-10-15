"""
NagrikSaarathi — Guided Self-Application Mode: Database Test Suite

Tests:
1. Scheme-to-requirement relationships (eligibility, documents, steps, fields) & cascade deletion.
2. Missing translations detection across all 22 scheduled Indian languages.
3. Source and verification metadata (verification_status, last_verified_at, official URLs).
4. Document requirement conditions (conditional vs always_required, condition_rule logic).
5. Migration from existing schema (Alembic upgrade 0001 -> 0002 and downgrade).
6. Privacy invariants — Zero storage of citizen application answers or PII in analytics.
7. Repeated seeding without duplication (idempotency).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import Settings
from backend.app.database import get_engine, get_session_factory, reset_engine
from backend.app.models import (
    AssistedSession,
    Base,
    FormField,
    GovernmentScheme,
    Language,
    SCHEDULED_LANGUAGES_22,
    SchemeApplicationStep,
    SchemeDocumentRequirement,
    SchemeEligibilityRequirement,
    SessionEvent,
    TranslationReview,
)
from backend.app.seed import seed


# ── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _isolate_engine():
    reset_engine()
    yield
    reset_engine()


@pytest.fixture
def db_url(tmp_path):
    db_file = tmp_path / "guided_self_app_test.db"
    return f"sqlite:///{db_file}"


@pytest.fixture
def db_session(db_url):
    os.environ["DATABASE_URL"] = db_url
    settings = Settings(database_url=db_url)
    engine = get_engine(settings)
    Base.metadata.create_all(engine)
    factory = get_session_factory(settings)
    with factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def seeded_db_session(db_url):
    os.environ["DATABASE_URL"] = db_url
    settings = Settings(database_url=db_url)
    seed()
    factory = get_session_factory(settings)
    with factory() as session:
        yield session


# ── 1. Scheme-to-Requirement Relationships ─────────────────────────────

class TestSchemeRequirementRelationships:
    def test_scheme_has_all_related_collections(self, seeded_db_session: Session):
        scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        assert len(scheme.fields) >= 4
        assert len(scheme.eligibility_requirements) >= 3
        assert len(scheme.document_requirements) >= 4
        assert len(scheme.application_steps) >= 5

        # Verify ordering
        step_numbers = [s.step_number for s in scheme.application_steps]
        assert step_numbers == sorted(step_numbers)

        doc_sort_orders = [d.sort_order for d in scheme.document_requirements]
        assert doc_sort_orders == sorted(doc_sort_orders)

    def test_cascade_delete_cleans_up_all_requirements(self, db_session: Session):
        # Create isolated scheme with child requirements
        scheme = GovernmentScheme(
            slug="temp-scheme-cascade-test",
            display_name="Cascade Test Scheme",
            department_name="Test Department",
            official_source_url="https://example.gov.in",
            verification_status="verified",
        )
        db_session.add(scheme)
        db_session.flush()

        eligibility = SchemeEligibilityRequirement(
            scheme_id=scheme.id,
            criterion_key="income_test",
            criterion_type="annual_income",
            titles_by_language={"en": "Income Test"},
            descriptions_by_language={"en": "Test description"},
        )
        doc = SchemeDocumentRequirement(
            scheme_id=scheme.id,
            document_code="doc_test",
            titles_by_language={"en": "Doc Test"},
            descriptions_by_language={"en": "Test doc description"},
        )
        step = SchemeApplicationStep(
            scheme_id=scheme.id,
            step_number=1,
            step_key="step_test",
            titles_by_language={"en": "Step 1"},
            instructions_by_language={"en": "Do step 1"},
        )
        field = FormField(
            scheme_id=scheme.id,
            field_key="field_test",
            labels_by_language={"en": "Field Test"},
            explanations_by_language={"en": "Field explanation"},
            instructions_by_language={"en": "Field instruction"},
        )
        db_session.add_all([eligibility, doc, step, field])
        db_session.commit()

        # Delete the scheme
        scheme_id = scheme.id
        db_session.delete(scheme)
        db_session.commit()

        # Verify child records were cascade-deleted
        assert db_session.execute(
            select(SchemeEligibilityRequirement).where(SchemeEligibilityRequirement.scheme_id == scheme_id)
        ).scalars().all() == []
        assert db_session.execute(
            select(SchemeDocumentRequirement).where(SchemeDocumentRequirement.scheme_id == scheme_id)
        ).scalars().all() == []
        assert db_session.execute(
            select(SchemeApplicationStep).where(SchemeApplicationStep.scheme_id == scheme_id)
        ).scalars().all() == []
        assert db_session.execute(
            select(FormField).where(FormField.scheme_id == scheme_id)
        ).scalars().all() == []


# ── 2. Missing Translations Detection ──────────────────────────────────

class TestMissingTranslationsDetection:
    def test_scheduled_languages_constant_has_exact_22(self):
        assert len(SCHEDULED_LANGUAGES_22) == 22
        expected_22 = {
            "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok",
            "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
            "sd", "ta", "te", "ur"
        }
        assert set(SCHEDULED_LANGUAGES_22) == expected_22

    def test_missing_languages_method_detects_untranslated_codes(self, db_session: Session):
        scheme = GovernmentScheme(
            slug="partial-translation-scheme",
            display_name="Partial Scheme",
            official_source_url="https://example.gov.in",
            descriptions_by_language={
                "hi": "विवरण",
                "bn": "বিবরণ",
            },
        )
        db_session.add(scheme)
        db_session.flush()

        # Target check: hi and bn are present, others are detected as missing
        assert "hi" not in scheme.missing_languages(["hi", "bn"])
        missing_subset = scheme.missing_languages(["hi", "bn", "ta", "te"])
        assert set(missing_subset) == {"ta", "te"}

        # Across all 22 scheduled languages:
        missing_all = scheme.missing_languages(SCHEDULED_LANGUAGES_22)
        assert len(missing_all) == 20
        assert "hi" not in missing_all
        assert "bn" not in missing_all
        assert "ta" in missing_all

    def test_field_and_requirement_missing_translations_detected(self, db_session: Session):
        field = FormField(
            scheme_id=1,
            field_key="test_field",
            labels_by_language={"hi": "लेबल"},
            explanations_by_language={"hi": "विवरण"},
            instructions_by_language={},
        )
        # hi is present; ta is missing
        assert "hi" not in field.missing_languages(["hi"])
        assert "ta" in field.missing_languages(["hi", "ta"])

        req = SchemeEligibilityRequirement(
            scheme_id=1,
            criterion_key="test_crit",
            titles_by_language={"bn": "শিরোনাম"},
            descriptions_by_language={"bn": "বিবরণ"},
        )
        assert "bn" not in req.missing_languages(["bn"])
        assert "ur" in req.missing_languages(["bn", "ur"])


# ── 3. Source and Verification Metadata ─────────────────────────────────

class TestSourceAndVerificationMetadata:
    def test_scheme_and_requirements_store_verification_metadata(self, seeded_db_session: Session):
        scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        assert scheme.official_application_url is not None
        assert scheme.last_verified_at is not None
        assert scheme.verification_status in ("verified", "pending_review", "outdated")
        assert scheme.verification_source_reference is not None

        # Check eligibility requirements have verification metadata
        for el in scheme.eligibility_requirements:
            assert el.verification_status in ("verified", "pending_review", "outdated")
            assert el.last_verified_at is not None
            assert el.official_source_reference is not None

        # Check document requirements have verification metadata
        for doc in scheme.document_requirements:
            assert doc.verification_status in ("verified", "pending_review", "outdated")
            assert doc.last_verified_at is not None
            assert doc.source_reference is not None
            assert doc.issuing_authority is not None

    def test_invalid_verification_status_check_constraint(self, db_session: Session):
        scheme = GovernmentScheme(
            slug="invalid-verification-scheme",
            display_name="Invalid Status Scheme",
            official_source_url="https://example.gov.in",
            verification_status="invalid_status_value",  # Fails CheckConstraint
        )
        db_session.add(scheme)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_synthetic_demonstration_schemes_are_clearly_flagged(self, seeded_db_session: Session):
        demo_scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        assert demo_scheme.is_demo is True
        assert "Demo" in demo_scheme.description or "Synthetic" in demo_scheme.verification_source_reference


# ── 4. Document Requirement Conditions ─────────────────────────────────

class TestDocumentRequirementConditions:
    def test_conditional_and_always_required_documents(self, seeded_db_session: Session):
        scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        docs_by_code = {d.document_code: d for d in scheme.document_requirements}

        # Income certificate is unconditionally required
        income_doc = docs_by_code["income_certificate"]
        assert income_doc.requirement_type == "always_required"
        assert income_doc.is_mandatory is True
        assert income_doc.is_conditional is False
        assert income_doc.condition_rule is None

        # Caste certificate is conditional
        caste_doc = docs_by_code["caste_category_certificate"]
        assert caste_doc.requirement_type == "conditional"
        assert caste_doc.is_conditional is True
        assert caste_doc.condition_rule is not None
        assert "trigger_field" in caste_doc.condition_rule
        assert caste_doc.condition_rule["trigger_field"] == "social_category"

    def test_evaluating_document_condition_rule(self, seeded_db_session: Session):
        scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        caste_doc = next(d for d in scheme.document_requirements if d.document_code == "caste_category_certificate")
        rule = caste_doc.condition_rule

        # Scenario A: Citizen belongs to "General" -> Document is NOT required
        citizen_category_general = "General"
        is_required_for_general = citizen_category_general in rule["values"]
        assert is_required_for_general is False

        # Scenario B: Citizen belongs to "OBC" -> Document IS required
        citizen_category_obc = "OBC"
        is_required_for_obc = citizen_category_obc in rule["values"]
        assert is_required_for_obc is True


# ── 5. Migration from Existing Schema ──────────────────────────────────

class TestAlembicMigrationFromExistingSchema:
    def test_alembic_upgrade_and_downgrade_0001_to_0002(self, tmp_path):
        import os
        from alembic import command
        from alembic.config import Config

        mig_db_path = tmp_path / "alembic_guided_migration_test.db"
        mig_db_url = f"sqlite:///{mig_db_path}"
        os.environ["DATABASE_URL"] = mig_db_url

        alembic_ini_path = "backend/alembic.ini" if os.path.exists("backend/alembic.ini") else "alembic.ini"
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", mig_db_url)

        # 1. Upgrade to 0001_initial_schema
        command.upgrade(alembic_cfg, "0001_initial_schema")
        mig_eng = create_engine(mig_db_url)
        insp_0001 = inspect(mig_eng)
        tables_0001 = set(insp_0001.get_table_names())
        assert "scheme_eligibility_requirements" not in tables_0001
        assert "scheme_document_requirements" not in tables_0001
        assert "scheme_application_steps" not in tables_0001

        # 2. Upgrade to 0002_guided_self_application (head)
        command.upgrade(alembic_cfg, "head")
        insp_0002 = inspect(mig_eng)
        tables_0002 = set(insp_0002.get_table_names())
        assert {
            "scheme_eligibility_requirements",
            "scheme_document_requirements",
            "scheme_application_steps",
        }.issubset(tables_0002)

        # Verify added columns in government_schemes and form_fields
        scheme_cols = {c["name"] for c in insp_0002.get_columns("government_schemes")}
        assert "official_application_url" in scheme_cols
        assert "verification_status" in scheme_cols
        assert "last_verified_at" in scheme_cols

        field_cols = {c["name"] for c in insp_0002.get_columns("form_fields")}
        assert "examples_by_language" in field_cols
        assert "validation_guidance_by_language" in field_cols
        assert "verification_status" in field_cols

        # 3. Downgrade to 0001_initial_schema
        command.downgrade(alembic_cfg, "0001_initial_schema")
        insp_downgrade = inspect(mig_eng)
        tables_down = set(insp_downgrade.get_table_names())
        assert "scheme_eligibility_requirements" not in tables_down
        assert "scheme_document_requirements" not in tables_down
        assert "scheme_application_steps" not in tables_down

        # 4. Downgrade back to base
        command.downgrade(alembic_cfg, "base")
        insp_base = inspect(mig_eng)
        base_tables = set(insp_base.get_table_names())
        assert "languages" not in base_tables
        assert "government_schemes" not in base_tables
        assert "scheme_eligibility_requirements" not in base_tables
        assert "scheme_document_requirements" not in base_tables
        assert "scheme_application_steps" not in base_tables
        assert "users" not in base_tables

        mig_eng.dispose()


# ── 6. Privacy & Zero Citizen Answer Storage ───────────────────────────

class TestPrivacyAndZeroAnswerStorage:
    def test_assisted_sessions_and_session_events_have_no_answer_columns(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        inspector = inspect(engine)

        forbidden_tokens = {
            "answer", "value", "response", "input_data", "payload",
            "name", "aadhaar", "bank", "account_number", "mobile",
            "phone", "email", "password", "document_content", "file_data"
        }

        for table_name in ("assisted_sessions", "session_events"):
            columns = inspector.get_columns(table_name)
            col_names = {c["name"].lower() for c in columns}
            for col in col_names:
                for token in forbidden_tokens:
                    assert token not in col, (
                        f"Privacy violation: table '{table_name}' contains sensitive/answer column '{col}'"
                    )

    def test_guided_self_application_works_without_user_account(self, seeded_db_session: Session):
        # A citizen guidance session can be created completely anonymously
        scheme = seeded_db_session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one()

        anon_session = AssistedSession(
            id=str(uuid.uuid4()),
            scheme_id=scheme.id,
            selected_language="bn",
            channel="web",
            status="in_progress",
            analytics_consent=False,
            is_demo=False,
        )
        seeded_db_session.add(anon_session)
        seeded_db_session.commit()

        retrieved = seeded_db_session.get(AssistedSession, anon_session.id)
        assert retrieved is not None
        assert retrieved.selected_language == "bn"


# ── 7. Repeated Seeding Idempotency ────────────────────────────────────

class TestIdempotentSeeding:
    def test_seed_twice_produces_identical_counts(self, db_url):
        os.environ["DATABASE_URL"] = db_url
        settings = Settings(database_url=db_url)
        engine = get_engine(settings)
        Base.metadata.create_all(engine)
        factory = get_session_factory(settings)

        # First run
        seed()
        with factory() as s:
            lang_1 = len(s.execute(select(Language)).scalars().all())
            scheme_1 = len(s.execute(select(GovernmentScheme)).scalars().all())
            field_1 = len(s.execute(select(FormField)).scalars().all())
            elig_1 = len(s.execute(select(SchemeEligibilityRequirement)).scalars().all())
            doc_1 = len(s.execute(select(SchemeDocumentRequirement)).scalars().all())
            step_1 = len(s.execute(select(SchemeApplicationStep)).scalars().all())
            rev_1 = len(s.execute(select(TranslationReview)).scalars().all())

        # Second run
        reset_engine()
        seed()
        with factory() as s:
            lang_2 = len(s.execute(select(Language)).scalars().all())
            scheme_2 = len(s.execute(select(GovernmentScheme)).scalars().all())
            field_2 = len(s.execute(select(FormField)).scalars().all())
            elig_2 = len(s.execute(select(SchemeEligibilityRequirement)).scalars().all())
            doc_2 = len(s.execute(select(SchemeDocumentRequirement)).scalars().all())
            step_2 = len(s.execute(select(SchemeApplicationStep)).scalars().all())
            rev_2 = len(s.execute(select(TranslationReview)).scalars().all())

        assert lang_1 == lang_2 == 22
        assert scheme_1 == scheme_2
        assert field_1 == field_2
        assert elig_1 == elig_2
        assert doc_1 == doc_2
        assert step_1 == step_2
        assert rev_1 == rev_2
