import pytest

import agent
import llm
import tools


@pytest.fixture(autouse=True)
def _stub_workspace_name(monkeypatch):
    async def fake_get_workspace_name():
        return "Acme Workspace"

    monkeypatch.setattr(tools, "get_workspace_name", fake_get_workspace_name)


async def test_agent_completes_without_tool_calls(monkeypatch):
    async def fake_chat(messages, tools=None, temperature=0.1):
        return {"role": "assistant", "content": "Hello there!"}

    monkeypatch.setattr(llm, "chat", fake_chat)

    result = await agent.run_agent("hi", [])

    assert result["stopped_reason"] == "complete"
    assert result["text"] == "Hello there!"
    assert result["trace"] == []
    assert result["messages"][0]["role"] == "system"
    assert "Acme Workspace" in result["messages"][0]["content"]


async def test_agent_calls_tool_then_completes(monkeypatch):
    calls = {"n": 0}

    async def fake_chat(messages, tools=None, temperature=0.1):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "list_workspace", "arguments": {}}}],
            }
        return {"role": "assistant", "content": "Here are your lists."}

    async def fake_execute(name, arguments):
        assert name == "list_workspace"
        return {"ok": True, "result": {"spaces": []}, "error": None, "ms": 5}

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(tools, "execute", fake_execute)

    result = await agent.run_agent("what lists exist?", [])

    assert result["stopped_reason"] == "complete"
    assert result["text"] == "Here are your lists."
    assert result["trace"] == [{"tool": "list_workspace", "ok": True, "ms": 5}]


async def test_agent_stops_at_max_steps(monkeypatch):
    async def fake_chat(messages, tools=None, temperature=0.1):
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "list_workspace", "arguments": {}}}],
        }

    async def fake_execute(name, arguments):
        return {"ok": True, "result": {}, "error": None, "ms": 1}

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(tools, "execute", fake_execute)

    result = await agent.run_agent("loop forever", [], max_steps=3)

    assert result["stopped_reason"] == "max_steps"
    assert len(result["trace"]) == 3


async def test_agent_records_failed_tool_call_in_trace(monkeypatch):
    calls = {"n": 0}

    async def fake_chat(messages, tools=None, temperature=0.1):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "search_tasks", "arguments": {"list_name": "Ghost"}}}],
            }
        return {"role": "assistant", "content": "That list doesn't exist."}

    async def fake_execute(name, arguments):
        return {"ok": False, "result": None, "error": "No list named 'Ghost'", "ms": 3}

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(tools, "execute", fake_execute)

    result = await agent.run_agent("what's in Ghost?", [])

    assert result["stopped_reason"] == "complete"
    assert result["trace"] == [{"tool": "search_tasks", "ok": False, "ms": 3}]


async def test_agent_never_raises_on_llm_failure(monkeypatch):
    async def fake_chat(messages, tools=None, temperature=0.1):
        raise ConnectionError("ollama unreachable")

    monkeypatch.setattr(llm, "chat", fake_chat)

    result = await agent.run_agent("hi", [])

    assert result["stopped_reason"] == "error"
    assert "ollama unreachable" in result["text"]


async def test_public_agent_completes_without_tool_calls(monkeypatch):
    async def fake_chat(messages, tools=None, temperature=0.1):
        assert {s["name"] for s in tools} == {"search_helpdesk_tickets"}
        return {"role": "assistant", "content": "Hi! How can I help?"}

    monkeypatch.setattr(llm, "chat", fake_chat)

    result = await agent.run_public_agent("hi", [])

    assert result["stopped_reason"] == "complete"
    assert result["text"] == "Hi! How can I help?"
    assert result["trace"] == []
    assert "Helpdesk Hero" in result["messages"][0]["content"]
    assert "Acme Workspace" not in result["messages"][0]["content"]


async def test_public_agent_calls_search_helpdesk_tickets(monkeypatch):
    calls = {"n": 0}

    async def fake_chat(messages, tools=None, temperature=0.1):
        calls["n"] += 1
        if calls["n"] == 1:
            assert {s["name"] for s in tools} == {"search_helpdesk_tickets"}
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "search_helpdesk_tickets", "arguments": {"query": "wifi"}}}
                ],
            }
        return {"role": "assistant", "content": "Found 1 matching ticket."}

    async def fake_execute_public(name, arguments):
        assert name == "search_helpdesk_tickets"
        return {"ok": True, "result": {"tasks": []}, "error": None, "ms": 4}

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(tools, "execute_public", fake_execute_public)

    result = await agent.run_public_agent("any wifi tickets?", [])

    assert result["stopped_reason"] == "complete"
    assert result["trace"] == [{"tool": "search_helpdesk_tickets", "ok": True, "ms": 4}]


async def test_public_agent_cannot_reach_create_task(monkeypatch):
    """Even if the LLM hallucinates a create_task call, run_public_agent only ever
    calls tools.execute_public, whose registry structurally excludes create_task."""
    calls = {"n": 0}

    async def fake_chat(messages, tools=None, temperature=0.1):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "create_task", "arguments": {"list_name": "QA", "name": "x"}}}],
            }
        return {"role": "assistant", "content": "I can't create tickets from chat."}

    monkeypatch.setattr(llm, "chat", fake_chat)

    result = await agent.run_public_agent("create a task", [])

    assert result["stopped_reason"] == "complete"
    assert result["trace"] == [{"tool": "create_task", "ok": False, "ms": 0}]


async def test_agent_truncates_large_tool_results(monkeypatch):
    calls = {"n": 0}

    async def fake_chat(messages, tools=None, temperature=0.1):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "search_tasks", "arguments": {}}}],
            }
        tool_message = next(m for m in messages if m["role"] == "tool")
        assert len(tool_message["content"]) <= 4000 + len("... [truncated]")
        return {"role": "assistant", "content": "done"}

    async def fake_execute(name, arguments):
        return {"ok": True, "result": {"blob": "x" * 10000}, "error": None, "ms": 1}

    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(tools, "execute", fake_execute)

    result = await agent.run_agent("search everything", [])

    assert result["stopped_reason"] == "complete"
