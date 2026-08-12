# Data Model: Agent Chat App

**Feature**: `001-agent-chat-app`  
**Date**: 2026-08-12

## Overview

v1 uses **in-memory only** data on the backend (Agno agent session) and **ephemeral UI state** on the frontend. No database entities. Contracts are defined at HTTP boundaries (AG-UI protocol + status endpoint).

## Entities

### Message (logical)

Represents one utterance in the chat thread.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string | yes | Unique within UI session (AG-UI message id or client-generated) |
| `role` | enum | yes | `user` \| `assistant` |
| `content` | string | yes | UTF-8 text; supports Traditional Chinese and other Unicode |
| `status` | enum | optional | `complete` \| `streaming` \| `cancelled` \| `error` |
| `created_at` | timestamp | optional | UI ordering only in v1 |

**Validation**:
- User messages MUST NOT be empty or whitespace-only (FR edge case).
- No max length enforced in v1 spec; recommend soft limit 32k chars in implementation with user-visible error.

**Lifecycle**:
1. User submits → `user` message `complete`.
2. Assistant reply starts → `assistant` message `streaming`.
3. Stream completes → `complete`; user aborts/new message → `cancelled`; failure → `error`.

**Persistence**: Frontend messages lost on page refresh. Backend history retained in Agno session until process restart.

### Chat Thread (logical)

Single global conversation container for v1.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string | yes | Fixed value `global-v1` for all backend runs |
| `messages` | ordered Message[] | yes | Append-only in normal flow |

**Rules**:
- Exactly one thread in UI (FR-005).
- All HTTP clients share the same backend session id (FR-003b).
- No thread list, switch, or delete in v1.

### Agent Run (backend, Agno)

Transient execution unit per user message.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `run_id` | string | Agno / AG-UI | Correlates streaming events |
| `session_id` | string | constant `global-v1` | Binds to in-memory history |
| `message` | string | user input | Latest user utterance |
| `agent_id` | string | AgentOS config | Registered chat agent |

**State transitions**:
```
idle → running (POST /agui) → streaming → completed | cancelled | failed
```

Concurrent runs: only one active; new POST cancels prior stream (FR-004a).

### Health Status (boundary DTO)

Response from `GET /status`.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `status` | string | yes | e.g. `ok` when process alive |
| `interface` | string | optional | e.g. `agui` |

Does not include LLM or model health (spec clarify).

## Relationships

```text
Chat Thread (global-v1)
  └── Message[] (ordered)
       └── triggers Agent Run (1:1 per user message, latest wins if concurrent)

AgentOS
  └── Agent (chat_agent)
       └── Session (global-v1) holds run history in memory
```

## AG-UI Boundary Types (reference)

Frontend/backend exchange uses `ag-ui-protocol` types at `POST /agui`:

- **RunAgentInput**: `threadId`, `runId`, `messages[]`, `forwardedProps`, etc.
- **Events (SSE)**: `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`, `RUN_ERROR`, etc.

Detailed wire format: see `contracts/ag-ui.openapi.yaml` and [AG-UI protocol](https://github.com/ag-ui-protocol/ag-ui).

## Out of Scope (no entities)

- User accounts, auth tokens (beyond optional future JWT on AgentOS)
- Database tables
- File attachments
- Tool call persistence (no tools in v1)
