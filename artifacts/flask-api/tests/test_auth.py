def test_register_requires_fields(client):
    r = client.post("/api/auth/register", json={})
    assert r.status_code == 400
    data = r.get_json()
    assert "message" in data or "error" in data


def test_login_rejects_invalid_credentials(client):
    r = client.post(
        "/api/auth/login",
        json={"email": "nope@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_admission_list_requires_admin(client):
    r = client.get("/api/admission/applications")
    assert r.status_code == 401


def test_opportunities_list_public(client):
    """Listing opportunities is public (finalist browse)."""
    r = client.get("/api/opportunities")
    assert r.status_code == 200
    data = r.get_json()
    assert "opportunities" in data
