"""
NagrikSaarathi — Authentication & Role-Based Access Control Tests
"""

import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.seed import seed


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed(reset=False)


@pytest.fixture
def client():
    return TestClient(app)


class TestAuthenticationEndpoints:
    def test_demo_credentials_listing(self, client):
        resp = client.get("/api/auth/demo-credentials")
        assert resp.status_code == 200
        data = resp.json()
        assert data["demo_mode"] is True
        assert len(data["accounts"]) >= 2
        roles = {a["role"] for a in data["accounts"]}
        assert "citizen" in roles
        assert "official" in roles

    def test_citizen_login_success(self, client):
        resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "9876543210",
                "password": "Citizen@2026",
                "role": "citizen",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "citizen"
        assert data["user"]["identifier"] == "9876543210"

    def test_official_login_success(self, client):
        resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "officer@dept.gov.in",
                "password": "Officer@2026",
                "role": "official",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "official"
        assert data["user"]["department"] is not None

    def test_invalid_credentials_rejected(self, client):
        resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "9876543210",
                "password": "WrongPassword123!",
                "role": "citizen",
            },
        )
        assert resp.status_code == 401
        assert "Invalid credentials" in resp.json()["detail"]

    def test_wrong_role_rejected(self, client):
        # Trying to login as official using citizen credentials
        resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "9876543210",
                "password": "Citizen@2026",
                "role": "official",
            },
        )
        assert resp.status_code == 401

    def test_get_current_user_profile(self, client):
        # 1. Login
        login_resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "9876543210",
                "password": "Citizen@2026",
                "role": "citizen",
            },
        )
        token = login_resp.json()["access_token"]

        # 2. Get profile
        me_resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        profile = me_resp.json()
        assert profile["identifier"] == "9876543210"
        assert profile["role"] == "citizen"

    def test_official_token_can_access_dashboard(self, client):
        # Official login
        login_resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "officer@dept.gov.in",
                "password": "Officer@2026",
                "role": "official",
            },
        )
        token = login_resp.json()["access_token"]

        # Access real (non-demo) dashboard
        dash_resp = client.get(
            "/api/dashboard/summary?include_demo=false",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert dash_resp.status_code == 200

    def test_citizen_token_cannot_access_real_dashboard(self, client):
        # Citizen login
        login_resp = client.post(
            "/api/auth/login",
            json={
                "identifier": "9876543210",
                "password": "Citizen@2026",
                "role": "citizen",
            },
        )
        token = login_resp.json()["access_token"]

        # Attempt to access real departmental dashboard
        dash_resp = client.get(
            "/api/dashboard/summary?include_demo=false",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert dash_resp.status_code == 403

    def test_logout_endpoint(self, client):
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert "Successfully logged out" in resp.json()["message"]
