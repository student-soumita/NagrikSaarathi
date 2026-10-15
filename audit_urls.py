import json
from backend.app.database import get_session_factory
from backend.app.models import GovernmentScheme
from sqlalchemy import select

db = get_session_factory()()
schemes = db.execute(select(GovernmentScheme).order_by(GovernmentScheme.id)).scalars().all()
data = []
for s in schemes:
    item = {
        'id': s.id,
        'slug': s.slug,
        'display_name': s.display_name,
        'state_code': s.state_code,
        'government_level': s.government_level,
        'official_source_url': s.official_source_url,
        'official_application_url': s.official_application_url,
        'source_document_reference': s.source_document_reference,
        'verification_source_reference': s.verification_source_reference
    }
    data.append(item)
    state = s.state_code if s.state_code else 'CENTRAL'
    print(f"{s.id:2d} | {s.slug[:26]:26s} | {state:7s} | src: {s.official_source_url} | app: {s.official_application_url}")

with open('audit_scheme_urls.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
