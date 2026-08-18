import pytest

import clickup
import tools


async def test_execute_list_workspace_success(monkeypatch):
    async def fake_list_workspace():
        return [{"space_name": "Marketing", "lists": [{"id": "1", "name": "General"}]}]

    monkeypatch.setattr(clickup, "list_workspace", fake_list_workspace)

    outcome = await tools.execute("list_workspace", {})

    assert outcome["ok"] is True
    assert outcome["result"] == {
        "spaces": [{"space_name": "Marketing", "lists": [{"id": "1", "name": "General"}]}]
    }
    assert outcome["error"] is None
    assert outcome["ms"] >= 0


async def test_execute_wraps_clickup_error_without_raising(monkeypatch):
    async def fake_search_tasks(**kwargs):
        raise clickup.ClickUpError("no such list")

    monkeypatch.setattr(clickup, "search_tasks", fake_search_tasks)

    outcome = await tools.execute("search_tasks", {"list_name": "Ghost"})

    assert outcome["ok"] is False
    assert outcome["error"] == "no such list"
    assert outcome["result"] is None


async def test_execute_unexpected_exception_is_caught(monkeypatch):
    async def fake_create_task(**kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(clickup, "create_task", fake_create_task)

    outcome = await tools.execute("create_task", {"list_name": "QA", "name": "x"})

    assert outcome["ok"] is False
    assert "boom" in outcome["error"]


async def test_execute_unknown_tool_returns_error_not_raise():
    outcome = await tools.execute("delete_everything", {})
    assert outcome["ok"] is False
    assert "Unknown tool" in outcome["error"]


async def test_execute_create_task_passes_kwargs_through(monkeypatch):
    captured = {}

    async def fake_create_task(**kwargs):
        captured.update(kwargs)
        return {"id": "1", "name": kwargs["name"], "url": "https://x"}

    monkeypatch.setattr(clickup, "create_task", fake_create_task)

    outcome = await tools.execute(
        "create_task", {"list_name": "QA", "name": "Test", "priority": "high"}
    )

    assert outcome["ok"] is True
    assert captured == {"list_name": "QA", "name": "Test", "priority": "high"}


def test_tool_schemas_names_match_registry():
    schema_names = {schema["name"] for schema in tools.TOOL_SCHEMAS}
    assert schema_names == set(tools.TOOLS.keys())
    assert schema_names == {"list_workspace", "search_tasks", "create_task", "search_knowledge_base"}


async def test_execute_search_knowledge_base_passes_kwargs_through(monkeypatch):
    captured = {}

    async def fake_search_kb(**kwargs):
        captured.update(kwargs)
        return {"results": [], "truncated": False}

    monkeypatch.setattr(clickup, "search_knowledge_base", fake_search_kb)

    outcome = await tools.execute("search_knowledge_base", {"query": "ringcentral"})

    assert outcome["ok"] is True
    assert captured == {"query": "ringcentral"}


# ---------------------------------------------------------------------------
# Public (helpdesk widget) tool surface — security-critical regression tests.
# ---------------------------------------------------------------------------


def test_public_tool_schemas_names_match_registry():
    schema_names = {schema["name"] for schema in tools.PUBLIC_TOOL_SCHEMAS}
    assert schema_names == set(tools.PUBLIC_TOOLS.keys())
    assert schema_names == {"search_knowledge_base"}


def test_public_registry_excludes_create_and_list_workspace_and_search_tasks():
    assert "create_task" not in tools.PUBLIC_TOOLS
    assert "list_workspace" not in tools.PUBLIC_TOOLS
    assert "search_tasks" not in tools.PUBLIC_TOOLS
    assert "create_task" not in {s["name"] for s in tools.PUBLIC_TOOL_SCHEMAS}
    assert "list_workspace" not in {s["name"] for s in tools.PUBLIC_TOOL_SCHEMAS}
    assert "search_tasks" not in {s["name"] for s in tools.PUBLIC_TOOL_SCHEMAS}


async def test_execute_public_create_task_is_unreachable():
    outcome = await tools.execute_public("create_task", {"list_name": "QA", "name": "x"})
    assert outcome["ok"] is False
    assert "Unknown tool" in outcome["error"]


async def test_execute_public_list_workspace_is_unreachable():
    outcome = await tools.execute_public("list_workspace", {})
    assert outcome["ok"] is False
    assert "Unknown tool" in outcome["error"]


async def test_execute_public_search_knowledge_base_success(monkeypatch):
    captured = {}

    async def fake_search_kb(**kwargs):
        captured.update(kwargs)
        return {"results": [], "truncated": False}

    monkeypatch.setattr(clickup, "search_knowledge_base", fake_search_kb)

    outcome = await tools.execute_public("search_knowledge_base", {"query": "ringcentral"})

    assert outcome["ok"] is True
    assert captured == {"query": "ringcentral"}
