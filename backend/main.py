from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import agent
import clickup
import llm
import store
from config import get_settings
from schemas import ChatRequest, ChatResponse, HealthResponse, TicketRequest, TicketResponse

app = FastAPI(title="Local ClickUp Agent")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    history = store.get_history(req.session_id)
    result = await agent.run_agent(req.message, history, max_steps=settings.max_steps)
    store.set_history(req.session_id, result["messages"])
    return ChatResponse(
        text=result["text"],
        trace=result["trace"],
        stopped_reason=result["stopped_reason"],
    )


@app.post("/api/ticket", response_model=TicketResponse)
async def create_ticket(req: TicketRequest) -> TicketResponse:
    task_name = f"[{req.category}] {req.name} — {req.building or 'Unknown Building'} Rm {req.room or 'N/A'}"
    description = "\n".join(
        [
            f"Requester: {req.name}",
            f"Email: {req.email or 'N/A'}",
            f"Building: {req.building or 'N/A'}",
            f"Room: {req.room or 'N/A'}",
            f"Category: {req.category}",
            "",
            req.description,
        ]
    )
    try:
        task = await clickup.create_task(
            list_name=settings.clickup_ticket_list_name,
            name=task_name,
            description=description,
        )
    except clickup.ClickUpError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return TicketResponse(id=task["id"], url=task["url"], status="created")


@app.post("/api/chat", response_model=ChatResponse)
async def public_chat(req: ChatRequest) -> ChatResponse:
    key = f"public:{req.session_id}"
    history = store.get_history(key)
    result = await agent.run_public_agent(req.message, history, max_steps=settings.max_steps)
    store.set_history(key, result["messages"])
    return ChatResponse(
        text=result["text"],
        trace=result["trace"],
        stopped_reason=result["stopped_reason"],
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    ollama_ok, ollama_detail = await llm.is_reachable()
    clickup_ok, clickup_detail = await clickup.ping_clickup()
    return HealthResponse(
        ollama=ollama_ok,
        clickup=clickup_ok,
        ollama_detail=ollama_detail,
        clickup_detail=clickup_detail,
    )
