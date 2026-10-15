# 🇮🇳 NagrikSaarathi

### Making Government Schemes Easier to Discover, Understand & Access

**A citizen-first civic technology platform that aims to bridge the gap between government schemes and the people who need them.**

[![Civic Tech](https://img.shields.io/badge/Domain-Civic%20Tech-0F766E?style=for-the-badge)](https://github.com/student-soumita/NagrikSaarathi)
[![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Under%20Development-E7A93B?style=for-the-badge)](https://github.com/student-soumita/NagrikSaarathi)

**Discover. Understand. Prepare. Access.**

[Explore Repository](https://github.com/student-soumita/NagrikSaarathi) · [Report a Bug](https://github.com/student-soumita/NagrikSaarathi/issues)

---

## 🌱 The Idea Behind NagrikSaarathi

Imagine being eligible for a government scheme but not knowing it exists. Or finding the scheme, only to struggle with complicated eligibility rules, unfamiliar terminology, missing documents, or a language barrier.

For many citizens, understanding and accessing public benefits can be unnecessarily difficult.

**NagrikSaarathi aims to change that experience.**

It brings together government scheme discovery, understandable guidance, application preparation, and administrative information management in one accessible digital platform.

> 🎯 **Our mission: Make government scheme information easier to find, easier to understand, and easier to act upon.**

## 🚩 The Problem We Address

- 🔎 **Scattered information:** Citizens may need to visit multiple websites to find relevant schemes.
- 🌐 **Language barriers:** Important instructions may not be understandable in a citizen's preferred language.
- 📄 **Complex requirements:** Eligibility rules and document requirements can be confusing.
- 🧭 **Lack of guidance:** Finding a scheme does not automatically explain how to prepare an application.
- 🔗 **Unreliable information:** Incorrect or outdated links can prevent citizens from reaching the right portal.
- 🏢 **Administrative challenges:** Keeping scheme details, translations, and official links accurate requires continuous effort.

## ✨ Features

### 👥 Citizen Workspace

Helping citizens navigate government schemes with greater confidence.

- **🔍 Scheme Discovery** — Explore schemes by category, government level, location, and beneficiary group, subject to available catalogue data.
- **🎁 Benefits at a Glance** — Understand scheme benefits, conditions, intended beneficiaries, and available assistance.
- **🧭 Guided Form Assistance** — Break complex form questions into simpler, understandable steps.
- **🌏 Multilingual Accessibility** — Build toward accessible guidance across India's 22 scheduled languages.
- **📋 Application Readiness Passport** — Track required documents, missing information, and preparation progress.
- **📨 Missing Scheme Requests** — Report schemes that are not listed and follow their review status.
- **🆘 Help & Support** — Report difficulties and track support requests.
- **♿ Accessibility Controls** — Adjust contrast and font size for a more comfortable experience.

### 🏢 Department Official Workspace

Giving authorised officials useful tools to maintain reliable scheme information.

- **📝 Department Workbench** — Manage assigned scheme proposals and corrections.
- **🔎 Scheme Rule Change Radar** — Compare revised guidelines with existing scheme information.
- **📚 Evidence-Linked Verification** — Associate important scheme claims with supporting official sources.
- **📊 Citizen Difficulty Heatmap** — Identify recurring form errors and confusing instructions using aggregated data.
- **🌐 Translation Drift Monitor** — Identify translations that may need review when source information changes.
- **✅ Review Workflow** — Track proposals, revision requests, approvals, and publication status.
- **🛡️ Restricted Access** — Keep department operations separate from citizen-facing functionality.

### 🛡️ Principal Administrator Workspace

Providing central oversight and control over the platform.

- Review and approve scheme proposals.
- Manage authorised Department Official accounts and department assignments.
- Review missing-scheme requests and support escalations.
- Monitor scheme catalogue coverage and official-link verification.
- Track translation quality and missing information.
- Review audit logs and important administrative actions.

*Feature descriptions include planned capabilities. Refer to the project's current implementation and roadmap for actual availability.*

---

## 💡 What Makes NagrikSaarathi Different?

NagrikSaarathi aims to go beyond listing schemes by connecting citizen assistance with the processes required to keep information accurate and useful.

| Traditional approach | NagrikSaarathi's direction |
|---|---|
| Find a scheme and figure out the rest | Understand benefits, requirements, and next steps |
| Struggle with unfamiliar form questions | Receive contextual, step-by-step guidance |
| Have no clear visibility into a missing-scheme report | Track requests and review decisions |
| Update information without visible comparison | Compare proposed changes against published rules |
| Translate content without monitoring freshness | Identify translations that may need revision |
| Investigate form difficulties individually | Use privacy-conscious aggregated analytics to identify recurring problems |

## ⭐ Signature Feature: Scheme Rule Change Radar

Government scheme details can change over time. Outdated eligibility rules, benefit amounts, document requirements, or application links can mislead citizens.

The proposed **Scheme Rule Change Radar** compares newly supplied official guidelines with existing scheme records and highlights potential changes to:

- Eligibility criteria and exclusions
- Benefits and assistance amounts
- Required documents
- Deadlines and application procedures
- Official scheme and application links

Each proposed change should retain its source evidence and remain unpublished until the required review and approval process is complete.

**The goal is not just to display information, but to help keep that information trustworthy.**

---

## 🔄 How It Works

1. **Discover** — Find potentially relevant government schemes.
2. **Understand** — Explore benefits, eligibility, and requirements in accessible language.
3. **Prepare** — Follow guidance and organise the information and documents needed.
4. **Take the Next Step** — Visit a verified official destination where available.
5. **Improve** — Help authorised officials review scheme information and address recurring difficulties.

*The platform guides and prepares citizens. Final eligibility decisions and application outcomes remain with the responsible authorities.*

---

## 🏗️ Application Architecture

NagrikSaarathi is organised into a modular web application.

```text
NagrikSaarathi/
│
├── frontend/        # Web application interface
├── backend/         # Python backend and application logic
├── database/        # Database-related resources
├── tests/           # Automated tests
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Three Separate Workspaces

```text
                    NAGRIKSAARATHI
                           |
          +----------------+----------------+
          |                |                |
       CITIZEN          DEPARTMENT       PRINCIPAL
       WORKSPACE         OFFICIAL       ADMINISTRATOR
                          WORKSPACE       WORKSPACE
          |                |                |
       Discover         Propose &        Review &
       Understand       Maintain         Approve
       Prepare          Scheme Data      & Govern
          |                |                |
          +----------------+----------------+
                           |
                  Shared Design System
                   & Protected Backend
```

Each role has separate responsibilities and permissions while sharing a consistent visual design.

Department Official access is intended for authorised accounts, not unrestricted public registration. Access restrictions must be enforced by the backend, not merely by hiding interface elements.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python |
| Database | SQLite resources and existing database configuration |
| Frontend | Web application in `frontend/` |
| Dependencies | `requirements.txt` and project configuration |
| Testing | Project test suite in `tests/` |

Refer to the actual project configuration for the frontend framework, application entry points, and installed dependency versions.

---

## 🚀 Getting Started

### Prerequisites

- Git
- Python compatible with the project's dependencies
- Node.js and npm, if required by the frontend

### 1. Clone the Repository

```bash
git clone https://github.com/student-soumita/NagrikSaarathi.git
cd NagrikSaarathi
```

### 2. Set Up the Python Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Inspect Frontend Commands

```powershell
cd frontend
npm install
npm run
```

Use the development command listed in the frontend's configured scripts. Start the backend using its actual application entry point and configuration.

### 4. Configure the Application

Before running the complete application:

- Review required environment variables.
- Configure external services where applicable.
- Initialise or migrate the database using the project's supported process.
- Check the project's setup instructions for any additional requirements.

**Security note:** Never commit API keys, passwords, private credentials, or databases containing sensitive personal information.

---

## 🗺️ Development Roadmap

NagrikSaarathi is under active development.

- [ ] Expand and verify nationwide scheme coverage.
- [ ] Correct scheme details and application portal links.
- [ ] Complete translation coverage and quality checks across 22 languages.
- [ ] Improve language-specific audio guidance.
- [ ] Complete guided-form help and issue-resolution workflows.
- [ ] Implement reliable scheme request and support-ticket tracking.
- [ ] Complete secure, department-scoped official access.
- [ ] Implement the Scheme Rule Change Radar.
- [ ] Implement the Citizen Difficulty Heatmap.
- [ ] Strengthen evidence-linked scheme verification.
- [ ] Complete translation drift monitoring.
- [ ] Verify global contrast and font-size settings.
- [ ] Expand end-to-end security and workflow testing.

---

## 🔐 Trust, Privacy & Accuracy

Government-related information must be handled responsibly.

- **Official sources first:** Important scheme claims should link to authoritative sources.
- **No false guarantees:** Potential eligibility is not a promise of approval.
- **Transparent verification:** Missing or uncertain information should be labelled clearly.
- **Privacy-conscious design:** Collect only necessary information and protect citizen records.
- **Secure administration:** Enforce permissions for official accounts and protected operations.
- **Controlled updates:** Important scheme changes should follow an auditable approval process.
- **Honest limitations:** Unavailable translations, audio voices, or integrations should be reported clearly.

## 🤝 Contributing

Ideas, feedback, bug reports, and contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement a focused improvement.
4. Test the change.
5. Submit a pull request with a clear description.

For scheme-related corrections, include the relevant official source whenever possible.

## ⚠️ Disclaimer

NagrikSaarathi is an independently developed project and is **not an official Government of India website**. It does not represent any government department or guarantee scheme eligibility, application acceptance, or benefit approval.

Users should consult the responsible government's official sources for current requirements and final decisions.

---

## 🌱 Our Vision

**A world where understanding government support is not a privilege, but an accessible opportunity for everyone.**

*One platform. Clearer guidance. More accessible public services.* 🇮🇳

[**Explore NagrikSaarathi on GitHub →**](https://github.com/student-soumita/NagrikSaarathi)
