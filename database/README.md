# NagrikSaarathi — Database README

## Overview

This directory contains the **reference SQL schema** and **ERD documentation**
for the NagrikSaarathi (नागरिक सारथी) database layer.

> **Canonical schema lives in Python.** The SQLAlchemy ORM models in
> [`backend/app/models.py`](../backend/app/models.py) are the single source
> of truth. The SQL file here is a read-only reference.

## Files

| File | Purpose |
|---|---|
| `schema.sql` | Read-only SQL reference of the current schema |
| `ERD.md` | Entity-Relationship Diagram (Mermaid) with full Guided Self-Application structure |

## Guided Self-Application Mode Capabilities

The database layer supports privacy-first, multilingual Guided Self-Application:

1. **Structured Eligibility Rules (`scheme_eligibility_requirements`)**:
   - Stores typed criteria (`annual_income`, `academic_qualification`, `age`, `institutional_enrollment`, etc.).
   - Captures operators (`lte`, `gte`, `eq`, `in`) and structured threshold values (e.g. `{"max_income_inr": 250000}`).
   - Localized rule summaries and explanations across all 22 Eighth Schedule Indian languages.
   - Verification metadata (`verification_status` in `'verified'`, `'pending_review'`, `'outdated'`).

2. **Required & Conditional Documents (`scheme_document_requirements`)**:
   - Classifies documents into `'always_required'`, `'conditional'`, or `'optional'`.
   - Stores structured conditions in JSON (e.g. caste certificate required only when applying under reserved categories).
   - Records issuing authority, validity period, official reference links, and verification dates.

3. **Step-by-Step Guidance (`scheme_application_steps`)**:
   - Ordered procedural steps with localized instructions and direct official URLs for actions like One-Time Registration (OTR).

4. **Scheme & Field Verification Metadata**:
   - `GovernmentScheme` stores `official_application_url`, `last_verified_at`, `verification_status`, and localized descriptions.
   - `FormField` stores `examples_by_language`, `validation_guidance_by_language`, and `verification_status`.

## Quick Start (Windows PowerShell)

```powershell
# From the project root:

# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run migrations
.\.venv\Scripts\alembic.exe -c backend/alembic.ini upgrade head

# 3. Create tables and seed data
python -m backend.app.seed

# 4. Run tests
pytest backend/ -v

# 5. Run with --reset to drop and recreate
python -m backend.app.seed --reset
```

## Privacy Design

The database is designed with strict privacy invariants:

- **No PII storage**: `assisted_sessions` and `session_events` tables
  contain zero columns for citizen names, phone numbers, addresses,
  identity numbers, bank details, passwords, form answers, uploaded
  documents, or voice recordings.
- **Client-Side Self-Application Memory**: Guided self-application runs
  without requiring user account registration, and application answers remain
  strictly in browser client-side memory.
- **Consent-gated analytics**: Sessions are only created with analytics
  events after explicit `analytics_consent = true`.
- **Demo isolation**: All seed data uses `is_demo = true` and can never
  be confused with real government data.
- **Parameterised queries**: All database operations use SQLAlchemy ORM
  with parameterised bindings.

## Languages

All 22 languages from the Eighth Schedule of the Indian Constitution are
supported and enabled for the text interface. Speech capabilities
(`supports_speech_recognition`, `supports_text_to_speech`) are set only
where validated cloud-provider support exists.

## Disclaimer

The "Demo Scholarship Application" seed scheme is **entirely fictional**
and does not represent any real government programme. Simulated analytics
sessions and events are synthetic test data and must never be cited as
actual public-sector statistics.
