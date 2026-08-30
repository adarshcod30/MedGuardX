"""API tests -- the security fixes are the headline assertions here."""
from __future__ import annotations

from tests.conftest import _admin_token, _register


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- the old build's central flaw: unauthenticated access -----------------------
def test_protected_endpoints_reject_missing_token(client):
    # Missing bearer credential is rejected as unauthenticated (401/403).
    assert client.get("/api/stats").status_code in (401, 403)
    assert client.post("/api/retrieve", json={"patient_id": "x"}).status_code in (401, 403)
    assert client.post("/api/preview", json={"text": "hi"}).status_code in (401, 403)


def test_invalid_token_is_rejected(client):
    assert client.get("/api/stats", headers=_auth("garbage.token.here")).status_code == 401


# --- role is derived from the token, not the request body -----------------------
def test_role_cannot_be_supplied_in_request_body(client):
    # Register a RESEARCHER, then try to retrieve as if a doctor by stuffing
    # 'role' into the body. It must be ignored; researcher+treatment => DENY.
    tok = _register(client, "res1", role="researcher").json()["access_token"]
    r = client.post(
        "/api/retrieve",
        headers=_auth(tok),
        json={"patient_id": "nope", "purpose": "treatment", "consent": True, "role": "doctor"},
    )
    assert r.status_code == 403  # researcher denied treatment regardless of body 'role'


def test_doctor_retrieval_uses_token_role(client):
    tok = _register(client, "doc1", role="doctor").json()["access_token"]
    # Upload a record as this doctor.
    up = client.post(
        "/api/upload",
        headers=_auth(tok),
        files={"file": ("note.txt", b"Patient Jane Doe, no PII engine in stub.", "text/plain")},
    )
    assert up.status_code == 200, up.text
    pid = up.json()["patient_id"]

    r = client.post(
        "/api/retrieve",
        headers=_auth(tok),
        json={"patient_id": pid, "purpose": "treatment", "consent": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "doctor"
    assert body["masking_strategy"] == "full_access"


# --- role-gated audit -----------------------------------------------------------
def test_audit_requires_privileged_role(client):
    patient_tok = _register(client, "pat1", role="patient").json()["access_token"]
    assert client.get("/api/audit", headers=_auth(patient_tok)).status_code == 403

    admin_tok = _admin_token(client)  # seeded admin, not via /register
    assert client.get("/api/audit", headers=_auth(admin_tok)).status_code == 200


# --- auth basics ----------------------------------------------------------------
def test_duplicate_registration_conflicts(client):
    _register(client, "dupe")
    assert _register(client, "dupe").status_code == 409


def test_login_wrong_password_rejected(client):
    _register(client, "loginuser", password="rightpassword")
    bad = client.post("/api/login", json={"username": "loginuser", "password": "wrongpassword"})
    assert bad.status_code == 401


def test_audit_trail_attributes_real_actor(client):
    # A doctor may view audit and its actions are attributed to them.
    tok = _register(client, "auditor", role="doctor").json()["access_token"]
    client.post("/api/preview", headers=_auth(tok), json={"text": "hello", "purpose": "research"})
    logs = client.get("/api/audit", headers=_auth(tok)).json()["logs"]
    preview_logs = [l for l in logs if l["action"] == "PREVIEW"]
    assert preview_logs and preview_logs[0]["actor"] == "auditor"  # not user_id=0 anymore


def test_cannot_self_register_as_admin(client):
    r = client.post("/api/register", json={
        "username": "wannabe_admin", "password": "password123", "role": "admin",
    })
    assert r.status_code == 403
    assert "admin" in r.json()["detail"].lower()


def test_non_privileged_roles_still_register(client):
    for role in ("patient", "doctor", "nurse", "researcher", "company"):
        r = _register(client, f"ok_{role}", role=role)
        assert r.status_code == 201, r.text
        assert r.json()["role"] == role


def test_unreadable_image_is_rejected_not_stored(client):
    # An invalid image (or one that needs OCR when tesseract is absent) must be
    # rejected with 422, never stored as an "[OCR error: ...]" record.
    tok = _register(client, "img_doc", role="doctor").json()["access_token"]
    r = client.post(
        "/api/upload",
        headers=_auth(tok),
        files={"file": ("scan.png", b"not a real image", "image/png")},
    )
    assert r.status_code == 422
    assert "error" not in r.json().get("detail", "").lower()[:6]  # a helpful message, not a stack string
