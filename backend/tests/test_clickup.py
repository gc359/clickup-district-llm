import asyncio

import httpx
import pytest

import clickup


async def test_list_workspace_builds_tree_with_folder_lists(make_clickup_client):
    make_clickup_client()

    spaces = await clickup.list_workspace()

    assert {s["space_name"] for s in spaces} == {"Marketing", "Engineering"}
    marketing = next(s for s in spaces if s["space_name"] == "Marketing")
    list_names = {lst["name"] for lst in marketing["lists"]}
    assert list_names == {"General", "Q3 Campaign"}  # folderless + folder list
    engineering = next(s for s in spaces if s["space_name"] == "Engineering")
    assert [lst["name"] for lst in engineering["lists"]] == ["QA"]


async def test_resolve_list_id_exact_match(make_clickup_client):
    make_clickup_client()
    list_id = await clickup.resolve_list_id("QA")
    assert list_id == "1001"


async def test_resolve_list_id_case_insensitive(make_clickup_client):
    make_clickup_client()
    list_id = await clickup.resolve_list_id("general")
    assert list_id == "1000"


async def test_resolve_list_id_not_found(make_clickup_client):
    make_clickup_client()
    with pytest.raises(clickup.ClickUpError, match="No list named"):
        await clickup.resolve_list_id("Nonexistent List")


async def test_resolve_list_id_ambiguous(make_clickup_client, workspace_data):
    workspace_data["folderless_lists"]["501"] = {"lists": [{"id": "1001", "name": "General"}]}
    make_clickup_client(workspace=workspace_data)

    with pytest.raises(clickup.ClickUpError, match="Multiple lists named"):
        await clickup.resolve_list_id("General")


async def test_resolve_folder_id_exact_match(make_clickup_client):
    make_clickup_client()
    folder_id = await clickup.resolve_folder_id("Knowledge Base")
    assert folder_id == "701"


async def test_resolve_folder_id_case_insensitive(make_clickup_client):
    make_clickup_client()
    folder_id = await clickup.resolve_folder_id("knowledge base")
    assert folder_id == "701"


async def test_resolve_folder_id_not_found(make_clickup_client):
    make_clickup_client()
    with pytest.raises(clickup.ClickUpError, match="No folder named"):
        await clickup.resolve_folder_id("Ghost Folder")


async def test_resolve_folder_id_ambiguous(make_clickup_client, workspace_data):
    workspace_data["folders"]["500"]["folders"].append({"id": "702", "name": "Knowledge Base"})
    make_clickup_client(workspace=workspace_data)

    with pytest.raises(clickup.ClickUpError, match="Multiple folders named"):
        await clickup.resolve_folder_id("Knowledge Base")


async def test_search_knowledge_base_returns_flattened_pages(make_clickup_client, kb_data):
    make_clickup_client(docs=kb_data["docs"], doc_pages=kb_data["pages"])

    result = await clickup.search_knowledge_base()

    assert result["truncated"] is False
    names = {(r["doc"], r["page"]) for r in result["results"]}
    assert names == {
        ("RingCentral KB", "Setting up RingCentral"),
        ("Network KB", "Connecting to WiFi"),
        ("Network KB", "Troubleshooting WiFi"),
    }


async def test_search_knowledge_base_query_filters_by_page_name(make_clickup_client, kb_data):
    make_clickup_client(docs=kb_data["docs"], doc_pages=kb_data["pages"])

    result = await clickup.search_knowledge_base(query="ringcentral")

    assert [r["page"] for r in result["results"]] == ["Setting up RingCentral"]


async def test_search_knowledge_base_query_matches_content(make_clickup_client, kb_data):
    make_clickup_client(docs=kb_data["docs"], doc_pages=kb_data["pages"])

    result = await clickup.search_knowledge_base(query="AD password")

    assert [r["page"] for r in result["results"]] == ["Connecting to WiFi"]


async def test_search_tasks_projects_fields(make_clickup_client):
    make_clickup_client()
    result = await clickup.search_tasks(list_name="QA")

    assert result["truncated"] is False
    assert len(result["tasks"]) == 2
    first = result["tasks"][0]
    assert set(first.keys()) == {"id", "name", "status", "assignees", "due_date", "url"}
    assert first["status"] == "open"
    assert first["assignees"] == ["jane"]


async def test_search_tasks_query_filters_by_name(make_clickup_client):
    make_clickup_client()
    result = await clickup.search_tasks(list_name="QA", query="login")
    assert [t["name"] for t in result["tasks"]] == ["Fix login redirect"]


async def test_search_tasks_caps_at_25_and_flags_truncated(make_clickup_client):
    many_tasks = {
        "tasks": [
            {"id": f"t{i}", "name": f"Task {i}", "status": {"status": "open"}, "assignees": [], "due_date": None}
            for i in range(30)
        ]
    }
    make_clickup_client(tasks=many_tasks)

    result = await clickup.search_tasks(list_name="QA")

    assert len(result["tasks"]) == 25
    assert result["truncated"] is True


async def test_create_task_converts_priority_and_date(make_clickup_client):
    created = {"id": "abc", "name": "Test task", "url": "https://app.clickup.com/t/abc"}
    make_clickup_client(created_task=created)

    result = await clickup.create_task(
        list_name="QA", name="Test task", priority="high", due_date="2026-08-14"
    )

    assert result == {"id": "abc", "name": "Test task", "url": "https://app.clickup.com/t/abc"}


async def test_create_task_unknown_list_raises(make_clickup_client):
    make_clickup_client()
    with pytest.raises(clickup.ClickUpError, match="No list named"):
        await clickup.create_task(list_name="Ghost List", name="x")


def test_iso_to_unix_ms():
    import datetime

    expected = int(datetime.datetime(2026, 8, 14, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    assert clickup.iso_to_unix_ms("2026-08-14") == expected


def test_priority_to_int_valid_and_invalid():
    assert clickup.priority_to_int("urgent") == 1
    assert clickup.priority_to_int("low") == 4
    with pytest.raises(clickup.ClickUpError):
        clickup.priority_to_int("whenever")


async def test_workspace_tree_is_cached_across_concurrent_calls(make_clickup_client):
    call_counts = {}
    make_clickup_client(call_counts=call_counts)

    results = await asyncio.gather(
        clickup.fetch_workspace_tree(),
        clickup.fetch_workspace_tree(),
        clickup.fetch_workspace_tree(),
    )

    assert results[0] == results[1] == results[2]
    assert call_counts.get("GET /api/v2/team/9000/space") == 1


async def test_rate_limit_429_retries_then_succeeds(workspace_data):
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/team":
            attempts["n"] += 1
            if attempts["n"] == 1:
                return httpx.Response(429, headers={"Retry-After": "0"}, json={"err": "rate limited"})
            return httpx.Response(200, json=workspace_data["team"])
        return httpx.Response(404)

    client = httpx.AsyncClient(base_url=clickup.BASE_URL, transport=httpx.MockTransport(handler))
    clickup.reset_state_for_tests(client=client)

    team_id = await clickup.resolve_team_id()

    assert team_id == "9000"
    assert attempts["n"] == 2


async def test_rate_limit_exhausts_retries_and_raises(workspace_data):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "0"}, json={"err": "rate limited"})

    client = httpx.AsyncClient(base_url=clickup.BASE_URL, transport=httpx.MockTransport(handler))
    clickup.reset_state_for_tests(client=client)

    with pytest.raises(clickup.ClickUpError):
        await clickup.resolve_team_id()


async def test_resolve_assignee_by_username(make_clickup_client):
    make_clickup_client()
    assignee_id = await clickup.resolve_assignee_id("jane")
    assert assignee_id == 102


async def test_resolve_assignee_unknown_raises_with_known_members(make_clickup_client):
    make_clickup_client()
    with pytest.raises(clickup.ClickUpError, match="Known workspace members"):
        await clickup.resolve_assignee_id("nobody")
