# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 (rev. 2) | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`

**User stack directive**: assistant-ui (frontend), Agno SDK + AgentOS with AGUI (backend).

## Summary

A **native AG-UI wire-up** — no custom protocol layer, no SSE bridge, no message translation middleware.

| Side | Use as-is | Do NOT build |
|------|-----------|--------------|
| **Backend** | Agno `AgentOS` + `AGUI` interface → `POST /agui`, `GET /status` | Custom FastAPI chat routes, hand-rolled SSE, `/agents/{id}/stream` adapter for UI |
| **Frontend** | assistant-ui `HttpAgent` + `useAgUiRuntime` + `Thread` | Custom chat components, fetch-to-SSE parser, REST chat API client |
| **Protocol** | [ag-ui-protocol](https://github.com/ag-ui-protocol/ag-ui) (both sides speak it) | Duplicate OpenAPI/event schemas, custom event types |

v1 scope unchanged: Traditional Chinese chat, streaming replies, single global thread, health endpoint, env-configurable agent URL. No login, DB, RAG, tools, uploads, or production deploy.

## Integration Strategy (core)

```text
assistant-ui Thread
    → useAgUiRuntime (built-in AG-UI adapter)
    → HttpAgent (@ag-ui/client)
    → POST /agui (SSE, ag-ui-protocol events)
    → Agno AGUI interface (built-in)
    → AgentOS Agent (in-memory session)
```

**Scaffold from official examples, then trim:**

1. **Frontend**: `npx assistant-ui@latest create frontend --example with-ag-ui` — already wires `HttpAgent` + `useAgUiRuntime` + `Thread`. We only change env URL and remove multi-thread UI if present.
2. **Backend**: Agno cookbook `05_agent_os/16_agui` pattern — `AgentOS(agents=[...], interfaces=[AGUI(agent=...)])`. One file, no extra routers.

**Spec-only customizations** (configuration, not new wheels):

- Fixed `threadId` / session for global thread (via AG-UI `RunAgentInput` or Agno session — use what the protocol already carries).
- Agent `instructions` for language-follow-input.
**Env configuration** (FR-007, SC-003):

| Env var | Example | Used by |
|---------|---------|---------|
| `BACKEND_BASE_URL` | `http://localhost:7777` | `make health`, `test_status.py`, docs |
| `NEXT_PUBLIC_AGUI_AGENT_URL` | `http://localhost:7777/agui` | Frontend `HttpAgent` |

Both MUST target the same backend instance.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript / Node 20+ (frontend)

**Primary Dependencies**:
- Backend: `agno[os,agui]` + Vercel AI Gateway via Agno `OpenAILike` (OpenAI-compatible Chat Completions API)
- Frontend: `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, `@ag-ui/client` (via with-ag-ui scaffold)

**LLM configuration** (no direct OpenAI):

| Env var | Default | Purpose |
|---------|---------|---------|
| `AI_GATEWAY_API_KEY` | — | Vercel AI Gateway credential |
| `AI_GATEWAY_BASE_URL` | `https://ai-gateway.vercel.sh/v1` | Gateway OpenAI-compatible base URL |
| `AI_GATEWAY_MODEL_ID` | `google/gemini-3.5-flash-lite` | Model slug passed to gateway |

**Storage**: None — Agno agent in-memory session; assistant-ui runtime holds UI state

**Testing**: `curl /status`; manual/E2E quickstart scenarios; **no custom AG-UI event parser tests** (protocol owned by libraries)

**Target Platform**: Local dev; browser + single AgentOS process

**Project Type**: Web app — two runtimes (browser + Python), one protocol

**Constraints**: Single global thread; cancel-on-new-message via runtime defaults; health = `GET /status` only

## Constitution Check

*GATE: PASS*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. No distribute by default | Justified | Browser + AgentOS = independent compute; one backend process, no extra services |
| II. Deletion over extension | **Strong pass** | Rev 2 removes custom URL builders, custom stream tests, redundant contract schemas |
| III. Explicit deps | Pass | Env vars only; no hidden singletons |
| IV. Contract at boundary | Pass | `contracts/versions.json` pins upstream protocol/package versions |
| V. Test plumbing | Pass | Test `/status` boundary; E2E for chat; don't mock AG-UI libraries |
| VI. Structured Events | Pass | T008: backend structured logs with `thread_id`/`run_id` on AGUI runs (v1 local dev scope) |
| X. Commands | Pass | Makefile targets; `BACKEND_BASE_URL` for health/test |

## Project Structure

### Documentation

```text
specs/001-agent-chat-app/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/README.md          # points to ag-ui-protocol + Agno docs
└── tasks.md                       # /speckit-tasks
```

### Source Code (minimal custom code)

```text
backend/
├── pyproject.toml
├── src/
│   └── app.py                     # Agno cookbook AGUI pattern (~30 lines)
└── tests/
    └── integration/
        └── test_status.py         # GET /status only

frontend/                          # scaffolded from with-ag-ui example
├── .env.example                   # NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui
├── src/
│   ├── app/page.tsx               # Thread + RuntimeProvider
│   └── components/assistant-ui/   # from scaffold (Thread, etc.)
└── package.json

Makefile
```

**Deleted from prior plan (do not implement)**:
- `frontend/src/lib/config.ts` — URL builder; use env URL directly in `HttpAgent`
- `test_agui_stream.py` — parsing AG-UI SSE by hand; use browser E2E or trust protocol libs
- Custom `runtime-provider.tsx` **protocol/SSE logic** — allowed: scaffold wiring + env + fixed `threadId` + stream cancel + connection error handlers (no custom AG-UI event parsing)

## Complexity Tracking

| Item | Justification |
|------|---------------|
| frontend + backend | User-mandated stacks; browser cannot run Agno |
| ~~AG-UI protocol layer~~ | **Not custom** — provided by Agno AGUI + assistant-ui react-ag-ui |

## Phase 0 & Phase 1 Artifacts

| Artifact | Path |
|----------|------|
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| Contracts | [contracts/README.md](./contracts/README.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

## Implementation Checklist (for `/speckit-tasks`)

### Backend — copy Agno pattern, configure agent

```python
# backend/src/app.py — pattern from Agno AG-UI docs / cookbook 16_agui
import os

from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

chat_agent = Agent(
    model=OpenAILike(
        id=os.environ["AI_GATEWAY_MODEL_ID"],  # google/gemini-3.5-flash-lite
        api_key=os.environ["AI_GATEWAY_API_KEY"],
        base_url=os.environ.get("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1"),
    ),
    instructions="Respond in the same language the user uses.",
)

agent_os = AgentOS(agents=[chat_agent], interfaces=[AGUI(agent=chat_agent)])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="app:app", reload=True)
```

No additional routes. Health = `GET /status` (AGUI built-in). Chat = `POST /agui` (AGUI built-in).

### Frontend — copy assistant-ui pattern, set env

```tsx
// From with-ag-ui example — only env + single-thread trim
const agent = useMemo(
  () =>
    new HttpAgent({
      url: process.env.NEXT_PUBLIC_AGUI_AGENT_URL!, // full URL, e.g. http://localhost:7777/agui
    }),
  [],
);
const runtime = useAgUiRuntime({ agent });
```

Use scaffold `Thread` component. Do **not** add `threadList` adapter (single thread). Stream cancel on new message: use `useAgUiRuntime` default behavior / `onCancel` from scaffold if already present.

### Global thread (spec FR-003a/b)

Use AG-UI `threadId` consistently (e.g. constant `global-v1` in `HttpAgent` / runtime options if scaffold exposes it). Agno AGUI passes thread context to agent session — **do not** build a separate in-memory message store on top.

## Next Step

Run **`/speckit-tasks`** to generate tasks aligned with this minimal integration plan.
