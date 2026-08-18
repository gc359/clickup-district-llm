from typing import Literal

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class TraceEntry(BaseModel):
    tool: str
    ok: bool
    ms: int


class ChatResponse(BaseModel):
    text: str
    trace: list[TraceEntry]
    stopped_reason: Literal["complete", "max_steps", "error"]


class HealthResponse(BaseModel):
    ollama: bool
    clickup: bool
    ollama_detail: str | None = None
    clickup_detail: str | None = None


class TicketRequest(BaseModel):
    name: str
    email: str | None = None
    building: str | None = None
    room: str | None = None
    category: Literal[
        "Hardware",
        "Software",
        "Network / WiFi",
        "Account / Password",
        "Printer",
        "Phone",
        "Other",
    ]
    description: str


class TicketResponse(BaseModel):
    id: str
    url: str
    status: Literal["created"] = "created"
