import pytest
from fastapi.testclient import TestClient

import agent
import clickup
import llm
import main
import store

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def _clear_store():
    store._sessions.clear()
    yield
    store._sessions.clear()


def test_chat_endpoint_returns_agent_result(monkeypatch):
    async def fake_run_agent(message, history, max_steps=5):
        return {
            "text": "Three tasks are overdue.",
            "trace": [{"tool": "search_tasks", "ok": True, "ms": 100}],
            "stopped_reason": "complete",
            "messages": history + [{"role": "user", "content": message}],
        }

    monkeypatch.setattr(agent, "run_agent", fake_run_agent)

    response = client.post("/chat", json={"session_id": "s1", "message": "what's overdue?"})

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Three tasks are overdue."
    assert body["trace"] == [{"tool": "search_tasks", "ok": True, "ms": 100}]
    assert body["stopped_reason"] == "complete"


def test_chat_endpoint_persists_history_across_calls(monkeypatch):
    seen_histories = []

    async def fake_run_agent(message, history, max_steps=5):
        seen_histories.append(list(history))
        updated = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "ok"},
        ]
        return {"text": "ok", "trace": [], "stopped_reason": "complete", "messages": updated}

    monkeypatch.setattr(agent, "run_agent", fake_run_agent)

    client.post("/chat", json={"session_id": "s2", "message": "first"})
    client.post("/chat", json={"session_id": "s2", "message": "second"})

    assert seen_histories[0] == []
    assert len(seen_histories[1]) == 2


def test_chat_endpoint_rejects_missing_fields():
    response = client.post("/chat", json={"session_id": "s3"})
    assert response.status_code == 422


def test_create_ticket_success(monkeypatch):
    captured = {}

    async def fake_create_task(list_name, name, description=None, **kwargs):
        captured["list_name"] = list_name
        captured["name"] = name
        captured["description"] = description
        return {"id": "t1", "name": name, "url": "https://app.clickup.com/t/t1"}

    monkeypatch.setattr(clickup, "create_task", fake_create_task)

    response = client.post(
        "/api/ticket",
        json={
            "name": "Jane Doe",
            "email": "jane@bloomfield.k12.nj.us",
            "building": "Bloomfield High School",
            "room": "204",
            "category": "Network / WiFi",
            "description": "Can't connect to WiFi.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"id": "t1", "url": "https://app.clickup.com/t/t1", "status": "created"}
    assert captured["list_name"] == "Support Tickets"
    assert "Jane Doe" in captured["name"]
    assert "Requester: Jane Doe" in captured["description"]


def test_create_ticket_clickup_error_returns_502(monkeypatch):
    async def fake_create_task(*args, **kwargs):
        raise clickup.ClickUpError("no such list", status_code=404)

    monkeypatch.setattr(clickup, "create_task", fake_create_task)

    response = client.post(
        "/api/ticket",
        json={"name": "Jane Doe", "category": "Hardware", "description": "Broken laptop."},
    )

    assert response.status_code == 502


def test_create_ticket_rejects_missing_fields():
    response = client.post("/api/ticket", json={"name": "Jane Doe"})
    assert response.status_code == 422


def test_public_chat_endpoint_returns_agent_result(monkeypatch):
    async def fake_run_public_agent(message, history, max_steps=5):
        return {
            "text": "Here's what I found.",
            "trace": [{"tool": "search_helpdesk_tickets", "ok": True, "ms": 10}],
            "stopped_reason": "complete",
            "messages": history + [{"role": "user", "content": message}],
        }

    monkeypatch.setattr(agent, "run_public_agent", fake_run_public_agent)

    response = client.post("/api/chat", json={"session_id": "w1", "message": "any tickets?"})

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Here's what I found."
    assert body["trace"] == [{"tool": "search_helpdesk_tickets", "ok": True, "ms": 10}]


def test_public_chat_endpoint_does_not_call_internal_run_agent(monkeypatch):
    called = {"run_agent": False}

    async def fake_run_agent(message, history, max_steps=5):
        called["run_agent"] = True
        return {"text": "", "trace": [], "stopped_reason": "complete", "messages": []}

    async def fake_run_public_agent(message, history, max_steps=5):
        return {"text": "ok", "trace": [], "stopped_reason": "complete", "messages": []}

    monkeypatch.setattr(agent, "run_agent", fake_run_agent)
    monkeypatch.setattr(agent, "run_public_agent", fake_run_public_agent)

    client.post("/api/chat", json={"session_id": "w2", "message": "hi"})

    assert called["run_agent"] is False


def test_public_chat_endpoint_persists_history_across_calls(monkeypatch):
    seen_histories = []

    async def fake_run_public_agent(message, history, max_steps=5):
        seen_histories.append(list(history))
        updated = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "ok"},
        ]
        return {"text": "ok", "trace": [], "stopped_reason": "complete", "messages": updated}

    monkeypatch.setattr(agent, "run_public_agent", fake_run_public_agent)

    client.post("/api/chat", json={"session_id": "w3", "message": "first"})
    client.post("/api/chat", json={"session_id": "w3", "message": "second"})

    assert seen_histories[0] == []
    assert len(seen_histories[1]) == 2


def test_public_chat_session_is_namespaced_separately_from_agent_route(monkeypatch):
    async def fake_run_agent(message, history, max_steps=5):
        return {"text": "agent-reply", "trace": [], "stopped_reason": "complete", "messages": [{"role": "user", "content": message}]}

    async def fake_run_public_agent(message, history, max_steps=5):
        assert history == []  # must not see /chat's history for the same session_id
        return {"text": "widget-reply", "trace": [], "stopped_reason": "complete", "messages": [{"role": "user", "content": message}]}

    monkeypatch.setattr(agent, "run_agent", fake_run_agent)
    monkeypatch.setattr(agent, "run_public_agent", fake_run_public_agent)

    client.post("/chat", json={"session_id": "shared-id", "message": "hi"})
    client.post("/api/chat", json={"session_id": "shared-id", "message": "hi"})


def test_health_reports_both_down(monkeypatch):
    async def fake_is_reachable():
        return False, "ConnectError: connection refused"

    async def fake_ping_clickup():
        return False, "HTTP 401: unauthorized"

    monkeypatch.setattr(llm, "is_reachable", fake_is_reachable)
    monkeypatch.setattr(clickup, "ping_clickup", fake_ping_clickup)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "ollama": False,
        "clickup": False,
        "ollama_detail": "ConnectError: connection refused",
        "clickup_detail": "HTTP 401: unauthorized",
    }


def test_health_reflects_ollama_up_clickup_down(monkeypatch):
    async def fake_is_reachable():
        return True, None

    async def fake_ping_clickup():
        return False, "HTTP 401: unauthorized"

    monkeypatch.setattr(llm, "is_reachable", fake_is_reachable)
    monkeypatch.setattr(clickup, "ping_clickup", fake_ping_clickup)

    response = client.get("/health")

    assert response.json() == {
        "ollama": True,
        "clickup": False,
        "ollama_detail": None,
        "clickup_detail": "HTTP 401: unauthorized",
    }


def test_health_reports_both_up_with_no_detail(monkeypatch):
    async def fake_is_reachable():
        return True, None

    async def fake_ping_clickup():
        return True, None

    monkeypatch.setattr(llm, "is_reachable", fake_is_reachable)
    monkeypatch.setattr(clickup, "ping_clickup", fake_ping_clickup)

    response = client.get("/health")

    assert response.json() == {
        "ollama": True,
        "clickup": True,
        "ollama_detail": None,
        "clickup_detail": None,
    }
