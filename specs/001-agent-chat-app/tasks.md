---
description: "Task list for agent chat app implementation"
---

# Tasks: Agent Chat App

**Input**: Design documents from `/specs/001-agent-chat-app/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: One integration test for `GET /status` (plan.md boundary test). No custom AG-UI SSE parser tests. Chat validation via quickstart manual/E2E scenarios.

**Organization**: Tasks grouped by user story. Native AG-UI integration only — no custom protocol bridge.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3)

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **Root**: `Makefile`, `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold projects and shared dev commands

- [ ] T001 Create `backend/` layout per plan.md (`backend/pyproject.toml`, `backend/src/`, `backend/tests/integration/`)
- [ ] T002 Scaffold `frontend/` via `npx assistant-ui@latest create frontend --example with-ag-ui` (or equivalent files matching with-ag-ui structure)
- [ ] T003 [P] Create root `Makefile` with targets: `install`, `dev-backend`, `dev-frontend`, `dev`, `test`, `health`, `lint`
- [ ] T004 [P] Add `frontend/.env.example` with `NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Agno AgentOS + AGUI backend serving native `/agui` and `/status` — **no custom chat routes**

**⚠️ CRITICAL**: No user story work until this phase completes

- [ ] T005 Add `backend/pyproject.toml` with `agno[os,agui]` and model provider (e.g. `openai`) dependencies managed by uv
- [ ] T006 Implement `backend/src/app.py` — Agno cookbook AGUI pattern: `Agent` + `AgentOS(agents=[...], interfaces=[AGUI(agent=...)])` + `agent_os.get_app()`
- [ ] T007 Configure agent `instructions` for language-follow-input in `backend/src/app.py` (FR-002a)
- [ ] T008 Enable CORS for `http://localhost:3000` on AgentOS FastAPI app in `backend/src/app.py`
- [ ] T009 Wire `make dev-backend` in `Makefile` to run `agent_os.serve(app="app:app", reload=True)` on port 7777

**Checkpoint**: `curl http://localhost:7777/status` returns 200; `POST /agui` exists (AGUI built-in — do not add custom routes)

---

## Phase 3: User Story 1 - 串流對話 (Priority: P1) 🎯 MVP

**Goal**: Web UI sends Traditional Chinese messages; assistant-ui displays streaming agent replies in a single thread via native AG-UI wire-up.

**Independent Test**: Open page → input 繁體中文 → send → observe reply streams incrementally (quickstart VS-2).

### Implementation for User Story 1

- [ ] T010 [US1] Trim `frontend/` scaffold: remove multi-thread UI, thread list adapter, tools demo routes (v1 single thread only)
- [ ] T011 [US1] Wire `HttpAgent` to `process.env.NEXT_PUBLIC_AGUI_AGENT_URL` (full `/agui` URL) in frontend runtime provider file
- [ ] T012 [US1] Configure `useAgUiRuntime({ agent })` without custom protocol code in frontend runtime provider file
- [ ] T013 [US1] Set fixed AG-UI `threadId` to `global-v1` in frontend runtime provider (FR-003a/b global thread)
- [ ] T014 [US1] Render `AssistantRuntimeProvider` + scaffold `Thread` in `frontend/src/app/page.tsx`
- [ ] T015 [US1] Ensure stream cancel on new message via `useAgUiRuntime` / `HttpAgent` abort (FR-004a) in frontend runtime provider
- [ ] T016 [US1] Add empty/whitespace input guard on composer in `frontend/src/components/assistant-ui/` (edge case)
- [ ] T017 [US1] Wire `make dev-frontend` in `Makefile` to start Next.js dev server

**Checkpoint**: VS-2, VS-3, VS-4 pass manually — multi-turn context, streaming, cancel-on-new-message

---

## Phase 4: User Story 2 - 服務健康檢查 (Priority: P2)

**Goal**: Checkable `GET /status` endpoint — HTTP process alive only (no LLM probe).

**Independent Test**: `make health` or `curl /status` → 200 + parseable JSON within 2s (quickstart VS-1).

### Implementation for User Story 2

- [ ] T018 [P] [US2] Implement `backend/tests/integration/test_status.py` — assert `GET /status` returns 200 and parseable JSON body
- [ ] T019 [US2] Implement `make health` in `Makefile` curling `http://localhost:7777/status`
- [ ] T020 [US2] Wire `make test` in `Makefile` to run `pytest backend/tests/integration/test_status.py`

**Checkpoint**: VS-1 passes; FR-006 satisfied without custom health router (use AGUI built-in `/status`)

---

## Phase 5: User Story 3 - 可設定的 Backend 位址 (Priority: P3)

**Goal**: Frontend backend URL configurable via environment variable without code changes.

**Independent Test**: Change `NEXT_PUBLIC_AGUI_AGENT_URL`, restart frontend only, requests hit new backend (quickstart VS-5).

### Implementation for User Story 3

- [ ] T021 [US3] Verify no hardcoded backend URL in `frontend/` — only `NEXT_PUBLIC_AGUI_AGENT_URL` in runtime provider
- [ ] T022 [US3] Document env var and restart requirement in `frontend/.env.example` and root `README.md`

**Checkpoint**: VS-5 passes — 100% requests to configured backend (SC-003)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, CI, end-to-end validation

- [ ] T023 [P] Add root `README.md` with prerequisites, env vars, and all `make` commands (Principle X)
- [ ] T024 [P] Add `.github/workflows/ci.yml` running `make test` and `make lint` (same as local)
- [ ] T025 Run quickstart.md validation scenarios VS-1 through VS-7 and note results in `specs/001-agent-chat-app/quickstart.md` Notes section
- [ ] T026 [P] Add backend connection error UX check — user sees feedback within 5s when backend down (SC-005, VS-6)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — MVP
- **US2 (Phase 4)**: Depends on Phase 2 — can parallel with US1 after T006 (status endpoint exists)
- **US3 (Phase 5)**: Depends on US1 frontend runtime (T011) — env wiring
- **Polish (Phase 6)**: Depends on US1–US3 for full quickstart validation

### User Story Dependencies

- **US1 (P1)**: Requires Foundational — no dependency on US2/US3
- **US2 (P2)**: Requires Foundational only — independently testable via curl/pytest
- **US3 (P3)**: Requires US1 frontend wiring — independently testable via env change

### Parallel Opportunities

- Phase 1: T003 + T004 in parallel after T001/T002 started
- Phase 2: sequential (single `app.py` file)
- After Phase 2: US2 tasks T018–T020 can run parallel with US1 frontend tasks T010–T017
- Phase 6: T023 + T024 + T026 in parallel

---

## Parallel Example: User Story 1

```bash
# After Phase 2 complete, frontend trim + wiring can proceed in parallel files:
Task T010: Trim scaffold in frontend/
Task T011: HttpAgent env URL in runtime provider
Task T014: page.tsx Thread render
```

---

## Parallel Example: User Story 2 + US1

```bash
# Backend status test does not block frontend work:
Task T018: backend/tests/integration/test_status.py
Task T010: frontend scaffold trim
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (AgentOS + AGUI — **do not add custom routes**)
3. Complete Phase 3: US1 frontend wire-up
4. **STOP and VALIDATE**: quickstart VS-2 (繁體中文串流)

### Incremental Delivery

1. Setup + Foundational → backend `/status` + `/agui` live
2. US1 → MVP chat demo
3. US2 → automated health test + `make health`
4. US3 → env documentation + verification
5. Polish → CI + full quickstart pass

### Do NOT Implement (plan rev 2)

- Custom FastAPI SSE or chat REST endpoints
- `frontend/src/lib/config.ts` URL builder
- `test_agui_stream.py` hand-parsing AG-UI events
- `contracts/ag-ui.openapi.yaml` duplicate schemas
- Database, auth, RAG, tools, file upload, production deploy

---

## Task Summary

| Phase | Story | Task IDs | Count |
|-------|-------|----------|-------|
| Setup | — | T001–T004 | 4 |
| Foundational | — | T005–T009 | 5 |
| US1 串流對話 | P1 | T010–T017 | 8 |
| US2 健康檢查 | P2 | T018–T020 | 3 |
| US3 Backend 位址 | P3 | T021–T022 | 2 |
| Polish | — | T023–T026 | 4 |
| **Total** | | **T001–T026** | **26** |

**Suggested MVP scope**: Phases 1–3 (T001–T017) — delivers streaming Traditional Chinese chat via native AG-UI.
