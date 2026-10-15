"""
Unit and integration tests for URL Authority and Portal Link Audit in NagrikSaarathi.
Verifies that all stored, seeded, ingested, and returned links adhere strictly
to authoritative Indian government domains and standards.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.database import get_session_factory
from backend.app.models import GovernmentScheme
from backend.app.services.url_authority_service import (
    UrlAuthorityService,
    NATIONAL_DISCOVERY_PORTALS,
    STATE_AUTHORITY_PORTALS,
)

client = TestClient(app)


def test_url_authority_domain_validator():
    # Valid government domains
    assert UrlAuthorityService.is_valid_official_government_url("https://pmkisan.gov.in/")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://scholarships.gov.in/otr")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://beneficiary.nha.gov.in/")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://pmayg.nic.in/netiay")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://edistrict.delhigovt.nic.in/")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://wb.gov.in/")[0] is True
    assert UrlAuthorityService.is_valid_official_government_url("https://geda.goa.gov.in/")[0] is True

    # Disallowed, broken, or placeholder domains
    assert UrlAuthorityService.is_valid_official_government_url("")[0] is False
    assert UrlAuthorityService.is_valid_official_government_url(None)[0] is False
    assert UrlAuthorityService.is_valid_official_government_url("https://example.gov.in")[0] is False
    assert UrlAuthorityService.is_valid_official_government_url("https://rural.nic.in/schemes/cattle-shed")[0] is False
    assert UrlAuthorityService.is_valid_official_government_url("http://localhost:8000")[0] is False
    assert UrlAuthorityService.is_valid_official_government_url("https://google.com")[0] is False


def test_fallback_urls_for_jurisdictions():
    # State with configured portal
    wb_fallback = UrlAuthorityService.get_fallback_urls_for_jurisdiction("WB")
    assert wb_fallback["official_source_url"] == "https://wb.gov.in/"
    assert "edistrict" in wb_fallback["official_application_url"].lower()

    # Central fallback
    central_fallback = UrlAuthorityService.get_fallback_urls_for_jurisdiction(None)
    assert central_fallback["official_source_url"] == "https://www.myscheme.gov.in/"
    assert central_fallback["official_application_url"] == "https://serviceonline.gov.in/"


def test_all_database_schemes_have_valid_official_urls():
    db = get_session_factory()()
    try:
        schemes = db.execute(select(GovernmentScheme)).scalars().all()
        assert len(schemes) >= 10, "Expected at least 10 schemes in catalogue"

        for s in schemes:
            # Check source URL
            is_valid_src, reason_src = UrlAuthorityService.is_valid_official_government_url(s.official_source_url)
            assert is_valid_src is True, f"Scheme ID {s.id} ({s.slug}) has invalid source URL: {s.official_source_url} ({reason_src})"

            # Check application URL if present
            if s.official_application_url:
                is_valid_app, reason_app = UrlAuthorityService.is_valid_official_government_url(s.official_application_url)
                assert is_valid_app is True, f"Scheme ID {s.id} ({s.slug}) has invalid application URL: {s.official_application_url} ({reason_app})"
    finally:
        db.close()


def test_api_schemes_summary_includes_url_authority_metadata():
    resp = client.get("/api/schemes?page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0

    for item in data["items"]:
        assert "official_source_url" in item
        assert "official_application_url" in item
        assert "official_source_label" in item
        assert "application_portal_type" in item
        assert item["application_portal_type"] in ("DIRECT_ONLINE", "STATE_SSO_EDISTRICT", "OFFLINE_OFFICE", "NATIONAL_PORTAL")
        assert item["official_source_url"].startswith("http")


def test_dashboard_coverage_includes_state_portal_links():
    resp = client.get("/api/dashboard/coverage")
    assert resp.status_code == 200
    data = resp.json()

    assert data["verified_sources_count"] > 0
    assert data["missing_sources_count"] == 0, f"Expected 0 missing URLs in audit, found {data['missing_sources_count']}"

    state_items = data["state_ut_coverage"]
    assert len(state_items) == 36  # 28 States + 8 UTs

    for state_row in state_items:
        code = state_row["state_code"]
        assert "official_portal_url" in state_row
        assert "official_services_url" in state_row
        assert state_row["official_portal_url"] is not None
        assert state_row["official_portal_url"].startswith("http")
        assert state_row["official_services_url"] is not None
        assert state_row["official_services_url"].startswith("http")


def test_candidate_scheme_submission_with_fallback_resolution():
    # Submit candidate scheme with empty/dummy URL
    payload = {
        "display_name": "Rajasthan Dairy Incentive Scheme Test",
        "official_source_url": "",
        "state_code": "RJ",
        "category": "agriculture",
        "description": "Test candidate scheme for url fallback audit."
    }
    resp = client.post("/api/schemes/candidate", json=payload)
    assert resp.status_code == 201
    cand = resp.json()

    assert cand["display_name"] == "Rajasthan Dairy Incentive Scheme Test"
    assert cand["state_code"] == "RJ"
    # Should resolve to official Rajasthan state portal
    assert cand["official_source_url"] == "https://rajasthan.gov.in/"
    assert "janaadhaar" in cand["official_application_url"] or "rajasthan" in cand["official_application_url"]
    assert cand["official_source_is_fallback"] is True
