# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`

**User stack directive**: assistant-ui (frontend), Agno SDK + AgentOS with AGUI interface (backend).

## Summary

Build a local-dev agent chat app: users send Traditional Chinese messages in a web UI and receive **streaming** agent replies in a **single global thread**. Backend is **Agno AgentOS** exposing the **AGUI** interface (`POST /agui`, `GET /status`). Frontend is **assistant-ui** connected via **AG-UI protocol** (`HttpAgent` + `useAgUiRuntime`). No login, database, RAG, tools, uploads, or production deployment in v1.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript / Node 20+ (frontend)

**Primary Dependencies**:
- Backend: `agno[os,agui]`, model provider (e.g. `openai`), `uvicorn`
- Frontend: `next`, `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, `@ag-ui/client`

**Storage**: None (in-memory Agno session `global-v1`; no database)

**Testing**: `pytest` + `httpx` (backend integration/contract), `make health` smoke, manual/Playwright UI scenarios per quickstart

**Target Platform**: Local development (Linux/macOS); browser for UI

**Project Type**: Web application (frontend + backend)

**Performance Goals**: Health &lt; 2s; error feedback &lt; 5s; first stream token visible within normal LLM latency (SC-001/SC-005)

**Constraints**: Single global thread; stream cancel on new message; env-configurable backend URL; health = HTTP only

**Scale/Scope**: Single developer local use; one concurrent active stream; no multi-user isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design | Notes |
|-----------|------------|-------------|-------|
| I. Do Not Distribute by Default | **Justified split** | **Justified** | Two runtimes: browser UI + Python AgentOS. Justification: genuinely independent compute (browser cannot host Agno agent). Not arbitrary microservices—one backend process + static/dev frontend. Documented in Complexity Tracking. |
| II. Optimize for Deletion | Pass | Pass | Thin `backend/src/app.py`, minimal frontend wrapper around assistant-ui primitives. |
| III. Explicit Dependencies | Pass | Pass | `HttpAgent` URL from env; agent model/key from env; no hidden globals. |
| IV. Contract at Boundary | Pass | Pass | `contracts/ag-ui.openapi.yaml` + ag-ui-protocol at `/agui`. |
| V. Test Transformation | Pass | Pass | Integration tests on `/status` and `/agui` boundary; no mocking owned HTTP layer in unit tests. |
| VI. Structured Events | Partial | Partial | v1: use Agno structured logging where available; defer full observability stack (local dev scope). |
| VII. Recovery | Pass | Pass | No DB migrations; revert = stop processes + git checkout. |
| VIII. Attention Finite | N/A | N/A | No production alerts in v1 scope. |
| IX. Value at User | Pass | Pass | quickstart defines deploy-to-browser validation. |
| X. Commands Discoverable | Pass | Pass | Root `Makefile` with `install`, `dev`, `test`, `health`, `lint`. |

**Gate result**: PASS (with documented Principle I justification).

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-chat-app/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── ag-ui.openapi.yaml
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── src/
│   └── app.py           # AgentOS + AGUI + chat agent definition
└── tests/
    ├── integration/
    │   ├── test_health.py
    │   └── test_agui_stream.py

frontend/
├── package.json
├── next.config.ts
├── .env.example
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   └── assistant-ui/
│   │       └── thread.tsx
│   └── lib/
│       ├── runtime-provider.tsx   # HttpAgent + useAgUiRuntime
│       └── config.ts              # NEXT_PUBLIC_AGUI_BACKEND_URL

Makefile                 # install, dev, test, health, lint
.github/workflows/ci.yml # same make targets as local
```

**Structure Decision**: Standard web split (`frontend/` + `backend/`) chosen because assistant-ui requires a Node/React build and Agno AgentOS requires Python. Single Makefile at root for Principle X.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two runtimes (frontend + backend) | Browser UI vs Python agent runtime are independent compute units | Single-process cannot run Agno AgentOS inside the browser; embedding UI in Python (e.g. only Dojo) rejects user-mandated assistant-ui |
| AG-UI protocol layer | assistant-ui AG-UI runtime requires protocol-compliant endpoint | Direct `/agents/stream` would need custom assistant-ui adapter; user chose assistant-ui + Agno AGUI path |

## Phase 0 Output

See [research.md](./research.md) — all NEEDS CLARIFICATION resolved.

## Phase 1 Output

| Artifact | Path |
|----------|------|
| Data model | [data-model.md](./data-model.md) |
| Contracts | [contracts/ag-ui.openapi.yaml](./contracts/ag-ui.openapi.yaml) |
| Quickstart | [quickstart.md](./quickstart.md) |

### Implementation notes (for `/speckit-tasks`)

**Backend (`backend/src/app.py`)**:
```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses  # or configured model
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

chat_agent = Agent(
    id="chat-agent",
    name="Chat Agent",
    model=OpenAIResponses(id="gpt-4o"),  # configure per env
    instructions="Respond in the same language the user uses.",
    # session history via fixed session_id in AG-UI runs
)

agent_os = AgentOS(
    agents=[chat_agent],
    interfaces=[AGUI(agent=chat_agent)],
)
app = agent_os.get_app()
```

Serve: `agent_os.serve(app="app:app", reload=True)` on port 7777.

**Frontend (`runtime-provider.tsx`)**:
- `const base = process.env.NEXT_PUBLIC_AGUI_BACKEND_URL`
- `new HttpAgent({ url: `${base}/agui`, headers: { Accept: "text/event-stream" } })`
- `useAgUiRuntime({ agent, onCancel: abort logic })`
- Single thread UI — no `threadList` adapter.

**Session**: Pass fixed `threadId` / session `global-v1` in AG-UI runs per data-model.

## Next Step

Run **`/speckit-tasks`** to generate actionable implementation tasks from this plan and spec.
