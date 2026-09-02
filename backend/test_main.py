"""A few focused tests: request validation, the happy path, and the AI-failure path.

The real Gemini call is monkeypatched everywhere -- these tests never hit the
network and never cost anything to run.
"""
import database
import main
import ai
from fastapi.testclient import TestClient


def make_client(tmp_path, monkeypatch):
    """Point the app at a fresh, isolated SQLite file for this test."""
    db_file = tmp_path / "test_entries.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    return TestClient(main.app)


def test_empty_text_is_rejected(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    with client:
        response = client.post("/entries", json={"text": ""})
    assert response.status_code == 422


def test_create_entry_success_and_list(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    def fake_call_gemini(text):
        return {"summary": "A short summary.", "tags": ["alpha", "beta", "gamma"]}

    monkeypatch.setattr(ai, "call_gemini", fake_call_gemini)

    with client:
        create_response = client.post("/entries", json={"text": "Some meeting notes."})
        assert create_response.status_code == 201
        body = create_response.json()
        assert body["summary"] == "A short summary."
        assert body["tags"] == ["alpha", "beta", "gamma"]

        list_response = client.get("/entries")
        assert list_response.status_code == 200
        entries = list_response.json()
        assert len(entries) == 1
        assert entries[0]["text"] == "Some meeting notes."


def test_ai_failure_returns_502_and_persists_nothing(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    def fake_call_gemini(text):
        raise ai.AIServiceError("The AI did not return valid JSON.")

    monkeypatch.setattr(ai, "call_gemini", fake_call_gemini)

    with client:
        create_response = client.post("/entries", json={"text": "Some text."})
        assert create_response.status_code == 502
        assert "detail" in create_response.json()

        list_response = client.get("/entries")
        assert list_response.json() == []
