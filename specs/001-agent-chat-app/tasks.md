---
description: "Task list for agent chat app implementation"
---

# Tasks: Agent Chat App

**Input**: Design documents from `/specs/001-agent-chat-app/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: `test_status.py` for `GET /status` (200 + JSON + <2s). Chat/stream UX via quickstart VS-2–VS-9. No custom AG-UI SSE parser tests.

**Organization**: Tasks grouped by user story. Native AG-UI integration only — no custom protocol bridge.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3)

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **Root**: `Makefile`, `README.md`, `.env.example`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold projects and shared dev commands

- [X] T001 Create `backend/` directory layout only (`backend/src/`, `backend/tests/integration/`) per plan.md
- [ ] T002 Scaffold `frontend/` via `npx assistant-ui@latest create frontend --example with-ag-ui` (or equivalent files matching with-ag-ui structure)
- [X] T003 [P] Create root `Makefile` with targets: `install`, `dev-backend`, `dev-frontend`, `dev`, `test`, `health`, `lint`
- [X] T004 [P] Add root, `backend/.env.example`, and `frontend/.env.example` with `BACKEND_BASE_URL`, `NEXT_PUBLIC_AGUI_AGENT_URL`, `AI_GATEWAY_API_KEY`, `AI_GATEWAY_BASE_URL=https://ai-gateway.vercel.sh/v1`, and `AI_GATEWAY_MODEL_ID=google/gemini-3.5-flash-lite` (no `OPENAI_API_KEY`) — backend + root `.env.example` done; `frontend/.env.example` pending T002

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Agno AgentOS + AGUI backend serving native `/agui` and `/status` — **no custom chat routes**

**⚠️ CRITICAL**: No user story work until this phase completes

- [X] T005 Add `backend/pyproject.toml` with pinned `agno[os,agui]` per `contracts/versions.json` (no direct OpenAI provider dependency)
- [X] T006 Implement `backend/src/app.py` — Agno AGUI pattern with `OpenAILike` reading `AI_GATEWAY_*` env vars (default model `google/gemini-3.5-flash-lite` via gateway) + `AgentOS` + `AGUI`; MUST NOT use `OpenAIResponses` or `OPENAI_API_KEY`
- [X] T007 Configure agent `instructions` for language-follow-input in `backend/src/app.py` (FR-002a)
- [X] T008 Enable CORS for `http://localhost:3000` and structured JSON logging with `thread_id`/`run_id` fields on AGUI runs in `backend/src/app.py` (Constitution VI)
- [X] T009 Wire `make dev-backend` in `Makefile` to run `agent_os.serve(app="app:app", reload=True)` using `AGENT_OS_PORT` (default 7777)

**Checkpoint**: `curl ${BACKEND_BASE_URL}/status` returns 200; `POST /agui` exists (AGUI built-in — do not add custom routes)

---

## Phase 3: User Story 1 - 串流對話 (Priority: P1) 🎯 MVP

**Goal**: Web UI sends Traditional Chinese messages; assistant-ui displays streaming agent replies in a single thread via native AG-UI wire-up.

**Independent Test**: Open page → input 繁體中文 → send → observe reply streams incrementally (quickstart VS-2).

### Implementation for User Story 1

- [ ] T010 [US1] Trim `frontend/` scaffold: remove multi-thread UI, thread list adapter, tools demo routes (v1 single thread only)
- [ ] T011 [US1] Wire `HttpAgent` to `process.env.NEXT_PUBLIC_AGUI_AGENT_URL` (full `/agui` URL) in frontend runtime provider file
- [ ] T012 [US1] Configure `useAgUiRuntime({ agent })` without custom AG-UI event parsing in frontend runtime provider file
- [ ] T013 [US1] Set fixed AG-UI `threadId` to `global-v1` in frontend runtime provider (FR-003a/b)
- [ ] T014 [US1] Render `AssistantRuntimeProvider` + scaffold `Thread` in `frontend/src/app/page.tsx`
- [ ] T015 [US1] Handle stream cancel on new message (FR-004a) and mid-stream connection loss with user-visible error (FR-008, VS-8) via `useAgUiRuntime`/`onError` in frontend runtime provider
- [ ] T016 [US1] Add empty/whitespace input guard on composer in `frontend/src/components/assistant-ui/`
- [ ] T017 [US1] Wire `make dev-frontend` in `Makefile` to start Next.js dev server

**Checkpoint**: VS-2, VS-3, VS-4, VS-8 pass — streaming, multi-turn context, cancel-on-new-message, mid-stream disconnect UX

---

## Phase 4: User Story 2 - 服務健康檢查 (Priority: P2)

**Goal**: Checkable `GET /status` endpoint — HTTP process alive only (no LLM probe).

**Independent Test**: `make health` → 200 + parseable JSON within 2s (quickstart VS-1); backend stopped → connection failure observable (US2 scenario 2).

### Implementation for User Story 2

- [X] T018 [P] [US2] Implement `backend/tests/integration/test_status.py` — assert `GET ${BACKEND_BASE_URL}/status` returns 200, parseable JSON, and response time <2s (SC-002)
- [X] T019 [US2] Implement `make health` in `Makefile` curling `${BACKEND_BASE_URL}/status` (default `http://localhost:7777/status`, FR-007/SC-003)
- [X] T020 [US2] Wire `make test` in `Makefile` to run `pytest backend/tests/integration/test_status.py` with `BACKEND_BASE_URL` from environment

**Checkpoint**: VS-1 passes; FR-006 satisfied via AGUI built-in `/status`

---

## Phase 5: User Story 3 - 可設定的 Backend 位址 (Priority: P3)

**Goal**: Chat and health checks configurable via environment variables without code changes.

**Independent Test**: Change `BACKEND_BASE_URL` + `NEXT_PUBLIC_AGUI_AGENT_URL`, restart frontend; chat and `make health` hit new backend (quickstart VS-5).

### Implementation for User Story 3

- [X] T021 [US3] Verify no hardcoded backend URLs in `frontend/` or `Makefile` — chat via `NEXT_PUBLIC_AGUI_AGENT_URL`, health/test via `BACKEND_BASE_URL` — Makefile verified; `frontend/` pending T002
- [X] T022 [US3] Document both env vars, sync requirement, and restart steps in root `README.md` (`.env.example` already created in T004) — backend + sync note; full frontend restart steps pending T002

**Checkpoint**: VS-5 passes — chat and health 100% to configured backend (SC-003)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, CI, contracts, end-to-end validation

- [X] T023 [P] Add root `README.md` with prerequisites, env vars (`BACKEND_BASE_URL`, `NEXT_PUBLIC_AGUI_AGENT_URL`, `AI_GATEWAY_*`), and all `make` commands (Principle X) — backend section complete; frontend pending
- [X] T024 [P] Add `.github/workflows/ci.yml` running `make test` and `make lint` with `BACKEND_BASE_URL` set (same as local)
- [ ] T025 Run quickstart.md validation VS-1 through VS-9 (incl. CJK input VS-2, scroll VS-9) and note results in `specs/001-agent-chat-app/quickstart.md` Notes section
- [ ] T026 [P] Verify backend-unreachable UX — user sees feedback within 5s when backend down before/during chat (SC-005, VS-6); covered by T015 for mid-stream case
- [X] T027 [P] Verify `specs/001-agent-chat-app/contracts/versions.json` matches installed package versions in `backend/pyproject.toml` and `frontend/package.json` — backend agno 2.8.7 verified; `frontend/package.json` pending T002

**Checkpoint**: All quickstart scenarios documented; contract versions pinned

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — MVP
- **US2 (Phase 4)**: Depends on Phase 2 — parallel with US1 after T006
- **US3 (Phase 5)**: Depends on T004 (env examples), T011 (frontend wiring), T019 (health env)
- **Polish (Phase 6)**: Depends on US1–US3 for full quickstart validation

### User Story Dependencies

- **US1 (P1)**: Requires Foundational — no dependency on US2/US3
- **US2 (P2)**: Requires Foundational only — independently testable via curl/pytest
- **US3 (P3)**: Requires env scaffolding (T004) + US1/US2 wiring — independently testable via env change

### Parallel Opportunities

- Phase 1: T003 + T004 in parallel after T001/T002
- After Phase 2: US2 (T018–T020) parallel with US1 frontend (T010–T017)
- Phase 6: T023 + T024 + T026 + T027 in parallel

---

## Parallel Example: User Story 2 + US1

```bash
Task T018: backend/tests/integration/test_status.py
Task T010: frontend scaffold trim
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 → Phase 2 → Phase 3 (T001–T017)
2. **STOP and VALIDATE**: quickstart VS-2 (繁體中文串流)

### Do NOT Implement (plan rev 2)

- Custom FastAPI SSE or chat REST endpoints
- `frontend/src/lib/config.ts` URL builder
- `test_agui_stream.py` hand-parsing AG-UI events
- Hand-maintained OpenAPI duplicate of ag-ui-protocol
- Direct `OpenAIResponses` / `OPENAI_API_KEY` — use Vercel AI Gateway via `OpenAILike` only

---

## Task Summary

| Phase | Story | Task IDs | Count |
|-------|-------|----------|-------|
| Setup | — | T001–T004 | 4 |
| Foundational | — | T005–T009 | 5 |
| US1 串流對話 | P1 | T010–T017 | 8 |
| US2 健康檢查 | P2 | T018–T020 | 3 |
| US3 Backend 位址 | P3 | T021–T022 | 2 |
| Polish | — | T023–T027 | 5 |
| **Total** | | **T001–T027** | **27** |

**Suggested MVP scope**: Phases 1–3 (T001–T017)
