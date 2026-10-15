"""
Tests for Scheme Requests, Help Tickets, Benefits Resolution, and Translation Audit.
Verifies compliance with all new requirements.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import get_settings
from backend.app.seed_pan_india_schemes import seed_pan_india_catalogue

client = TestClient(app)
settings = get_settings()
ADMIN_HEADERS = {"X-Admin-API-Key": settings.admin_api_key}


@pytest.fixture(autouse=True, scope="module")
def setup_catalogue():
    seed_pan_india_catalogue()


def test_scheme_request_lifecycle():
    # 1. Citizen submits a new scheme request
    payload = {
        "scheme_name": "Test Unique Solar Scheme 2026",
        "government_level": "state",
        "state_code": "RJ",
        "department_name": "Energy Department",
        "description": "Rooftop solar subsidy for residential consumers in Rajasthan.",
        "official_portal_url": "https://energy.rajasthan.gov.in/solar",
        "citizen_contact": "citizen.rajasthan@example.in",
    }
    resp = client.post("/api/schemes/requests", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    tracking_id = data["tracking_id"]
    assert tracking_id.startswith("REQ-")
    assert data["status"] == "Request Received"
    assert data["scheme_name"] == "Test Unique Solar Scheme 2026"
    req_id = data["id"]

    # 2. Citizen tracks request via public tracking endpoint
    track_resp = client.get(f"/api/schemes/requests/track/{tracking_id}")
    assert track_resp.status_code == 200
    assert track_resp.json()["tracking_id"] == tracking_id
    assert track_resp.json()["status"] == "Request Received"

    # 3. Admin views request queue
    admin_queue = client.get("/api/dashboard/scheme-requests", headers=ADMIN_HEADERS)
    assert admin_queue.status_code == 200
    all_reqs = admin_queue.json()
    assert any(r["tracking_id"] == tracking_id for r in all_reqs)

    # 4. Admin updates status to Under Review
    patch_resp = client.patch(
        f"/api/dashboard/scheme-requests/{req_id}",
        json={"status": "Under Review", "admin_notes": "Checking with nodal energy department."},
        headers=ADMIN_HEADERS,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "Under Review"

    # 5. Invariant check: Cannot mark 'Added to Catalogue' without a verified existing scheme
    fail_patch = client.patch(
        f"/api/dashboard/scheme-requests/{req_id}",
        json={"status": "Added to Catalogue", "linked_scheme_id": 999999},
        headers=ADMIN_HEADERS,
    )
    assert fail_patch.status_code == 400

    # 6. Admin publishes scheme from request (atomic transaction)
    pub_payload = {
        "display_name": "Rajasthan Rooftop Solar Scheme",
        "category": "other",
        "official_source_url": "https://energy.rajasthan.gov.in/solar",
        "official_application_url": "https://energy.rajasthan.gov.in/apply",
        "department_name": "Energy Department",
        "beneficiary_groups": ["households"],
        "description": "Verified residential rooftop solar subsidy.",
        "admin_notes": "Official gazette verified and catalogued.",
    }
    pub_resp = client.post(
        f"/api/dashboard/scheme-requests/{req_id}/publish",
        json=pub_payload,
        headers=ADMIN_HEADERS,
    )
    assert pub_resp.status_code == 200
    pub_data = pub_resp.json()
    assert pub_data["status"] == "Added to Catalogue"
    assert pub_data["linked_scheme_id"] is not None
    assert pub_data["linked_scheme_slug"] is not None

    # 7. Confirm the published scheme is immediately retrievable in the catalogue
    new_scheme_id = pub_data["linked_scheme_id"]
    get_scheme = client.get(f"/api/schemes/{new_scheme_id}")
    assert get_scheme.status_code == 200
    assert get_scheme.json()["display_name"] == "Rajasthan Rooftop Solar Scheme"


def test_help_ticket_lifecycle():
    # 1. Citizen creates a help ticket
    payload = {
        "citizen_name": "Priya Patel",
        "citizen_contact": "priya.patel@example.in",
        "category": "guided_form_difficulty",
        "subject": "Unable to proceed past Step 2",
        "description": "The system asks for land record document number, but my document has an alphanumeric Khasra format.",
        "page_or_scheme_ref": "pm-kisan / step 2",
    }
    resp = client.post("/api/help/tickets", json=payload)
    assert resp.status_code == 201
    ticket = resp.json()
    ticket_num = ticket["ticket_number"]
    assert ticket_num.startswith("TKT-")
    assert ticket["status"] == "Received"
    assert ticket["category"] == "guided_form_difficulty"
    ticket_id = ticket["id"]

    # 2. Track ticket
    track_resp = client.get(f"/api/help/tickets/track/{ticket_num}")
    assert track_resp.status_code == 200
    assert track_resp.json()["ticket_number"] == ticket_num

    # 3. Admin queues help tickets
    admin_q = client.get("/api/dashboard/help-tickets", headers=ADMIN_HEADERS)
    assert admin_q.status_code == 200
    assert any(t["ticket_number"] == ticket_num for t in admin_q.json())

    # 4. Admin resolves ticket with resolution message
    res_resp = client.patch(
        f"/api/dashboard/help-tickets/{ticket_id}",
        json={
            "status": "Resolved",
            "resolution_message": "Alphanumeric Khasra numbers are supported. Please omit slashes and dashes when entering the number.",
        },
        headers=ADMIN_HEADERS,
    )
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "Resolved"
    assert res_resp.json()["resolved_at"] is not None

    # 5. Citizen submits satisfaction: Problem solved (Yes)
    feed_resp = client.post(
        f"/api/help/tickets/{ticket_num}/feedback",
        json={"satisfaction_solved": True, "feedback_notes": "Thank you, that worked!"},
    )
    assert feed_resp.status_code == 200
    assert feed_resp.json()["satisfaction_solved"] is True

    # 6. Citizen feedback with Reopening (No)
    reopen_resp = client.post(
        f"/api/help/tickets/{ticket_num}/feedback",
        json={
            "satisfaction_solved": False,
            "feedback_notes": "Still seeing an error code on submission.",
            "reopen": True,
        },
    )
    assert reopen_resp.status_code == 200
    reopened = reopen_resp.json()
    assert reopened["status"] == "In Progress"
    assert reopened["reopen_count"] == 1


def test_scheme_benefit_enrichment():
    # Verify PM-KISAN benefits have verified financial assistance
    resp = client.get("/api/schemes?search=PM-KISAN")
    assert resp.status_code == 200
    schemes = resp.json()["items"] if "items" in resp.json() else resp.json()
    assert len(schemes) > 0

    pm_kisan = next((s for s in schemes if "kisan" in s["slug"].lower() or "kisan" in s["display_name"].lower()), None)
    assert pm_kisan is not None
    benefits = pm_kisan["benefit_details"]
    assert "assistance_type" in benefits
    assert "₹6,000" in (benefits.get("benefit_amount") or "")
    assert benefits["is_verified"] is True


def test_translation_completeness_audit():
    resp = client.get("/api/dashboard/translation-audit", headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_canonical_keys" in data
    assert data["total_canonical_keys"] > 0
    assert "languages_audited" in data
    assert data["languages_audited"] >= 23  # en + 22 languages
    # Check English coverage is 100%
    en_audit = next(r for r in data["results"] if r["language_code"] == "en")
    assert en_audit["coverage_pct"] == 100.0
    assert en_audit["missing_keys"] == 0
    # Check Urdu is flagged as RTL
    ur_audit = next(r for r in data["results"] if r["language_code"] == "ur")
    assert ur_audit["is_rtl"] is True
