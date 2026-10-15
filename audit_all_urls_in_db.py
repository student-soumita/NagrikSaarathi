import json
from backend.app.database import get_session_factory
from backend.app.models import (
    GovernmentScheme,
    SchemeDocumentRequirement,
    SchemeApplicationStep,
    IngestionAuditLog
)
from sqlalchemy import select

db = get_session_factory()()

schemes = db.execute(select(GovernmentScheme)).scalars().all()
print(f"=== GOVERNMENT SCHEMES ({len(schemes)}) ===")
schemes_data = []
for s in schemes:
    schemes_data.append({
        "id": s.id,
        "slug": s.slug,
        "display_name": s.display_name,
        "state_code": s.state_code,
        "official_source_url": s.official_source_url,
        "official_application_url": s.official_application_url,
        "source_document_reference": s.source_document_reference,
        "verification_source_reference": s.verification_source_reference,
        "is_candidate": s.is_candidate,
        "is_demo": s.is_demo,
    })

doc_reqs = db.execute(select(SchemeDocumentRequirement)).scalars().all()
print(f"=== SCHEME DOCUMENT REQUIREMENTS ({len(doc_reqs)}) ===")
docs_with_url = [
    {"id": d.id, "scheme_id": d.scheme_id, "document_code": d.document_code, "url": d.official_source_url}
    for d in doc_reqs if d.official_source_url
]
print(f"Doc reqs with official_source_url: {len(docs_with_url)}")

steps = db.execute(select(SchemeApplicationStep)).scalars().all()
print(f"=== SCHEME APPLICATION STEPS ({len(steps)}) ===")
steps_with_url = [
    {"id": st.id, "scheme_id": st.scheme_id, "step_key": st.step_key, "url": st.official_action_url}
    for st in steps if st.official_action_url
]
print(f"Steps with official_action_url: {len(steps_with_url)}")

with open("full_db_urls.json", "w", encoding="utf-8") as f:
    json.dump({
        "schemes": schemes_data,
        "doc_requirements": docs_with_url,
        "steps": steps_with_url
    }, f, indent=2, ensure_ascii=False)

print("Saved to full_db_urls.json")
