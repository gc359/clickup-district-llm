import json
from datetime import datetime, timezone

import llm
import tools

SYSTEM_PROMPT_TEMPLATE = """You are a ClickUp workspace assistant for "{workspace_name}", running locally.
Today's date is {today} ({weekday}).

Rules:
1. Never guess, recall, or invent a space, folder, list, or task ID. Always call
   list_workspace first if you need one — IDs go stale and hallucinated IDs cause
   silent failures.
2. Tool arguments take human names (list names, assignee names/emails), never IDs.
3. Before calling create_task, confirm the details with the user in plain language
   UNLESS their request is already an unambiguous, fully-specified instruction
   (e.g. "create a task called X in list Y, due Friday, high priority" needs no
   confirmation; "we should probably track that" does).
4. If a tool returns an error, don't retry the same call blindly — read the error,
   adjust (e.g. resolve an ambiguous list name), or tell the user what went wrong.
5. Never claim an action succeeded unless a tool call actually returned success.
6. Be concise. Do not narrate your tool-calling process to the user; report results.
7. Write in plain conversational text only — no Markdown, anywhere in the message,
   including inside list items. Never wrap any word or phrase in ** or _ for emphasis,
   not even a step's title — write step titles as plain text with no special
   formatting at all. Do not use #-style headers, tables, horizontal rules, or
   emoji-numbered headings. Do not use "•" or "–" as bullet characters. Keep lists
   flat, one level only — never nest a sub-list or indented sub-bullet under a
   numbered item. If a step has more than one action, either fold them into the
   same line separated by "; " or give each action its own top-level numbered
   line. For step-by-step instructions, use plain numbered lines ("1. Do this
   thing: detail.") or a hyphen "- " per bullet — nothing fancier.

You have three tools: list_workspace, search_tasks, create_task. Nothing else is
possible in this MVP — no deleting, archiving, or editing existing tasks."""

_MAX_TOOL_RESULT_CHARS = 4000

_PUBLIC_SYSTEM_PROMPT_TEMPLATE = """You are "Helpdesk Hero," the AI tech-support assistant for Bloomfield
Technology Department's public helpdesk widget. Today's date is {today} ({weekday}).

Rules:
1. You can look up existing helpdesk tickets with search_helpdesk_tickets. You cannot create,
   edit, or close tickets — you have no tool for that. If the user wants to submit a new ticket,
   tell them to use the "Submit a ticket" option in this chat, which opens a form.
2. search_helpdesk_tickets takes no required arguments. If the user asks a general question
   like "are there any open tickets" or "what's in the queue" — with no specific keyword or
   person in mind — call it with no arguments at all; that lists every open ticket. Only pass
   query/assignee when the user actually named a keyword or a specific person. Never refuse or
   ask the user to narrow down before trying an unfiltered call first.
3. Never invent a ticket ID, status, or assignee. If search_helpdesk_tickets returns nothing
   relevant, say so plainly.
4. Be concise and friendly. Do not narrate tool-calling; report results.
5. You cannot see or discuss anything about the district's broader ClickUp workspace — only
   helpdesk tickets.
6. Write in plain conversational text only — no Markdown, anywhere in the message,
   including inside list items. Never wrap any word or phrase in ** or _ for emphasis,
   not even a step's title — write step titles as plain text with no special
   formatting at all. Do not use #-style headers, tables, horizontal rules, or
   emoji-numbered headings. Do not use "•" or "–" as bullet characters. Keep lists
   flat, one level only — never nest a sub-list or indented sub-bullet under a
   numbered item. If a step has more than one action, either fold them into the
   same line separated by "; " or give each action its own top-level numbered
   line. For step-by-step instructions, use plain numbered lines ("1. Do this
   thing: detail.") or a hyphen "- " per bullet — nothing fancier."""


async def _build_system_prompt() -> dict:
    workspace_name = await tools.get_workspace_name()
    now = datetime.now(timezone.utc)
    content = SYSTEM_PROMPT_TEMPLATE.format(
        workspace_name=workspace_name,
        today=now.strftime("%Y-%m-%d"),
        weekday=now.strftime("%A"),
    )
    return {"role": "system", "content": content}


async def _build_public_system_prompt() -> dict:
    now = datetime.now(timezone.utc)
    content = _PUBLIC_SYSTEM_PROMPT_TEMPLATE.format(
        today=now.strftime("%Y-%m-%d"),
        weekday=now.strftime("%A"),
    )
    return {"role": "system", "content": content}


def _truncate(text: str) -> str:
    if len(text) <= _MAX_TOOL_RESULT_CHARS:
        return text
    return text[:_MAX_TOOL_RESULT_CHARS] + "... [truncated]"


async def run_agent(
    message: str,
    history: list[dict],
    max_steps: int = 5,
    tool_schemas: list[dict] | None = None,
    execute_fn=None,
    build_system_prompt=None,
) -> dict:
    """Run the bounded tool-calling loop.

    Never raises — always returns {text, trace, stopped_reason, messages}, where
    `messages` is the updated conversation the caller should persist.

    `tool_schemas`/`execute_fn`/`build_system_prompt` let callers swap in a
    restricted tool surface (see `run_public_agent`) without forking this loop.
    Resolved here rather than as default-argument values so they're re-evaluated
    per call instead of bound once at import/def time.
    """
    tool_schemas = tool_schemas if tool_schemas is not None else tools.TOOL_SCHEMAS
    execute_fn = execute_fn if execute_fn is not None else tools.execute
    build_system_prompt = build_system_prompt if build_system_prompt is not None else _build_system_prompt

    trace: list[dict] = []
    try:
        messages = list(history)
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, await build_system_prompt())
        messages.append({"role": "user", "content": message})

        for _ in range(max_steps):
            assistant_message = await llm.chat(messages, tools=tool_schemas)
            messages.append(assistant_message)
            tool_calls = assistant_message.get("tool_calls") or []

            if not tool_calls:
                return {
                    "text": assistant_message.get("content", "") or "",
                    "trace": trace,
                    "stopped_reason": "complete",
                    "messages": messages,
                }

            for call in tool_calls:
                function = call.get("function", {})
                name = function.get("name", "")
                arguments = function.get("arguments") or {}
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                outcome = await execute_fn(name, arguments)
                trace.append({"tool": name, "ok": outcome["ok"], "ms": outcome["ms"]})

                payload = outcome["result"] if outcome["ok"] else {"error": outcome["error"]}
                messages.append({"role": "tool", "content": _truncate(json.dumps(payload))})

        return {
            "text": "I wasn't able to finish that within the allotted steps. Could you narrow the request?",
            "trace": trace,
            "stopped_reason": "max_steps",
            "messages": messages,
        }
    except Exception as exc:
        return {
            "text": f"Something went wrong: {exc}",
            "trace": trace,
            "stopped_reason": "error",
            "messages": history,
        }


async def run_public_agent(message: str, history: list[dict], max_steps: int = 5) -> dict:
    """Run the bounded tool-calling loop for the anonymous public helpdesk widget.

    Uses `tools.PUBLIC_TOOL_SCHEMAS`/`tools.execute_public` — a registry that
    structurally excludes list_workspace/create_task, not a runtime permission
    check. Never reveals the internal workspace name.
    """
    return await run_agent(
        message,
        history,
        max_steps=max_steps,
        tool_schemas=tools.PUBLIC_TOOL_SCHEMAS,
        execute_fn=tools.execute_public,
        build_system_prompt=_build_public_system_prompt,
    )
