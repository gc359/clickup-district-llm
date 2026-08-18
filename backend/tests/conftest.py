import json
from pathlib import Path

import httpx
import pytest

import clickup

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


@pytest.fixture
def workspace_data():
    return load_fixture("workspace.json")


@pytest.fixture
def tasks_data():
    return load_fixture("tasks.json")


@pytest.fixture
def kb_data():
    return load_fixture("kb.json")


def build_workspace_handler(
    workspace,
    tasks=None,
    created_task=None,
    status_overrides=None,
    call_counts=None,
    docs=None,
    doc_pages=None,
):
    tasks = tasks if tasks is not None else {"tasks": []}
    status_overrides = status_overrides or {}
    docs = docs if docs is not None else {"docs": []}
    doc_pages = doc_pages or {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method
        if call_counts is not None:
            call_counts[f"{method} {path}"] = call_counts.get(f"{method} {path}", 0) + 1

        override = status_overrides.get(f"{method} {path}")
        if override is not None:
            return override

        if method == "GET" and path == "/api/v2/team":
            return httpx.Response(200, json=workspace["team"])
        if method == "GET" and path == "/api/v2/team/9000/space":
            return httpx.Response(200, json=workspace["spaces"])
        for space_id, data in workspace["folderless_lists"].items():
            if method == "GET" and path == f"/api/v2/space/{space_id}/list":
                return httpx.Response(200, json=data)
        for space_id, data in workspace["folders"].items():
            if method == "GET" and path == f"/api/v2/space/{space_id}/folder":
                return httpx.Response(200, json=data)
        for folder_id, data in workspace["folder_lists"].items():
            if method == "GET" and path == f"/api/v2/folder/{folder_id}/list":
                return httpx.Response(200, json=data)
        if method == "GET" and path == "/api/v2/team/9000/task":
            return httpx.Response(200, json=tasks)
        if path.startswith("/api/v2/list/") and path.endswith("/task"):
            if method == "GET":
                return httpx.Response(200, json=tasks)
            if method == "POST":
                return httpx.Response(
                    200,
                    json=created_task
                    or {"id": "new1", "name": "New Task", "url": "https://app.clickup.com/t/new1"},
                )
        if path.startswith("/api/v2/list/") and path.endswith("/member"):
            return httpx.Response(200, json={"members": []})
        if method == "GET" and path == "/api/v3/workspaces/9000/docs":
            return httpx.Response(200, json=docs)
        for doc_id, pages in doc_pages.items():
            if method == "GET" and path == f"/api/v3/workspaces/9000/docs/{doc_id}/pages":
                return httpx.Response(200, json=pages)

        return httpx.Response(404, json={"err": f"unmocked path {method} {path}"})

    return handler


@pytest.fixture
def make_clickup_client(workspace_data, tasks_data):
    made = []

    def _make(
        workspace=None,
        tasks=None,
        created_task=None,
        status_overrides=None,
        call_counts=None,
        docs=None,
        doc_pages=None,
    ):
        handler = build_workspace_handler(
            workspace or workspace_data,
            tasks=tasks if tasks is not None else tasks_data,
            created_task=created_task,
            status_overrides=status_overrides,
            call_counts=call_counts,
            docs=docs,
            doc_pages=doc_pages,
        )
        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(base_url=clickup.BASE_URL, transport=transport)
        clickup.reset_state_for_tests(client=client)
        made.append(client)
        return client

    yield _make
    for client in made:
        pass  # AsyncClient close is best-effort; test process exits shortly after


@pytest.fixture(autouse=True)
def _reset_clickup_state():
    clickup.reset_state_for_tests()
    yield
    clickup.reset_state_for_tests()
