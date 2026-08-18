# Local ClickUp Agent (MVP)

A chat UI for managing a ClickUp workspace in natural language via a locally-hosted
Ollama model. See `clickup-agent-mvp-prd.md` for the full spec. No conversation
content or workspace data leaves the machine except calls made directly to
ClickUp's REST API.

```
React SPA (:5173) → FastAPI backend (:8000) → Ollama (:11434)
                                             → ClickUp REST API
```

## Deployment note

This was built on a separate dev machine with no Ollama installed. It's meant to
run entirely on one machine (e.g. a Mac Studio with Ollama installed) — the
backend, frontend, and Ollama should all end up on the same host `localhost`
loop per the PRD's non-goals (no deployment beyond a single machine).

## Backend setup

```
cd backend
python -m venv .venv
./.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip
cp .env.example .env                             # then fill in CLICKUP_TOKEN
./.venv/bin/uvicorn main:app --reload --port 8000
```

Required in `.env`:

- `CLICKUP_TOKEN` — your ClickUp personal API token (`pk_...`). Never commit `.env`.
- `CLICKUP_TEAM_ID` — optional; resolved automatically from `/team` if left blank.
- `OLLAMA_HOST` — defaults to `http://localhost:11434`.
- `OLLAMA_MODEL` — defaults to `gpt-oss-safeguard`. This is a safety/policy
  classification fine-tune, not a model built for agentic tool-calling — if the
  agent frequently hits `stopped_reason: "max_steps"` or produces malformed tool
  calls, switch this to `qwen3:32b` (or another tool-call-tuned model already
  pulled in Ollama) and restart the backend. No code changes needed either way.
- `MAX_STEPS` — agent loop iteration cap, default `5`.
- `CORS_ORIGINS` — comma-separated list, defaults to `http://localhost:5173`.

Run tests: `./.venv/bin/pytest -q` (uses mocked HTTP/LLM calls — no live Ollama
or ClickUp token required).

## Frontend setup

```
cd frontend
npm install
cp .env.example .env      # VITE_API_BASE, defaults to http://localhost:8000
npm run dev                # http://localhost:5173
```

Run tests: `npm test`. Build for production: `npm run build`.

## First run checklist (on the machine that actually has Ollama + a ClickUp token)

1. `ollama pull <model in OLLAMA_MODEL>` and confirm `ollama list` shows it.
2. Start the backend, then `curl http://localhost:8000/health` — expect
   `{"ollama": true, "clickup": true}`. If either is `false`, the response also
   includes `ollama_detail` / `clickup_detail` explaining why (e.g. a connection
   error means Ollama isn't reachable at `OLLAMA_HOST`; an `HTTP 401` on the
   ClickUp side means `CLICKUP_TOKEN` is missing or invalid).
3. From a Python REPL in `backend/`, sanity-check the three ClickUp functions
   directly against the real workspace: `clickup.list_workspace()`,
   `clickup.search_tasks(...)`, `clickup.create_task(...)` (PRD milestone M0).
4. Start the frontend and run the PRD §13 acceptance prompts end-to-end in the
   browser.
