import asyncio
import random
import time
from datetime import datetime, timezone

import httpx

from config import get_settings

BASE_URL = "https://api.clickup.com/api/v2"
API_V3_BASE = "https://api.clickup.com/api/v3"
_TREE_TTL_SECONDS = 60
_MAX_RESULTS = 25
_MAX_RETRIES = 2
_KB_CONTENT_CHARS = 3000

PRIORITY_MAP = {"urgent": 1, "high": 2, "normal": 3, "low": 4}


class ClickUpError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


_client: httpx.AsyncClient | None = None
_team_id: str | None = None
_teams_payload: list[dict] | None = None
_tree_task: "asyncio.Task | None" = None
_tree_expires_at: float = 0.0
_kb_task: "asyncio.Task | None" = None
_kb_expires_at: float = 0.0


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"Authorization": settings.clickup_token},
            timeout=15.0,
        )
    return _client


def reset_state_for_tests(client: httpx.AsyncClient | None = None) -> None:
    global _client, _team_id, _teams_payload, _tree_task, _tree_expires_at, _kb_task, _kb_expires_at
    _client = client
    _team_id = None
    _teams_payload = None
    _tree_task = None
    _tree_expires_at = 0.0
    _kb_task = None
    _kb_expires_at = 0.0


async def _request(method: str, path: str, **kwargs) -> httpx.Response:
    client = _get_client()
    attempt = 0
    while True:
        response = await client.request(method, path, **kwargs)
        if response.status_code != 429:
            return response
        if attempt >= _MAX_RETRIES:
            return response
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            wait = float(retry_after)
        else:
            reset = response.headers.get("X-RateLimit-Reset")
            wait = max(1.0, float(reset) - time.time()) if reset else 2.0
        wait = min(max(wait, 1.0), 10.0) + random.uniform(0, 0.5)
        await asyncio.sleep(wait)
        attempt += 1


async def _get_json(path: str, params: dict | None = None) -> dict:
    response = await _request("GET", path, params=params)
    if response.status_code >= 400:
        raise ClickUpError(
            f"ClickUp API error {response.status_code} on GET {path}: {response.text[:300]}",
            response.status_code,
        )
    return response.json()


async def _get_json_v3(path: str, params: dict | None = None) -> dict | list:
    response = await _request("GET", f"{API_V3_BASE}{path}", params=params)
    if response.status_code >= 400:
        raise ClickUpError(
            f"ClickUp API error {response.status_code} on GET {path}: {response.text[:300]}",
            response.status_code,
        )
    return response.json()


async def _fetch_teams() -> list[dict]:
    global _teams_payload
    if _teams_payload is None:
        data = await _get_json("/team")
        _teams_payload = data.get("teams") or []
    return _teams_payload


async def resolve_team_id() -> str:
    global _team_id
    if _team_id:
        return _team_id
    settings = get_settings()
    if settings.clickup_team_id:
        _team_id = settings.clickup_team_id
        return _team_id
    teams = await _fetch_teams()
    if not teams:
        raise ClickUpError("No ClickUp workspaces found for this token")
    _team_id = str(teams[0]["id"])
    return _team_id


async def _get_current_team() -> dict | None:
    teams = await _fetch_teams()
    team_id = await resolve_team_id()
    for team in teams:
        if str(team.get("id")) == team_id:
            return team
    return teams[0] if teams else None


async def get_workspace_name() -> str:
    try:
        team = await _get_current_team()
        return (team or {}).get("name") or "your ClickUp workspace"
    except Exception:
        return "your ClickUp workspace"


async def _get_team_members() -> list[dict]:
    team = await _get_current_team()
    if not team:
        return []
    return [m["user"] for m in team.get("members", []) if "user" in m]


async def _build_workspace_tree() -> list[dict]:
    team_id = await resolve_team_id()
    spaces_data = await _get_json(f"/team/{team_id}/space")
    spaces = spaces_data.get("spaces") or []

    async def build_space(space: dict) -> dict:
        space_id = space["id"]
        lists_data, folders_data = await asyncio.gather(
            _get_json(f"/space/{space_id}/list"),
            _get_json(f"/space/{space_id}/folder"),
        )
        lists = [{"id": str(l["id"]), "name": l["name"]} for l in lists_data.get("lists", [])]
        folders = folders_data.get("folders") or []
        if folders:
            folder_lists_results = await asyncio.gather(
                *[_get_json(f"/folder/{f['id']}/list") for f in folders]
            )
            for folder_lists in folder_lists_results:
                lists.extend(
                    {"id": str(l["id"]), "name": l["name"]} for l in folder_lists.get("lists", [])
                )
        return {"space_id": str(space_id), "space_name": space["name"], "lists": lists}

    return list(await asyncio.gather(*(build_space(s) for s in spaces)))


def _tree_cache_valid() -> bool:
    return _tree_task is not None and time.time() < _tree_expires_at


async def fetch_workspace_tree() -> list[dict]:
    global _tree_task, _tree_expires_at
    if not _tree_cache_valid():
        _tree_task = asyncio.ensure_future(_build_workspace_tree())
        _tree_expires_at = time.time() + _TREE_TTL_SECONDS
    try:
        return await _tree_task
    except Exception:
        _tree_task = None
        raise


async def list_workspace() -> list[dict]:
    tree = await fetch_workspace_tree()
    return [{"space_name": s["space_name"], "lists": s["lists"]} for s in tree]


async def resolve_list_id(list_name: str) -> str:
    tree = await fetch_workspace_tree()
    target = list_name.strip().lower()

    exact = [lst for space in tree for lst in space["lists"] if lst["name"].strip().lower() == target]
    if len(exact) == 1:
        return exact[0]["id"]
    if len(exact) > 1:
        candidates = ", ".join(f"{m['name']} ({m['id']})" for m in exact)
        raise ClickUpError(f"Multiple lists named '{list_name}' exist. Candidates: {candidates}")

    partial = [lst for space in tree for lst in space["lists"] if target in lst["name"].strip().lower()]
    if len(partial) == 1:
        return partial[0]["id"]
    if len(partial) > 1:
        candidates = ", ".join(lst["name"] for lst in partial)
        raise ClickUpError(f"No list named exactly '{list_name}'. Did you mean one of: {candidates}?")

    raise ClickUpError(f"No list named '{list_name}' found in the workspace.")


async def _fetch_all_folders() -> list[dict]:
    team_id = await resolve_team_id()
    spaces_data = await _get_json(f"/team/{team_id}/space")
    spaces = spaces_data.get("spaces") or []

    async def folders_for_space(space: dict) -> list[dict]:
        data = await _get_json(f"/space/{space['id']}/folder")
        return [{"id": str(f["id"]), "name": f["name"]} for f in data.get("folders") or []]

    results = await asyncio.gather(*(folders_for_space(s) for s in spaces))
    return [folder for group in results for folder in group]


async def resolve_folder_id(folder_name: str) -> str:
    folders = await _fetch_all_folders()
    target = folder_name.strip().lower()

    exact = [f for f in folders if f["name"].strip().lower() == target]
    if len(exact) == 1:
        return exact[0]["id"]
    if len(exact) > 1:
        candidates = ", ".join(f"{m['name']} ({m['id']})" for m in exact)
        raise ClickUpError(f"Multiple folders named '{folder_name}' exist. Candidates: {candidates}")

    partial = [f for f in folders if target in f["name"].strip().lower()]
    if len(partial) == 1:
        return partial[0]["id"]
    if len(partial) > 1:
        candidates = ", ".join(f["name"] for f in partial)
        raise ClickUpError(f"No folder named exactly '{folder_name}'. Did you mean one of: {candidates}?")

    raise ClickUpError(f"No folder named '{folder_name}' found in the workspace.")


def _flatten_kb_pages(pages: list[dict], doc_name: str, out: list[dict]) -> None:
    for page in pages:
        out.append(
            {
                "doc": doc_name,
                "page": page.get("name"),
                "content": (page.get("content") or "")[:_KB_CONTENT_CHARS],
            }
        )
        sub_pages = page.get("pages") or []
        if sub_pages:
            _flatten_kb_pages(sub_pages, doc_name, out)


async def _fetch_kb_pages() -> list[dict]:
    settings = get_settings()
    team_id = await resolve_team_id()
    folder_id = await resolve_folder_id(settings.clickup_kb_folder_name)

    docs_data = await _get_json_v3(
        f"/workspaces/{team_id}/docs",
        params={"parent_id": folder_id, "parent_type": "FOLDER", "limit": 100},
    )
    docs = docs_data.get("docs") or [] if isinstance(docs_data, dict) else []

    pages_results = await asyncio.gather(
        *(
            _get_json_v3(f"/workspaces/{team_id}/docs/{doc['id']}/pages", params={"content_format": "text/md"})
            for doc in docs
        )
    )

    flattened: list[dict] = []
    for doc, pages_data in zip(docs, pages_results):
        pages = pages_data if isinstance(pages_data, list) else (pages_data.get("pages") or [])
        _flatten_kb_pages(pages, doc["name"], flattened)
    return flattened


def _kb_cache_valid() -> bool:
    return _kb_task is not None and time.time() < _kb_expires_at


async def search_knowledge_base(query: str | None = None) -> dict:
    global _kb_task, _kb_expires_at
    if not _kb_cache_valid():
        _kb_task = asyncio.ensure_future(_fetch_kb_pages())
        _kb_expires_at = time.time() + _TREE_TTL_SECONDS
    try:
        pages = await _kb_task
    except Exception:
        _kb_task = None
        raise

    if query:
        needle = query.strip().lower()
        pages = [p for p in pages if needle in (p["page"] or "").lower() or needle in p["content"].lower()]

    truncated = len(pages) > _MAX_RESULTS
    return {"results": pages[:_MAX_RESULTS], "truncated": truncated}


async def resolve_assignee_id(assignee: str, list_id: str | None = None) -> int:
    target = assignee.strip().lower()
    members = await _get_team_members()
    for member in members:
        if str(member.get("username", "")).strip().lower() == target:
            return int(member["id"])
        if str(member.get("email", "")).strip().lower() == target:
            return int(member["id"])

    if list_id:
        list_members = await _get_json(f"/list/{list_id}/member")
        for member in list_members.get("members", []):
            if str(member.get("email", "")).strip().lower() == target:
                return int(member["id"])
            if str(member.get("username", "")).strip().lower() == target:
                return int(member["id"])

    known = ", ".join(str(m.get("username", "?")) for m in members) or "none found"
    raise ClickUpError(f"Could not resolve assignee '{assignee}'. Known workspace members: {known}")


def iso_to_unix_ms(iso_date: str) -> int:
    try:
        parsed = datetime.fromisoformat(iso_date)
    except ValueError as exc:
        raise ClickUpError(f"Invalid ISO 8601 date '{iso_date}': {exc}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def priority_to_int(priority: str) -> int:
    key = priority.strip().lower()
    if key not in PRIORITY_MAP:
        raise ClickUpError(f"Unknown priority '{priority}'. Must be one of {list(PRIORITY_MAP)}")
    return PRIORITY_MAP[key]


def _task_url(task: dict) -> str:
    return task.get("url") or f"https://app.clickup.com/t/{task.get('id')}"


def project_task(raw: dict) -> dict:
    assignees = [a.get("username") for a in raw.get("assignees", []) if a.get("username")]
    status = raw.get("status")
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "status": status.get("status") if isinstance(status, dict) else status,
        "assignees": assignees,
        "due_date": raw.get("due_date"),
        "url": _task_url(raw),
    }


async def search_tasks(
    list_name: str | None = None,
    query: str | None = None,
    assignee: str | None = None,
    overdue_only: bool = False,
    include_closed: bool = False,
) -> dict:
    params: dict = {"include_closed": str(bool(include_closed)).lower()}
    list_id = None
    if list_name:
        list_id = await resolve_list_id(list_name)
        path = f"/list/{list_id}/task"
    else:
        team_id = await resolve_team_id()
        path = f"/team/{team_id}/task"

    if assignee:
        assignee_id = await resolve_assignee_id(assignee, list_id=list_id)
        params["assignees[]"] = [assignee_id]
    if overdue_only:
        params["due_date_lt"] = str(int(time.time() * 1000))

    data = await _get_json(path, params=params)
    raw_tasks = data.get("tasks") or []

    if query:
        needle = query.strip().lower()
        raw_tasks = [t for t in raw_tasks if needle in (t.get("name") or "").lower()]

    projected = [project_task(t) for t in raw_tasks]
    truncated = len(projected) > _MAX_RESULTS
    return {"tasks": projected[:_MAX_RESULTS], "truncated": truncated}


async def create_task(
    list_name: str,
    name: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
) -> dict:
    list_id = await resolve_list_id(list_name)
    body: dict = {"name": name}
    if description:
        body["description"] = description
    if due_date:
        body["due_date"] = iso_to_unix_ms(due_date)
    if priority:
        body["priority"] = priority_to_int(priority)
    if assignee:
        assignee_id = await resolve_assignee_id(assignee, list_id=list_id)
        body["assignees"] = [assignee_id]

    response = await _request("POST", f"/list/{list_id}/task", json=body)
    if response.status_code >= 400:
        raise ClickUpError(
            f"ClickUp API error {response.status_code} creating task: {response.text[:300]}",
            response.status_code,
        )
    raw = response.json()
    return {"id": raw.get("id"), "name": raw.get("name"), "url": _task_url(raw)}


async def ping_clickup() -> tuple[bool, str | None]:
    try:
        response = await _request("GET", "/team")
        if response.status_code == 200:
            return True, None
        return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
