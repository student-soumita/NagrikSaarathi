import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# 1. Test coverage audit
audit_resp = client.get("/api/schemes/coverage-audit")
assert audit_resp.status_code == 200, f"Expected 200, got {audit_resp.status_code}: {audit_resp.text}"
audit_data = audit_resp.json()
print("Total schemes in audit:", audit_data["total_schemes"])
print("Fully supported schemes:", audit_data["fully_supported_schemes"])
print("Unsupported schemes:", audit_data["unsupported_schemes"])
print("Coverage percentage:", audit_data["coverage_percentage"], "%")
assert audit_data["coverage_percentage"] == 100.0, "Coverage percentage must be 100%"

# 2. Test schemes list (with candidates)
schemes_resp = client.get("/api/schemes/?include_candidates=true")
assert schemes_resp.status_code == 200
schemes = schemes_resp.json()
print(f"Loaded {len(schemes)} schemes from catalogue (including candidates)")
assert len(schemes) == 67

# 3. Test guidance and form fields across a diverse set of schemes
sample_ids = [schemes[0]["id"], schemes[10]["id"], schemes[25]["id"], schemes[40]["id"], schemes[-1]["id"]]
for sid in sample_ids:
    guidance_resp = client.get(f"/api/schemes/{sid}/guidance?language=hi")
    assert guidance_resp.status_code == 200
    g = guidance_resp.json()
    name = g["scheme"]["display_name"]
    fields_cnt = len(g["fields"])
    elig_cnt = len(g["eligibility_requirements"])
    docs_cnt = len(g["document_requirements"])
    print(f"Scheme {sid} ({name}): {fields_cnt} fields, {elig_cnt} eligibility criteria, {docs_cnt} docs")
    assert fields_cnt > 0, f"Scheme {sid} must have fields"

print("ALL BACKEND AUDIT AND SCHEME GUIDANCE TESTS PASSED (100% COVERAGE)!")
