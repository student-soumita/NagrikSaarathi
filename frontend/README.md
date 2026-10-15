# NagrikSaarathi (नागरिक सारथी) — Frontend

A refined, accessible public-service web application built with React, Vite, and the **Civic Editorial** design system.

---

## 1. Design Identity: Civic Editorial

The user interface avoids generic SaaS templates and artificial intelligence clichés (no purple gradients, neon glows, glassmorphism, or floating orbs). Instead, it embodies trustworthy public-service editorial typography:

- **Deep Navy** (`#102A43`): Primary text and structural headers.
- **Warm Ivory** (`#F8F5EF`): Canvas background and warm reading surface.
- **Teal** (`#0F766E`): Primary actions, verified badges, and interactive focus states.
- **Saffron Accent** (`#E7A93B`): Prototype badges and escalation buttons.
- **Restrained Red** (`#BA2525`): Real validation errors and missing requirements.

---

## 2. All 22 Eighth Schedule Indian Languages

Full native-script support and layout direction handling (LTR and RTL for Urdu, Kashmiri, Sindhi):

1. **Assamese** (`as` — অসমীয়া)
2. **Bengali** (`bn` — বাংলা)
3. **Bodo** (`brx` — बड़ो)
4. **Dogri** (`doi` — डोगरी)
5. **Gujarati** (`gu` — ગુજરાતી)
6. **Hindi** (`hi` — हिन्दी)
7. **Kannada** (`kn` — ಕನ್ನಡ)
8. **Kashmiri** (`ks` — कॉशुर / كٲشُر)
9. **Konkani** (`kok` — कोंकणी)
10. **Maithili** (`mai` — मैथिली)
11. **Malayalam** (`ml` — മലയാളം)
12. **Manipuri/Meitei** (`mni` — মৈতৈলোন্)
13. **Marathi** (`mr` — मराठी)
14. **Nepali** (`ne` — नेपाली)
15. **Odia** (`or` — ଓଡ଼ିଆ)
16. **Punjabi** (`pa` — ਪੰਜਾਬੀ)
17. **Sanskrit** (`sa` — संस्कृतम्)
18. **Santali** (`sat` — ᱥᱟᱱᱛᱟᱲᱤ)
19. **Sindhi** (`sd` — سنڌي / सिन्धी)
20. **Tamil** (`ta` — தமிழ்)
21. **Telugu** (`te` — తెలుగు)
22. **Urdu** (`ur` — اردو)

---

## 3. Features & Architecture

- **Immediate Language Selector**: Citizens can pick their preferred language *before* starting any form.
- **Guided Form Workflow**:
  - Scheme selection (`Demo Scholarship Application`).
  - Document instruction overview.
  - Step-by-step field guidance with Layer A stored explanations.
  - Deterministic field validation without inventing government rules.
  - Barrier resolution modal with human desk escalation.
  - Ephemeral voice-assisted speech recognition and text-to-speech.
  - Review screen with in-memory state preservation and clearing.
- **Strict Privacy & Consent**:
  - Two explicit choices: "Allow anonymous analytics" or "Continue without analytics".
  - Assistance works identically if consent is declined.
  - Zero PII or form answers are ever sent to analytics tables.
- **Department Dashboard (`/dashboard`)**:
  - Live analytics from backend endpoints.
  - Completion & abandonment rates with mathematically explicit formulas.
  - Problematic field and barrier breakdowns.
  - 22-language translation coverage audit.
  - Admin API Key authentication gate for inspecting real production data.

---

## 4. Windows PowerShell Quick Start

Run these commands from the repository root (`c:\Users\chatt\OneDrive\Desktop\NagrikSaarathi`):

```powershell
# 1. Start the backend server (Terminal 1)
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start the frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

The frontend application will be live at:
`http://localhost:5173`

---

## 5. Running Tests

Run the language completeness test suite to verify that all 22 locale JSON files exist, have 100% of required keys, and contain zero raw placeholders:

```powershell
cd frontend
npm test
```

---

## 6. Building for Production

```powershell
cd frontend
npm run build
```
