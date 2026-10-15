# NagrikSaarathi (नागरिक सारथी) — Backend

Production-conscious FastAPI backend for NagrikSaarathi, a multilingual government-service application assistance platform supporting all 22 official Indian languages.

---

## 1. Architectural Overview

NagrikSaarathi operates as a modular citizen-guidance engine with strict anonymity:

- **Framework**: FastAPI with asynchronous endpoints.
- **ORM**: SQLAlchemy 2.x declarative models with PostgreSQL / SQLite compatibility.
- **Data Schemas**: Pydantic v2 schemas validating request sizes and data integrity.
- **3-Layer Language Architecture**:
  - **Layer A (Stored Guidance)**: Pre-verified translations stored in database tables with human-review metadata.
  - **Layer B (Provider Adapter)**: Dynamic adapter for external language providers (e.g. BHASHINI) with strict timeouts and error isolation.
  - **Layer C (Safe Fallback)**: Transparent missing-content identification directing citizens to human assistance desks without masquerading English as the target language.
- **Privacy & Consent Boundary**:
  - Ephemeral client-side form completion by default.
  - Zero citizen form answers, PII, documents, or raw voice recordings stored on server.
  - Analytics events rejected unless explicit citizen consent (`analytics_consent = true`) was granted.
  - Complete separation between synthetic demonstration records (`is_demo = true`) and real observations.

---

## 2. Supported Indian Languages (Eighth Schedule)

The platform supports all 22 Eighth Schedule Indian languages:

| Language | Code | Native Name | Script Direction | Text Support | Voice Support (Actual) |
|---|---|---|---|---|---|
| Assamese | `as` | অসমীয়া | LTR | Yes | No |
| Bengali | `bn` | বাংলা | LTR | Yes | Yes |
| Bodo | `brx` | बड़ो | LTR | Yes | No |
| Dogri | `doi` | डोगरी | LTR | Yes | No |
| Gujarati | `gu` | ગુજરાતી | LTR | Yes | Yes |
| Hindi | `hi` | हिन्दी | LTR | Yes | Yes |
| Kannada | `kn` | ಕನ್ನಡ | LTR | Yes | Yes |
| Kashmiri | `ks` | कॉशुर / كٲشُر | RTL | Yes | No |
| Konkani | `kok` | कोंकणी | LTR | Yes | No |
| Maithili | `mai` | मैथिली | LTR | Yes | No |
| Malayalam | `ml` | മലയാളം | LTR | Yes | Yes |
| Manipuri | `mni` | মৈতৈলোন্ | LTR | Yes | No |
| Marathi | `mr` | मराठी | LTR | Yes | Yes |
| Nepali | `ne` | नेपाली | LTR | Yes | Yes |
| Odia | `or` | ଓଡ଼ିଆ | LTR | Yes | No |
| Punjabi | `pa` | ਪੰਜਾਬੀ | LTR | Yes | Yes |
| Sanskrit | `sa` | संस्कृतम् | LTR | Yes | No |
| Santali | `sat` | ᱥᱟᱱᱛᱟᱲᱤ | LTR | Yes | No |
| Sindhi | `sd` | سنڌي / सिन्धी | RTL | Yes | No |
| Tamil | `ta` | தமிழ் | LTR | Yes | Yes |
| Telugu | `te` | తెలుగు | LTR | Yes | Yes |
| Urdu | `ur` | اردو | RTL | Yes | Yes |

*Note: Voice capabilities reflect validated provider model availability. Text interface support is enabled across all 22 languages.*

---

## 3. API Endpoints

### System & Reference
- `GET /api/health` — System and database health check
- `GET /api/languages` — List 22 Indian languages with capability flags
- `GET /api/languages/{language_code}` — Specific language metadata
- `GET /api/schemes` — List available government schemes
- `GET /api/schemes/{scheme_id}` — Scheme detail with form fields
- `GET /api/schemes/{scheme_id}/fields` — Ordered form fields

### Citizen Assistance Sessions
- `POST /api/sessions` — Start assistance session (persisted only if `analytics_consent=true`)
- `POST /api/sessions/{session_id}/events` — Record anonymous lifecycle event (consent required)
- `PATCH /api/sessions/{session_id}/status` — Update session status (`in_progress`, `completed`, `abandoned`, `needs_human_help`)

### Multilingual Guidance
- `POST /api/assist/explain` — Localized field guidance with translation review status
- `POST /api/assist/validate` — Safe deterministic rule validation (never invents rules)

### Dashboard Analytics (Protected in production)
- `GET /api/dashboard/summary` — Consented session volume and completion rates
- `GET /api/dashboard/barriers` — Frequency distribution of identified barrier categories
- `GET /api/dashboard/languages` — Language-wise session and barrier distribution
- `GET /api/dashboard/fields` — Form fields with highest barrier incidence
- `GET /api/dashboard/recovery` — Guidance issue resolution and recovery rate
- `GET /api/dashboard/translation-quality` — Localization coverage and review audit

### Speech Services
- `POST /api/voice/transcribe` — Ephemeral speech-to-text with capability check
- `POST /api/voice/speak` — Ephemeral text-to-speech with capability check

---

## 4. Windows PowerShell Quick Start

Run the following commands in Windows PowerShell from the repository root:

```powershell
# 1. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install backend dependencies
.\.venv\Scripts\pip.exe install -r backend/requirements.txt

# 3. Apply database migrations
.\.venv\Scripts\alembic.exe -c backend/alembic.ini upgrade head

# 4. Seed initial data (22 languages, demo scheme, synthetic sessions)
.\.venv\Scripts\python.exe -m backend.app.seed

# 5. Start the development server
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 6. Run the test suite
.\.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

Interactive API documentation will be available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
