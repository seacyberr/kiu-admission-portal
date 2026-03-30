def test_healthz(client):
    r = client.get("/api/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "kiu-portal-api"


def test_readyz(client):
    r = client.get("/api/readyz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "sqlite"


def test_security_headers(client):
    r = client.get("/api/healthz")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("X-Request-ID")
