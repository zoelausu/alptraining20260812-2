# Quickstart: Agent Chat App

**Feature**: `001-agent-chat-app`  
**Stack**: assistant-ui (frontend) + Agno AgentOS + AGUI (backend)

## Prerequisites

- Node.js 20+ and pnpm
- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- OpenAI API key (or other model provider configured for Agno agent)

## Environment

### Backend

```bash
export OPENAI_API_KEY=sk-...          # if using OpenAIResponses model
export AGENT_OS_HOST=0.0.0.0
export AGENT_OS_PORT=7777
```

### Frontend

```bash
# Base URL of AgentOS (no trailing slash)
export NEXT_PUBLIC_AGUI_BACKEND_URL=http://localhost:7777
```

Frontend constructs:
- Chat: `{NEXT_PUBLIC_AGUI_BACKEND_URL}/agui`
- Health: `{NEXT_PUBLIC_AGUI_BACKEND_URL}/status`

## Commands (from repo root)

| Command | Purpose |
|---------|---------|
| `make install` | Install backend + frontend dependencies |
| `make dev-backend` | Start AgentOS with AGUI on :7777 |
| `make dev-frontend` | Start Next.js dev server |
| `make dev` | Start both (backend + frontend) |
| `make test` | Run backend integration + frontend checks |
| `make health` | Curl backend `/status` |
| `make lint` | Lint backend and frontend |

Local and CI MUST invoke the same `make` targets (Constitution Principle X).

## Setup

```bash
git clone <repo>
cd <repo>
make install
```

## Run locally

**Terminal 1 — backend**

```bash
make dev-backend
```

**Terminal 2 — frontend**

```bash
export NEXT_PUBLIC_AGUI_BACKEND_URL=http://localhost:7777
make dev-frontend
```

Open the frontend URL (typically `http://localhost:3000`).

## Validation scenarios

### VS-1: Health endpoint (User Story 2)

```bash
make health
# or
curl -sS http://localhost:7777/status
```

**Expected**: HTTP 200 within 2s, JSON with parseable `status` field (e.g. `"ok"`).  
**Not required**: LLM connectivity check.

### VS-2: Streaming chat — Traditional Chinese (User Story 1)

1. Open chat UI in browser.
2. Type `你好，請用繁體中文自我介紹` and send.
3. Observe user message appears immediately.
4. Observe assistant reply **streams** token-by-token (not all at once at end).

**Expected**: SC-001, SC-004, SC-006 satisfied.

### VS-3: Multi-turn context (Clarify Q1)

1. Send: `我最喜歡的顏色是藍色`
2. After reply completes, send: `我剛才說我最喜歡什麼顏色？`

**Expected**: Assistant references blue from prior turn (backend global session memory).

### VS-4: Cancel stream on new message (Clarify Q2)

1. Send a message that produces a long reply.
2. While streaming, send a new message.

**Expected**: Prior stream stops (cancelled/incomplete in UI); new reply streams for new message only.

### VS-5: Backend URL via env (User Story 3)

1. Stop backend on :7777; start second instance on :8888 (if supported) OR change `AGENT_OS_PORT`.
2. Set `NEXT_PUBLIC_AGUI_BACKEND_URL` to new base URL; restart frontend only.
3. Send a chat message.

**Expected**: Request hits the configured backend (verify via logs or health on that port).

### VS-6: Backend unreachable (Edge case)

1. Stop backend.
2. Send message from UI.

**Expected**: User sees understandable error within 5s (SC-005).

### VS-7: Page refresh (Edge case)

1. Complete a conversation.
2. Refresh browser.

**Expected**: UI empty; backend still has global session until process restart.

## Contract references

- OpenAPI: [contracts/ag-ui.openapi.yaml](./contracts/ag-ui.openapi.yaml)
- Data model: [data-model.md](./data-model.md)
- AG-UI protocol: https://github.com/ag-ui-protocol/ag-ui

## Troubleshooting

| Symptom | Check |
|---------|--------|
| CORS errors | AgentOS / FastAPI CORS for frontend origin |
| Stream never starts | `OPENAI_API_KEY`, model config, backend logs |
| Wrong backend | `NEXT_PUBLIC_AGUI_BACKEND_URL`, restart frontend after change |
| Health fails | `curl localhost:7777/status`, backend process running |
