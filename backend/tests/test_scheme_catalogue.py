import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.seed_pan_india_schemes import seed_pan_india_catalogue

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_catalogue():
    seed_pan_india_catalogue()


def test_list_schemes_returns_seeded_schemes():
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 5
    # Every scheme has the catalogue attributes
    for s in schemes:
        assert "government_level" in s
        assert "category" in s
        assert "portal_capability" in s
        assert "is_candidate" in s
        assert s["is_candidate"] is False


def test_filter_by_government_level():
    # Central schemes
    resp_central = client.get("/api/schemes?level=central")
    assert resp_central.status_code == 200
    central_schemes = resp_central.json()
    assert all(s["government_level"] == "central" for s in central_schemes)
    assert len(central_schemes) >= 3

    # State schemes
    resp_state = client.get("/api/schemes?level=state")
    assert resp_state.status_code == 200
    state_schemes = resp_state.json()
    assert all(s["government_level"] == "state" for s in state_schemes)
    assert len(state_schemes) >= 2


def test_filter_by_state_code():
    resp_wb = client.get("/api/schemes?state=WB")
    assert resp_wb.status_code == 200
    wb_schemes = resp_wb.json()
    assert len(wb_schemes) >= 1
    assert any(s["slug"] == "kanyashree-prakalpa-wb" for s in wb_schemes)

    resp_up = client.get("/api/schemes?state=UP")
    assert resp_up.status_code == 200
    up_schemes = resp_up.json()
    assert len(up_schemes) >= 1
    assert any(s["slug"] == "mksy-uttar-pradesh" for s in up_schemes)


def test_filter_by_category():
    resp_agri = client.get("/api/schemes?category=agriculture")
    assert resp_agri.status_code == 200
    agri_schemes = resp_agri.json()
    assert len(agri_schemes) >= 1
    assert any(s["slug"] == "pm-kisan" for s in agri_schemes)


def test_search_schemes():
    resp_search = client.get("/api/schemes?search=ayushman")
    assert resp_search.status_code == 200
    results = resp_search.json()
    assert len(results) >= 1
    assert any("ayushman" in s["display_name"].lower() or "ayushman" in s["slug"] for s in results)


def test_submit_candidate_scheme():
    payload = {
        "display_name": "Gram Panchayat Cattle Shed Subsidy",
        "official_source_url": "https://nrega.nic.in/",
        "department_name": "Animal Husbandry Department",
        "government_level": "state",
        "state_code": "RJ",
        "category": "agriculture",
        "description": "Financial subsidy for small dairy farmers to construct concrete cattle shed.",
        "user_notes": "Noticed on block notice board, please provide guidance form."
    }
    response = client.post("/api/schemes/candidate", json=payload)
    assert response.status_code == 201
    cand = response.json()
    assert cand["display_name"] == "Gram Panchayat Cattle Shed Subsidy"
    assert cand["is_candidate"] is True
    assert cand["verification_status"] == "pending_review"
    assert cand["portal_capability"] == "DISCOVERY_ONLY"
    assert cand["state_code"] == "RJ"

    # Verify candidate is NOT in default list_schemes
    resp_list = client.get("/api/schemes")
    assert not any(s["id"] == cand["id"] for s in resp_list.json())

    # Verify candidate IS in list_schemes when include_candidates=True
    resp_list_cand = client.get("/api/schemes?include_candidates=true")
    assert any(s["id"] == cand["id"] for s in resp_list_cand.json())


def test_paginated_schemes_response():
    resp = client.get("/api/schemes?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) <= 5
    assert data["total"] >= 5


def test_nationwide_coverage_endpoint():
    resp = client.get("/api/dashboard/coverage")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_schemes_discovered" in data
    assert "states_represented" in data
    assert "uts_represented" in data
    assert "all_28_states_covered" in data
    assert "all_8_uts_covered" in data
    assert "coverage_methodology_disclaimer" in data
    assert len(data["state_ut_coverage"]) == 36  # 28 States + 8 UTs


def test_extract_form_from_text():
    sample_text = """
    Application for Rural Artisan Solar Tool Kit
    Applicant Full Name:
    Aadhaar Number:
    District / Taluk:
    Bank Account Number and IFSC Code:
    Annual Family Income:
    Category (SC/ST/OBC/General):
    """
    resp = client.post("/api/schemes/extract-form", json={
        "scheme_name": "Rural Artisan Solar Tool Kit",
        "form_text_or_url": sample_text,
        "state_code": "OD",
        "category": "employment",
    })
    assert resp.status_code == 201
    extracted = resp.json()
    assert extracted["scheme"]["display_name"] == "Rural Artisan Solar Tool Kit"
    assert extracted["scheme"]["form_status"] == "EXTRACTED_DRAFT"
    assert len(extracted["extracted_fields"]) >= 3
    assert extracted["confidence_score"] > 0


def test_admin_bulk_import():
    import uuid
    suffix = uuid.uuid4().hex[:6]
    items = [
        {
            "display_name": f"Goa Solar Rooftop Subsidy {suffix}",
            "slug": f"goa-solar-rooftop-sub-{suffix}",
            "canonical_id": f"GOA-SOLAR-{suffix}",
            "government_level": "state",
            "state_code": "GA",
            "category": "energy",
            "ministry_name": "Department of New and Renewable Energy Goa",
            "portal_capability": "ASSISTED_PREPARATION",
            "official_source_url": "https://geda.goa.gov.in/",
            "form_status": "VERIFIED_SCHEMA",
        }
    ]
    resp = client.post("/api/schemes/admin/import?source_name=TEST_FIXTURE", json=items)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["total_processed"] == 1
    assert res_data["records_created"] == 1
