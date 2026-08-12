# Contracts: Agent Chat App

**Do not redefine the AG-UI protocol here.** Both assistant-ui and Agno implement the same upstream specification.

## Pinned versions (Constitution Principle IV)

See [versions.json](./versions.json) for pinned package/protocol versions used in v1.

| Component | Pin location | Notes |
|-----------|--------------|-------|
| `@ag-ui/client` | `versions.json` | Frontend AG-UI client |
| `@assistant-ui/react-ag-ui` | `versions.json` | assistant-ui runtime adapter |
| `agno[os,agui]` | `versions.json` | Backend AgentOS + AGUI |

Update `versions.json` when upgrading dependencies; do not maintain parallel OpenAPI by hand.

## Source of truth

| Contract | Owner | URL |
|----------|-------|-----|
| AG-UI wire protocol (SSE events, `RunAgentInput`) | ag-ui-protocol | https://github.com/ag-ui-protocol/ag-ui |
| Agno AGUI endpoints | Agno | https://docs.agno.com/agent-os/interfaces/ag-ui/introduction |
| assistant-ui client | assistant-ui | https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart |

## Endpoints used by this feature (Agno AGUI — built-in, not custom)

| Method | Path | Purpose | Spec ref |
|--------|------|---------|----------|
| `POST` | `/agui` | AG-UI agent run (SSE stream) | FR-003, FR-004 |
| `GET` | `/status` | HTTP process health | FR-006 |

Default base: `http://localhost:7777` (`BACKEND_BASE_URL` or `AGENT_OS_PORT`).

## Environment configuration

| Env var | Example | Purpose |
|---------|---------|---------|
| `NEXT_PUBLIC_AGUI_AGENT_URL` | `http://localhost:7777/agui` | Frontend `HttpAgent.url` — full chat endpoint |
| `BACKEND_BASE_URL` | `http://localhost:7777` | Health check, `make health`, integration tests — backend root (no path) |
| `AI_GATEWAY_API_KEY` | `vck_...` | Vercel AI Gateway credential (backend only) |
| `AI_GATEWAY_BASE_URL` | `https://ai-gateway.vercel.sh/v1` | Gateway OpenAI-compatible base URL |
| `AI_GATEWAY_MODEL_ID` | `google/gemini-3.5-flash-lite` | Model slug routed through gateway |

`BACKEND_BASE_URL` and `NEXT_PUBLIC_AGUI_AGENT_URL` MUST target the same backend instance (SC-003, FR-007). LLM config is pinned in [versions.json](./versions.json) `llm` section.

## v1 spec constraints on the protocol (configuration only)

- **Single global thread**: fixed `threadId` (`global-v1`) in AG-UI runs — no custom API.
- **Health scope**: `/status` success = HTTP alive; no LLM check in health response.
- **Cancel stream**: client aborts in-flight AG-UI request; no custom backend cancel route required.

## Removed

`ag-ui.openapi.yaml` partial redefinition was removed in plan rev 2. Use `versions.json` + upstream docs instead.
