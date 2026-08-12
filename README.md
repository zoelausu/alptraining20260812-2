# Agent Chat App

Simple agent chat: assistant-ui frontend + Agno AgentOS/AGUI backend (native AG-UI protocol).

## Prerequisites

- Python 3.11+, [uv](https://docs.astral.sh/uv/)
- Node.js 20+, npm

## Environment

Copy examples and set values:

- `backend/.env.example` → `backend/.env`
- `frontend/.env.example` → `frontend/.env.local`

| Variable | Example | Used by |
|----------|---------|---------|
| `AI_GATEWAY_API_KEY` | `vck_...` | Backend (chat) |
| `AI_GATEWAY_BASE_URL` | `https://ai-gateway.vercel.sh/v1` | Backend |
| `AI_GATEWAY_MODEL_ID` | `google/gemini-3.5-flash-lite` | Backend |
| `AGENT_OS_PORT` | `7777` | Backend listen port |
| `BACKEND_BASE_URL` | `http://localhost:7777` | Health check, tests |
| `NEXT_PUBLIC_AGUI_AGENT_URL` | `http://localhost:7777/agui` | Frontend chat |

`BACKEND_BASE_URL` and `NEXT_PUBLIC_AGUI_AGENT_URL` must target the same backend host/port. After changing frontend env, restart the Next.js dev server.

## Commands

| Command | Purpose |
|---------|---------|
| `make install` | Install backend + frontend dependencies |
| `make dev-backend` | AgentOS on `:7777` (`POST /agui`, `GET /status`) |
| `make dev-frontend` | Next.js dev server on `:3000` |
| `make health` | `curl ${BACKEND_BASE_URL}/status` |
| `make test` | Backend `/status` pytest |
| `make lint` | Backend compile check + frontend production build |

## Run locally

```bash
make install
# set AI_GATEWAY_API_KEY in backend/.env or export
make dev-backend   # terminal 1
make dev-frontend  # terminal 2
```

Open http://localhost:3000

## Spec

See `specs/001-agent-chat-app/`.
