# Research: Agent Chat App

**Feature**: `001-agent-chat-app`  
**Date**: 2026-08-12

## Decision 1: Frontend — assistant-ui with AG-UI runtime

**Decision**: Use `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, and `@ag-ui/client` (`HttpAgent`) as the chat UI and streaming transport.

**Rationale**:
- Spec requires streaming chat UI with Traditional Chinese input/display.
- assistant-ui provides production-ready Thread/composer components and streaming message rendering.
- `@assistant-ui/react-ag-ui` implements the AG-UI protocol adapter (`useAgUiRuntime`), matching Agno's native `AGUI` interface.
- Official reference: [assistant-ui AG-UI quickstart](https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart) and [with-ag-ui example](https://github.com/assistant-ui/assistant-ui/tree/main/examples/with-ag-ui).

**Alternatives considered**:
- Custom React chat from scratch — rejected; duplicates streaming/state handling assistant-ui already solves.
- Direct `POST /agents/{id}/stream` without AG-UI — rejected; assistant-ui AG-UI runtime is the user-requested stack and aligns with Agno's `AGUI` interface.

## Decision 2: Backend — Agno SDK + AgentOS with AGUI interface

**Decision**: Run `AgentOS` with `interfaces=[AGUI(agent=chat_agent)]`, default port `7777`.

**Rationale**:
- User explicitly requested agno SDK and AgentOS.
- `AGUI` exposes `POST /agui` (SSE streaming) and `GET /status` (health) per [Agno AG-UI docs](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction).
- AgentOS provides FastAPI server, agent lifecycle, and optional session APIs without adding a separate database for v1.
- Install: `uv pip install 'agno[os,agui]'` (plus model provider package, e.g. `openai`).

**Alternatives considered**:
- Raw FastAPI custom SSE endpoint — rejected; loses AgentOS agent management and AG-UI compliance.
- AgentOS without AGUI + custom bridge — rejected; assistant-ui expects AG-UI protocol.

## Decision 3: Frontend ↔ Backend protocol — AG-UI over HTTP SSE

**Decision**: Frontend `HttpAgent` targets `{BACKEND_URL}/agui` with `Accept: text/event-stream`.

**Rationale**:
- Agno mounts AG-UI at `POST /agui` by default (root prefix).
- assistant-ui `HttpAgent` speaks AG-UI events (`TEXT_MESSAGE_*`, etc.) natively.
- Health check uses `GET /status` on the same AGUI router (interface-level status).

**Alternatives considered**:
- AgentOS native `/agents/{id}/stream` — rejected for frontend; assistant-ui AG-UI runtime does not target that endpoint without custom adapter.

## Decision 4: Single global thread (v1 session model)

**Decision**: Use one fixed Agno session identifier (`session_id="global-v1"`) for all agent runs; disable multi-thread UI in assistant-ui (single thread, no thread list).

**Rationale**:
- Spec clarification: single global backend thread, no per-user/per-tab isolation.
- Agno `run_agent` / AG-UI `RunAgentInput` supports `session_id` for in-memory conversation history on the agent side.
- Frontend refresh clears UI only; backend retains history until process restart (spec assumption).

**Alternatives considered**:
- No session_id (stateless per request) — rejected; violates FR-003a (full context on each message).
- Per-browser session_id — rejected; spec chose global shared thread (clarify session 2026-08-12).

## Decision 5: Stream cancellation on new message

**Decision**: Use assistant-ui runtime cancel/abort when user submits while streaming; frontend aborts in-flight `HttpAgent` request and sends new `POST /agui` run.

**Rationale**:
- Spec FR-004a: new message aborts current stream and starts new turn.
- `useAgUiRuntime` supports `onCancel`; `HttpAgent` fetch can be aborted via `AbortController`.

**Alternatives considered**:
- Disable input during stream — rejected; contradicts clarify answer C.

## Decision 6: Backend URL configuration

**Decision**: Frontend reads `NEXT_PUBLIC_AGUI_BACKEND_URL` (base URL, e.g. `http://localhost:7777`); construct AG-UI URL as `${BASE}/agui` and status URL as `${BASE}/status`.

**Rationale**:
- Meets FR-007 (env-configurable without code change).
- Matches assistant-ui convention (`NEXT_PUBLIC_AGUI_AGENT_URL` in examples); we use base URL + fixed paths for clarity and contract versioning.

## Decision 7: Language follow input

**Decision**: Configure agent system instructions to respond in the same language as the user message; no separate locale UI.

**Rationale**:
- FR-002a / clarify session: follow input language.
- Implemented via Agno `Agent` instructions, not frontend i18n.

## Decision 8: Health check scope

**Decision**: Use `GET /status` from AGUI interface; success = HTTP 200 with parseable JSON body. Do not probe LLM connectivity.

**Rationale**:
- Matches spec clarify answer A and FR-006.
- Agno documents `GET /status` on AGUI router.

## Decision 9: Project layout and tooling

**Decision**: Monorepo with `backend/` (Python/uv) and `frontend/` (Next.js/pnpm); root `Makefile` listing all commands for Principle X.

**Rationale**:
- Constitution Principle X: discoverable commands, local matches CI.
- Web app naturally splits browser UI and Python agent server (independent compute: browser vs agent runtime).

## Decision 10: Testing strategy

**Decision**:
- Integration: `curl`/`httpx` against `/status` and `/agui` (contract tests).
- Frontend: Playwright or manual quickstart scenarios (boundary tests).
- Unit: pure helpers only (message validation, URL builder).

**Rationale**:
- Constitution Principle V: test boundaries, not mock owned plumbing.

## Resolved NEEDS CLARIFICATION

All technical context items resolved; no open unknowns for Phase 1.
