from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data


def test_chat_rejects_empty_query():
    response = client.post("/api/chat", json={"query": "   "})
    assert response.status_code == 422


def test_chat_missing_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()

    response = client.post("/api/chat", json={"query": "What are Grade 5 fees?"})
    assert response.status_code == 503
    assert "GOOGLE_API_KEY" in response.json()["detail"]

    get_settings.cache_clear()
