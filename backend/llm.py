import httpx

from config import get_settings


def _to_ollama_tools(tool_schemas: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"],
            },
        }
        for schema in tool_schemas
    ]


async def chat(messages: list[dict], tools: list[dict], temperature: float = 0.1) -> dict:
    """Call Ollama's /api/chat and return the parsed assistant message."""
    settings = get_settings()
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "tools": _to_ollama_tools(tools),
        "stream": False,
        "options": {"temperature": min(temperature, 0.1)},
    }
    async with httpx.AsyncClient(base_url=settings.ollama_host, timeout=120.0) as client:
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
    return data.get("message", {"role": "assistant", "content": ""})


async def is_reachable() -> tuple[bool, str | None]:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(base_url=settings.ollama_host, timeout=5.0) as client:
            response = await client.get("/api/tags")
            if response.status_code == 200:
                return True, None
            return False, f"HTTP {response.status_code} from {settings.ollama_host}/api/tags"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
