# Agent Chat App

Simple agent chat: assistant-ui frontend + Agno AgentOS/AGUI backend (native AG-UI protocol).

## Backend (implemented)

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

### Environment

Copy `backend/.env.example` to `backend/.env` and set:

| Variable | Example | Purpose |
|----------|---------|---------|
| `AI_GATEWAY_API_KEY` | `vck_...` | Vercel AI Gateway credential |
| `AI_GATEWAY_BASE_URL` | `https://ai-gateway.vercel.sh/v1` | Gateway OpenAI-compatible base URL |
| `AI_GATEWAY_MODEL_ID` | `google/gemini-3.5-flash-lite` | Model routed through gateway |
| `AGENT_OS_PORT` | `7777` | AgentOS listen port |
| `BACKEND_BASE_URL` | `http://localhost:7777` | Health check / tests (backend root) |

Chat uses `POST /agui` and health uses `GET /status` (Agno AGUI built-in).

### Commands

| Command | Purpose |
|---------|---------|
| `make install` | Install backend dependencies |
| `make dev-backend` | Start AgentOS on `AGENT_OS_PORT` |
| `make health` | `curl ${BACKEND_BASE_URL}/status` |
| `make test` | Run `pytest` (in-process `/status` tests) |
| `make lint` | Python compile check |

### Run backend

```bash
make install
export AI_GATEWAY_API_KEY=vck_...
make dev-backend
make health
```

## Frontend (pending)

Run `/speckit-implement` for frontend tasks (T010–T017). When frontend exists, set `NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui` to match `BACKEND_BASE_URL` (same host/port; SC-003).

## Spec

See `specs/001-agent-chat-app/`.
