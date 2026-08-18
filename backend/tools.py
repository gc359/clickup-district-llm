import time

import clickup
from config import get_settings

TOOL_SCHEMAS = [
    {
        "name": "list_workspace",
        "description": (
            "List all spaces and lists in the workspace. Call this first if you need "
            "a list ID — never guess or recall IDs."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "search_tasks",
        "description": (
            "Search tasks. Accepts a list NAME (not ID) — resolved internally. Omit "
            "list_name to search the whole workspace."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {"type": "string"},
                "query": {"type": "string", "description": "Text to match in task names"},
                "assignee": {"type": "string", "description": "Username or email"},
                "overdue_only": {"type": "boolean", "default": False},
                "include_closed": {"type": "boolean", "default": False},
            },
            "required": [],
        },
    },
    {
        "name": "create_task",
        "description": "Create a task. Accepts a list NAME, resolved internally.",
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "due_date": {"type": "string", "description": "ISO 8601 date"},
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "normal", "low"],
                },
                "assignee": {"type": "string"},
            },
            "required": ["list_name", "name"],
        },
    },
    {
        "name": "search_knowledge_base",
        "description": (
            "Search IT knowledge-base articles (e.g. RingCentral, Network setup) for help "
            "content. Returns matching page excerpts. Omit query to list all KB pages."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to match in KB page titles or content. Omit to list everything.",
                },
            },
            "required": [],
        },
    },
]


async def get_workspace_name() -> str:
    """Not a model-callable tool — used by agent.py to build the system prompt
    without importing clickup.py directly (per PRD D2)."""
    return await clickup.get_workspace_name()


async def _list_workspace(**_kwargs) -> dict:
    return {"spaces": await clickup.list_workspace()}


async def _search_tasks(**kwargs) -> dict:
    return await clickup.search_tasks(**kwargs)


async def _create_task(**kwargs) -> dict:
    return await clickup.create_task(**kwargs)


async def _search_knowledge_base(**kwargs) -> dict:
    return await clickup.search_knowledge_base(**kwargs)


TOOLS = {
    "list_workspace": _list_workspace,
    "search_tasks": _search_tasks,
    "create_task": _create_task,
    "search_knowledge_base": _search_knowledge_base,
}


async def _dispatch(name: str, arguments: dict, registry: dict) -> dict:
    """Dispatch a tool call by name against `registry`. Never raises — errors come back as {"ok": False, ...}."""
    start = time.monotonic()
    handler = registry.get(name)
    if handler is None:
        return {"ok": False, "result": None, "error": f"Unknown tool '{name}'", "ms": 0}
    try:
        result = await handler(**(arguments or {}))
        ms = int((time.monotonic() - start) * 1000)
        return {"ok": True, "result": result, "error": None, "ms": ms}
    except Exception as exc:
        ms = int((time.monotonic() - start) * 1000)
        return {"ok": False, "result": None, "error": str(exc), "ms": ms}


async def execute(name: str, arguments: dict) -> dict:
    """Dispatch a tool call by name. Never raises — errors come back as {"ok": False, ...}."""
    return await _dispatch(name, arguments, TOOLS)


# ---------------------------------------------------------------------------
# Public tool surface — exposed to the anonymous helpdesk chat widget only.
# Deliberately excludes list_workspace/create_task/search_tasks: this registry
# is the only set of tools reachable from that code path, not a runtime
# permission check. Ticket creation for the public widget bypasses this
# registry entirely (POST /api/ticket calls clickup.create_task directly).
# ---------------------------------------------------------------------------

PUBLIC_TOOL_SCHEMAS = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Search IT knowledge-base articles (e.g. RingCentral, Network setup) for help "
            "content. Query is optional: call with no arguments to list all KB pages."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Optional: text to match in KB page titles or content.",
                },
            },
            "required": [],
        },
    },
]


async def _public_search_knowledge_base(query: str | None = None, **_ignored) -> dict:
    return await clickup.search_knowledge_base(query=query)


PUBLIC_TOOLS = {
    "search_knowledge_base": _public_search_knowledge_base,
}


async def execute_public(name: str, arguments: dict) -> dict:
    """Dispatch a tool call by name against the scoped public registry only."""
    return await _dispatch(name, arguments, PUBLIC_TOOLS)
