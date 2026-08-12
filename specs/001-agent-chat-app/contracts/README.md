# Contracts: Agent Chat App

**Do not redefine the AG-UI protocol here.** Both assistant-ui and Agno implement the same upstream specification.

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

Default base: `http://localhost:7777` (`AGENT_OS_PORT`).

## Frontend configuration

| Env var | Example | Purpose |
|---------|---------|---------|
| `NEXT_PUBLIC_AGUI_AGENT_URL` | `http://localhost:7777/agui` | `HttpAgent.url` — full endpoint |

## v1 spec constraints on the protocol (configuration only)

- **Single global thread**: fixed `threadId` (e.g. `global-v1`) in AG-UI runs — no custom API.
- **Health scope**: `/status` success = HTTP alive; no LLM check in health response.
- **Cancel stream**: client aborts in-flight AG-UI request; no custom backend cancel route required.

## Removed

`ag-ui.openapi.yaml` partial redefinition was removed in plan rev 2. If OpenAPI is needed later, generate from Agno's served OpenAPI or ag-ui-protocol package — do not maintain a parallel schema by hand.
