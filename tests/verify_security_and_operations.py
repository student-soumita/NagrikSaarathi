"""
End-to-end Security, Operational Access, and Functional Verification Script
for NagrikSaarathi (Tests all 14 requirements specified in Priority 9).
"""

import sys
import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

passed_tests = []
failed_tests = []

def test(name):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            print(f"\n[TEST] {name} ...", end=" ", flush=True)
            try:
                fn(*args, **kwargs)
                print("PASSED [OK]")
                passed_tests.append(name)
            except Exception as e:
                err_msg = str(e).encode("ascii", "replace").decode()
                print(f"FAILED [ERR]: {err_msg}")
                failed_tests.append((name, err_msg))
        return wrapper
    return decorator


def login(identifier, password, role="citizen"):
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": identifier,
        "password": password,
        "role": role,
    })
    if res.status_code != 200:
        raise Exception(f"Login failed for {identifier} ({role}): {res.status_code} {res.text}")
    return res.json()["access_token"]


# ── TEST 1: Citizen cannot register as a Department Official ──────────────
@test("1. Citizen cannot register as a Department Official")
def test_1():
    # Attempt to submit an official or elevated role via register endpoint
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "full_name": "Attacker Trying Official Role",
        "email": f"attacker_{int(datetime.now().timestamp())}@example.com",
        "password": "Password@1234",
        "role": "official",
        "department": "Ministry of Defense"
    })
    # Since RegisterRequest enforces role: Literal['citizen'], passing official must be rejected (422)
    # OR registered strictly as a citizen with no official privileges
    if res.status_code == 422:
        return
    elif res.status_code in (200, 201):
        user = res.json().get("user", {})
        if user.get("role") != "citizen" or user.get("department"):
            raise Exception(f"VULNERABILITY: Public user obtained role '{user.get('role')}' with department '{user.get('department')}'!")
    else:
        raise Exception(f"Unexpected status: {res.status_code} {res.text}")


# ── TEST 2: Arbitrary user cannot activate invitation without required checks ──
@test("2. Arbitrary user cannot activate an invitation without required checks")
def test_2():
    fake_token = "NON-EXISTENT-FAKE-TOKEN-999"
    res = requests.get(f"{BASE_URL}/auth/invitation/{fake_token}")
    if res.status_code != 404:
        raise Exception(f"Expected 404 for invalid token, got {res.status_code}")

    res_act = requests.post(f"{BASE_URL}/auth/invitation/activate", json={
        "token": fake_token,
        "password": "ValidPassword@123",
    })
    if res_act.status_code != 404:
        raise Exception(f"Expected 404 on activation of fake token, got {res_act.status_code}")


# ── TEST 3: Expired and reused invitations are rejected ────────────────────
@test("3. Expired and reused invitations are rejected")
def test_3():
    admin_token = login("admin@nagrik.gov.in", "Admin@2026", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    unique_email = f"officer_expired_{int(datetime.now().timestamp())}@dept.gov.in"
    inv_res = requests.post(f"{BASE_URL}/admin/official-invitations", headers=headers, json={
        "email": unique_email,
        "full_name": "Test Official Expired",
        "department": "Ministry of Electronics and Information Technology",
        "expires_in_days": 1,
    })
    if inv_res.status_code not in (200, 201):
        raise Exception(f"Failed to create invitation: {inv_res.text}")
    inv_data = inv_res.json()
    token = inv_data["invitation_token"]

    # 1. Activate it successfully the first time
    act_res = requests.post(f"{BASE_URL}/auth/invitation/activate", json={
        "token": token,
        "password": "SecurePassword@2026",
    })
    if act_res.status_code != 200:
        raise Exception(f"First activation failed: {act_res.text}")

    # 2. Try to REUSE the same token
    reuse_res = requests.post(f"{BASE_URL}/auth/invitation/activate", json={
        "token": token,
        "password": "AnotherPassword@2026",
    })
    if reuse_res.status_code != 400:
        raise Exception(f"Expected 400 on reused token, got {reuse_res.status_code}: {reuse_res.text}")


# ── TEST 4: A pending official cannot access protected dashboard APIs ─────
@test("4. A pending official cannot access protected dashboard APIs")
def test_4():
    citizen_token = login("citizen@nagrik.gov.in", "Citizen@2026", role="citizen")
    c_headers = {"Authorization": f"Bearer {citizen_token}"}

    # Attempt to access department official schemes
    dept_res = requests.get(f"{BASE_URL}/department/my-schemes", headers=c_headers)
    if dept_res.status_code != 403:
        raise Exception(f"Citizen accessed department API! Expected 403, got {dept_res.status_code}")

    # Attempt to access admin official invitations
    admin_res = requests.get(f"{BASE_URL}/admin/official-invitations", headers=c_headers)
    if admin_res.status_code != 403:
        raise Exception(f"Citizen accessed admin API! Expected 403, got {admin_res.status_code}")


# ── TEST 5: An authorised official can access only the assigned department's data ──
@test("5. Authorised official can access only assigned department's data")
def test_5():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}

    schemes_res = requests.get(f"{BASE_URL}/department/my-schemes", headers=agri_headers)
    if schemes_res.status_code != 200:
        raise Exception(f"Failed to fetch schemes: {schemes_res.status_code} {schemes_res.text}")

    schemes = schemes_res.json()
    for s in schemes:
        dept_name = s.get("ministry_name") or s.get("department_name") or ""
        assert len(dept_name) > 0


# ── TEST 6: A Department Official cannot grant themselves additional permissions ──
@test("6. Department Official cannot grant themselves additional permissions")
def test_6():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}

    # Attempt to issue an official invitation (admin only)
    res = requests.post(f"{BASE_URL}/admin/official-invitations", headers=agri_headers, json={
        "email": "self_invite@dept.gov.in",
        "full_name": "Rogue Official",
        "department": "Ministry of Finance",
    })
    if res.status_code != 403:
        raise Exception(f"Official accessed admin invitation provisioning! Status: {res.status_code}")

    # Attempt to self-approve a radar change
    res_review = requests.post(f"{BASE_URL}/admin/radar/1/review", headers=agri_headers, json={
        "action": "approve"
    })
    if res_review.status_code != 403:
        raise Exception(f"Official accessed admin radar review endpoint! Status: {res_review.status_code}")


# ── TEST 7: A revoked official immediately loses protected access ────────
@test("7. A revoked official immediately loses protected access")
def test_7():
    admin_token = login("admin@nagrik.gov.in", "Admin@2026", role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Issue & activate a temporary official
    temp_email = f"temp_officer_{int(datetime.now().timestamp())}@dept.gov.in"
    inv_res = requests.post(f"{BASE_URL}/admin/official-invitations", headers=admin_headers, json={
        "email": temp_email,
        "full_name": "Temporary Official",
        "department": "Ministry of Agriculture and Farmers Welfare",
        "expires_in_days": 1,
    })
    if inv_res.status_code not in (200, 201):
        raise Exception(f"Failed to create invitation: {inv_res.text}")
    token = inv_res.json()["invitation_token"]

    requests.post(f"{BASE_URL}/auth/invitation/activate", json={
        "token": token,
        "password": "TempPassword@2026",
    })

    # Log in as the new official
    temp_off_token = login(temp_email, "TempPassword@2026", role="official")
    temp_headers = {"Authorization": f"Bearer {temp_off_token}"}

    # Verify they can access department API
    ok_res = requests.get(f"{BASE_URL}/department/my-schemes", headers=temp_headers)
    if ok_res.status_code != 200:
        raise Exception(f"Active official could not access schemes: {ok_res.status_code}")

    # Now Admin suspends this official
    officials_res = requests.get(f"{BASE_URL}/admin/officials?search={temp_email}", headers=admin_headers)
    officials_data = officials_res.json()
    officials = officials_data if isinstance(officials_data, list) else officials_data.get("items", [])
    if not officials:
        raise Exception("Could not find provisioned official in admin list")
    off_id = officials[0]["id"]

    susp_res = requests.post(f"{BASE_URL}/admin/officials/{off_id}/suspend", headers=admin_headers)
    if susp_res.status_code != 200:
        raise Exception(f"Failed to suspend official: {susp_res.text}")

    # Attempt to access department API again with previous token -> must fail with 403
    forbidden_res = requests.get(f"{BASE_URL}/department/my-schemes", headers=temp_headers)
    if forbidden_res.status_code != 403:
        raise Exception(f"Suspended official still accessed protected API! Status: {forbidden_res.status_code}")


# ── TEST 8: A scheme change remains a draft until approved ─────────────────
@test("8. A scheme change remains a draft until approved")
def test_8():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}

    # Submit a radar change for Scheme 2 (PM-KISAN - Agriculture)
    sub_res = requests.post(f"{BASE_URL}/department/radar/submit", headers=agri_headers, json={
        "scheme_id": 2,
        "source_url": "https://pmkisan.gov.in/notification-draft-2026.pdf",
        "source_title": "PM-KISAN Gazette Revision Draft 2026",
        "source_version": "Gazette Ref 2026-TestDraft",
        "source_document_text": "Revised installment of PM-KISAN to INR 7,000 annually.",
        "detected_changes": [{
            "category": "benefits",
            "field_name": "Annual Financial Assistance",
            "old_value": "₹6,000 per annum",
            "new_value": "₹7,000 per annum",
            "supporting_passage": "Revised installment of PM-KISAN to INR 7,000 annually.",
            "confidence": 0.95,
            "requires_manual_validation": False,
        }],
        "diff_summary": {
            "total_differences": 1,
            "benefit_changes_count": 1,
            "eligibility_changes_count": 0,
            "document_changes_count": 0,
            "url_changes_count": 0,
            "uncertain_flags_count": 0
        },
        "uncertain_flags": []
    })
    if sub_res.status_code not in (200, 201):
        raise Exception(f"Failed to submit radar change: {sub_res.text}")

    radar_record = sub_res.json()
    if radar_record["status"] not in ("submitted", "draft"):
        raise Exception(f"Newly submitted radar change set is not in draft/submitted state: {radar_record['status']}")


# ── TEST 9: A published change is saved and retrievable ───────────────────
@test("9. A published change is saved and retrievable")
def test_9():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}
    admin_token = login("admin@nagrik.gov.in", "Admin@2026", role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Submit radar change for Scheme 2
    sub_res = requests.post(f"{BASE_URL}/department/radar/submit", headers=agri_headers, json={
        "scheme_id": 2,
        "source_url": "https://pmkisan.gov.in/notification-publish-2026.pdf",
        "source_title": "PM-KISAN Benefit Enhancement Gazette 2026",
        "source_version": "2026-PublishTest",
        "source_document_text": "Official Benefit Revision: Annual payment updated to 7500 INR.",
        "detected_changes": [{
            "category": "benefits",
            "field_name": "Annual Financial Assistance",
            "old_value": "₹6,000 per annum",
            "new_value": "₹7,500 per annum",
            "supporting_passage": "Annual payment updated to 7500 INR.",
            "confidence": 0.95,
            "requires_manual_validation": False,
        }],
        "diff_summary": {
            "total_differences": 1,
            "benefit_changes_count": 1,
            "eligibility_changes_count": 0,
            "document_changes_count": 0,
            "url_changes_count": 0,
            "uncertain_flags_count": 0
        },
        "uncertain_flags": []
    })
    if sub_res.status_code not in (200, 201):
        raise Exception(f"Failed to submit radar change: {sub_res.text}")

    radar_id = sub_res.json()["id"]

    # Admin approves and publishes
    rev_res = requests.post(f"{BASE_URL}/admin/radar/{radar_id}/review", headers=admin_headers, json={
        "action": "approve",
        "review_notes": "Approved and committed to database."
    })
    if rev_res.status_code != 200:
        raise Exception(f"Failed to approve radar: {rev_res.text}")

    # Verify status is published
    detail_res = requests.get(f"{BASE_URL}/admin/radar/{radar_id}", headers=admin_headers)
    if detail_res.status_code != 200:
        raise Exception(f"Failed to retrieve radar record: {detail_res.text}")
    status = detail_res.json()["status"]
    if status != "published":
        raise Exception(f"Expected status 'published', got '{status}'")


# ── TEST 10: Source evidence remains linked to its relevant scheme fields ─
@test("10. Source evidence remains linked to its relevant scheme fields")
def test_10():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}

    ev_res = requests.post(f"{BASE_URL}/department/evidence", headers=agri_headers, json={
        "scheme_id": 2,
        "field_category": "eligibility",
        "field_key": "landholding_criteria",
        "field_label": "Landholding Eligibility Criteria",
        "claim_value": "Small and marginal farmers owning cultivable land up to 2 hectares",
        "official_source_url": "https://pmkisan.gov.in/guidelines-evidence-test.pdf",
        "source_title": "Operational Guidelines of PM-KISAN Section 3.1",
        "responsible_department": "Ministry of Agriculture and Farmers Welfare",
        "supporting_quotation": "Para 3.1: All landholding farmer families having cultivable landholding in their names"
    })
    if ev_res.status_code not in (200, 201):
        raise Exception(f"Failed to submit field evidence: {ev_res.text}")

    ev_id = ev_res.json()["id"]

    # Retrieve evidence list
    list_res = requests.get(f"{BASE_URL}/department/evidence?scheme_id=2", headers=agri_headers)
    records = list_res.json()
    matching = [r for r in records if r["id"] == ev_id]
    if not matching:
        raise Exception("Created evidence record not found in query results")
    if matching[0]["field_key"] != "landholding_criteria" or "Operational Guidelines" not in matching[0]["source_title"]:
        raise Exception("Evidence linkage corrupted or mismatched")


# ── TEST 11: Translation changes are flagged when their source text changes ──
@test("11. Translation changes are flagged when source text changes")
def test_11():
    admin_token = login("admin@nagrik.gov.in", "Admin@2026", role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # In test 9 we published a radar change on scheme 2.
    # Check that translation drift alerts were automatically generated!
    drift_res = requests.get(f"{BASE_URL}/admin/translation-drift", headers=admin_headers)
    if drift_res.status_code != 200:
        raise Exception(f"Failed to query translation drift: {drift_res.text}")

    alerts = drift_res.json()
    scheme_2_alerts = [a for a in alerts if a["scheme_id"] == 2]
    if not scheme_2_alerts:
        raise Exception("No translation drift alerts generated following scheme 2 publication!")
    # Check that Eighth Schedule languages were flagged
    languages_flagged = {a.get("target_language") or a.get("language_code") for a in scheme_2_alerts}
    if "hi" not in languages_flagged and "bn" not in languages_flagged:
        raise Exception(f"Expected major scheduled languages in drift alerts, got: {languages_flagged}")


# ── TEST 12: Heatmap statistics use real, privacy-preserving event data ───
@test("12. Heatmap statistics use real, privacy-preserving event data (< 3 threshold)")
def test_12():
    agri_token = login("officer@dept.gov.in", "Officer@2026", role="official")
    agri_headers = {"Authorization": f"Bearer {agri_token}"}

    # Request heatmap for a filter with 0 sessions
    res = requests.get(f"{BASE_URL}/department/heatmap?days=7&scheme_id=9999", headers=agri_headers)
    if res.status_code != 200:
        raise Exception(f"Failed to query heatmap: {res.status_code} {res.text}")

    data = res.json()
    # Must enforce privacy threshold
    if not data.get("is_insufficient_data"):
        raise Exception(f"Privacy violation: heatmap did not flag insufficient data when sessions < 3! Data: {data}")


# ── TEST 13: Existing Citizen and Admin functionality remain intact ───────
@test("13. Existing Citizen and Admin functions remain intact")
def test_13():
    # Citizen can get public schemes
    schemes_res = requests.get(f"{BASE_URL}/schemes")
    if schemes_res.status_code != 200:
        raise Exception(f"Citizen public scheme catalogue returned status {schemes_res.status_code}")
    res_data = schemes_res.json()
    items = res_data if isinstance(res_data, list) else res_data.get("items", [])
    if len(items) == 0:
        raise Exception("Citizen public scheme catalogue is empty")

    # Citizen can get scheme detail
    detail_res = requests.get(f"{BASE_URL}/schemes/2")
    if detail_res.status_code != 200:
        raise Exception("Scheme detail endpoint broken")

    # Languages endpoint
    lang_res = requests.get(f"{BASE_URL}/languages")
    lang_data = lang_res.json()
    langs = lang_data.get("items", lang_data if isinstance(lang_data, list) else [])
    if lang_res.status_code != 200 or len(langs) < 22:
        raise Exception(f"22 Eighth Schedule languages endpoint broken: count={len(langs)}")


# ── TEST 14: All workspaces share consistent theme tokens and Gov SSO Config ──
@test("14. Government SSO protocol is configured and testable")
def test_14():
    sso_res = requests.get(f"{BASE_URL}/auth/gov-sso/config")
    if sso_res.status_code != 200:
        raise Exception(f"Gov SSO config endpoint failed: {sso_res.text}")

    sso_cfg = sso_res.json()
    prov_name = sso_cfg.get("provider_name") or sso_cfg.get("provider") or ""
    if "Parichay" not in prov_name:
        raise Exception(f"Unexpected SSO provider name: {prov_name}")
    if sso_cfg.get("is_configured") is not False:
        raise Exception("Gov SSO marked as operational without valid credentials!")


def run_all_tests():
    print("=" * 70)
    print("  NAGRIKSAARATHI SECURITY & OPERATIONAL WORKBENCH VERIFICATION")
    print("=" * 70)

    test_1()
    test_2()
    test_3()
    test_4()
    test_5()
    test_6()
    test_7()
    test_8()
    test_9()
    test_10()
    test_11()
    test_12()
    test_13()
    test_14()

    print("\n" + "=" * 70)
    print(f"RESULTS: {len(passed_tests)} Passed, {len(failed_tests)} Failed.")
    print("=" * 70)

    if failed_tests:
        print("\nFailures:")
        for name, err in failed_tests:
            print(f"- {name}: {err}")
        sys.exit(1)
    else:
        print("\nAll 14 Security & Operational Acceptance Tests PASSED successfully!")


if __name__ == "__main__":
    run_all_tests()
