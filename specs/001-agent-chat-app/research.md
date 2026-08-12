# Research: Agent Chat App

**Feature**: `001-agent-chat-app`  
**Date**: 2026-08-12 (rev. 4)

## Decision 0: Native AG-UI integration — no custom bridge (PRIMARY)

**Decision**: Connect assistant-ui to Agno via the **AG-UI protocol end-to-end**. Use each framework's built-in AG-UI support; zero custom protocol translation.

**Rationale**:
- [Agno AGUI interface](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction) exposes `POST /agui` + `GET /status` as a standard AG-UI server.
- [assistant-ui `@assistant-ui/react-ag-ui`](https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart) provides `HttpAgent` + `useAgUiRuntime` as a standard AG-UI client.
- Both implement [ag-ui-protocol](https://github.com/ag-ui-protocol/ag-ui) — wiring them together is configuration, not engineering.

**Alternatives considered (rejected — reinventing the wheel)**:
- Custom FastAPI SSE endpoint translating to assistant-ui format — rejected.
- AgentOS `/agents/{id}/stream` + custom frontend adapter — rejected; bypasses AG-UI on both sides.
- Hand-written OpenAPI/event schemas duplicating ag-ui-protocol — rejected; reference upstream spec.
- Custom `config.ts` URL/path assembly layer — rejected; `HttpAgent.url` accepts full endpoint URL via env.

## Decision 1: Scaffold from official examples

**Decision**:
- Frontend: `npx assistant-ui@latest create frontend --example with-ag-ui`
- Backend: Agno cookbook `cookbook/05_agent_os/16_agui` / docs basic.py pattern

**Rationale**: Official examples already solve streaming, event parsing, Thread UI, and AgentOS+AGUI boot. Custom code should be diff-from-example only (env, instructions, trim thread list).

## Decision 2: Backend — AgentOS + AGUI only

**Decision**: `AgentOS(agents=[chat_agent], interfaces=[AGUI(agent=chat_agent)])`, port 7777.

**Rationale**: User-requested stack. AGUI is the Agno-native way to serve assistant-ui-compatible chat. Install: `uv pip install 'agno[os,agui]'`.

**Rejected**: AgentOS without AGUI; separate health router (use `GET /status` on AGUI).

## Decision 3: Frontend — HttpAgent points at Agno `/agui`

**Decision**: `NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui` (full URL). Health/Makefile/tests use `BACKEND_BASE_URL=http://localhost:7777` (backend root). Both MUST target the same instance (SC-003).

**Rationale**: Matches [with-ag-ui README](https://github.com/assistant-ui/assistant-ui/blob/main/examples/with-ag-ui/README.md). Separates chat client URL from health/test tooling without hardcoding host/port in Makefile.

## Decision 4: Single global thread

**Decision**: Fixed AG-UI `threadId` (e.g. `global-v1`); no `threadList` adapter; no custom session store.

**Rationale**: Spec clarify session. AG-UI protocol already models threads; Agno maintains session history for the thread — use that, don't duplicate.

## Decision 5: Stream cancellation

**Decision**: Rely on assistant-ui `useAgUiRuntime` + `HttpAgent` abort/cancel (scaffold may already implement). No custom cancel API on backend.

**Rationale**: FR-004a is a client-side abort of in-flight AG-UI run + new `POST /agui`. Protocol and runtime handle this; no Agno-specific cancel endpoint needed for v1.

## Decision 6: Language follow input

**Decision**: Agno `Agent(instructions="Respond in the same language the user uses.")` — one line, no i18n framework.

## Decision 7: Health scope

**Decision**: `GET /status` on AGUI router; HTTP 200 + parseable JSON = pass. No LLM probe.

## Decision 9: LLM — Vercel AI Gateway + Gemini Flash Lite (not OpenAI direct)

**Decision**: Backend agent uses Agno `OpenAILike` with:
- `base_url`: `https://ai-gateway.vercel.sh/v1` (`AI_GATEWAY_BASE_URL`)
- `api_key`: `AI_GATEWAY_API_KEY`
- `id`: `google/gemini-3.5-flash-lite` (`AI_GATEWAY_MODEL_ID`)

**Rationale**: User preference; Vercel AI Gateway exposes OpenAI-compatible Chat Completions API ([docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-chat-completions)). Agno has no native Gateway class yet; `OpenAILike` is the supported adapter — no custom bridge.

**Rejected**: `OpenAIResponses` + `OPENAI_API_KEY`; direct `agno.models.google.Gemini` (bypasses user's gateway billing/routing).

## Decision 10: Testing

**Decision**:
- Automated: `test_status.py` only (owned boundary we expose for spec FR-006).
- Chat/streaming: quickstart manual scenarios or Playwright against real UI — **do not** parse AG-UI SSE in pytest.

**Rationale**: Constitution V — test boundaries we own; AG-UI event stream is owned by ag-ui-protocol libraries.

## Resolved NEEDS CLARIFICATION

All items resolved. Rev 4 adds Vercel AI Gateway + Gemini Flash Lite model stack.
