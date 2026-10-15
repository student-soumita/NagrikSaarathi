import pytest
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import get_settings
from backend.app.models import User, GovernmentScheme, SchemeProposal
from backend.app.seed_pan_india_schemes import seed_pan_india_catalogue

settings = get_settings()
ADMIN_HEADERS = {"X-Admin-API-Key": settings.admin_api_key}

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_catalogue():
    seed_pan_india_catalogue()

def test_full_department_official_and_proposal_governance_lifecycle():
    unique_suffix = uuid.uuid4().hex[:6]
    official_identifier = f"agri_nodal_{unique_suffix}"

    # 1. Admin Provisions a Department Official
    official_payload = {
        "identifier": official_identifier,
        "email": f"{official_identifier}@gov.in",
        "password": "OfficialPassword123!",
        "full_name": "Dr. Ramesh Chandra",
        "department": "Ministry of Agriculture & Farmers Welfare",
        "designation": "Director (Schemes)",
        "state_scope": None,
    }
    create_off_res = client.post("/api/admin/officials", json=official_payload, headers=ADMIN_HEADERS)
    assert create_off_res.status_code == 201, create_off_res.text
    official_data = create_off_res.json()
    assert official_data["identifier"] == official_identifier
    assert official_data["department"] == "Ministry of Agriculture & Farmers Welfare"
    assert official_data["role"] == "official"

    # 2. Admin Lists Officials
    list_off_res = client.get("/api/admin/officials", headers=ADMIN_HEADERS)
    assert list_off_res.status_code == 200
    officials_list = list_off_res.json()
    assert any(o["identifier"] == official_identifier for o in officials_list)

    # 3. Department Official Logs In
    off_login_res = client.post("/api/auth/login", json={
        "identifier": official_identifier,
        "password": "OfficialPassword123!",
        "role": "official",
    })
    assert off_login_res.status_code == 200, off_login_res.text
    off_token = off_login_res.json()["access_token"]
    off_headers = {"Authorization": f"Bearer {off_token}"}

    # 4. Official checks stats & schemes
    stats_res = client.get("/api/department/stats", headers=off_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_schemes" in stats
    assert "pending_proposals" in stats

    # 5. Official creates a New Scheme Proposal
    new_prop_payload = {
        "proposal_type": "new_scheme",
        "scheme_name": f"PM Kisan Samriddhi Micro-Irrigation Grant {unique_suffix}",
        "government_level": "central",
        "category": "agriculture",
        "description": "Financial grant for smallholder farmers adopting drip and sprinkler irrigation technologies across drought-prone regions.",
        "benefit_summary": "Direct transfer of up to ₹25,000 subsidy per hectare for irrigation systems.",
        "official_source_url": "https://agricoop.nic.in/irrigation",
        "official_application_url": "https://pmkisan.gov.in/apply-irrigation",
        "source_evidence": "Gazette of India Notification AGRI-2026/04 dated 14-Jan-2026 under National Water Mission.",
    }
    create_prop_res = client.post("/api/department/proposals", json=new_prop_payload, headers=off_headers)
    assert create_prop_res.status_code == 201, create_prop_res.text
    prop_data = create_prop_res.json()
    prop_id = prop_data["id"]
    assert prop_data["proposal_number"].startswith("PRP-")
    assert prop_data["status"] == "submitted"
    assert prop_data["department_name"] == "Ministry of Agriculture & Farmers Welfare"

    # 6. Official lists their proposals
    off_props_res = client.get("/api/department/proposals", headers=off_headers)
    assert off_props_res.status_code == 200
    assert len(off_props_res.json()) >= 1

    # 7. Admin reviews proposal: first requests revision
    rev_req_payload = {
        "action": "request_revision",
        "revision_notes": "Please specify whether tenant farmers without land deeds are eligible.",
    }
    rev_res = client.post(f"/api/admin/proposals/{prop_id}/review", json=rev_req_payload, headers=ADMIN_HEADERS)
    assert rev_res.status_code == 200, rev_res.text
    assert rev_res.json()["status"] == "revision_required"

    # 8. Official updates proposal with clarifications and resubmits
    patch_payload = {
        "description": "Financial grant for smallholder farmers, including tenant farmers with registered agreements, adopting drip and sprinkler irrigation technologies.",
        "submit_now": True,
    }
    patch_res = client.patch(f"/api/department/proposals/{prop_id}", json=patch_payload, headers=off_headers)
    assert patch_res.status_code == 200, patch_res.text
    assert patch_res.json()["status"] == "submitted"

    # 9. Admin approves and publishes the proposal to the live catalogue
    appr_payload = {
        "action": "approve",
        "admin_notes": "Verified against Ministry of Agriculture notification #AG-2026/04. Approved for live catalogue.",
    }
    appr_res = client.post(f"/api/admin/proposals/{prop_id}/review", json=appr_payload, headers=ADMIN_HEADERS)
    assert appr_res.status_code == 200, appr_res.text
    approved_prop = appr_res.json()
    assert approved_prop["status"] == "approved"
    assert approved_prop["scheme_id"] is not None

    # 10. Verify the newly created scheme is live in public catalogue endpoint!
    pub_scheme_res = client.get(f"/api/schemes/{approved_prop['scheme_id']}")
    assert pub_scheme_res.status_code == 200
    live_scheme = pub_scheme_res.json()
    assert live_scheme["display_name"] == f"PM Kisan Samriddhi Micro-Irrigation Grant {unique_suffix}"
    assert live_scheme["is_active"] is True
    assert live_scheme["department_name"] == "Ministry of Agriculture & Farmers Welfare"
    assert "tenant farmers" in live_scheme["description"]
