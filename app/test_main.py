"""Minimal API tests. Run with: pytest"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_qr_returns_png():
    res = client.get("/api/qr", params={"data": "https://example.com"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert res.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_qr_requires_data():
    res = client.get("/api/qr")
    assert res.status_code == 422