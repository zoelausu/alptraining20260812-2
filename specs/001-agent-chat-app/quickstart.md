# Quickstart: Agent Chat App

**Feature**: `001-agent-chat-app`  
**Integration**: Native AG-UI — assistant-ui ↔ Agno AGUI (no custom bridge)

## Prerequisites

- Node.js 20+, pnpm
- Python 3.11+, uv
- `OPENAI_API_KEY` (if using OpenAI model in Agno agent)

## Scaffold (recommended — don't start from scratch)

**Frontend** (official AG-UI example):

```bash
npx assistant-ui@latest create frontend --example with-ag-ui
```

**Backend** (Agno AG-UI cookbook pattern — single `app.py`):

Follow [Agno AG-UI introduction](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction) or cookbook `05_agent_os/16_agui`.

Trim scaffold to v1 scope: remove multi-thread UI, tools demo, extra example routes.

## Environment

```bash
# Backend
export OPENAI_API_KEY=sk-...
export AGENT_OS_PORT=7777

# Frontend — full AG-UI endpoint URL (assistant-ui convention)
export NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui
```

Health check (separate from chat client):

```bash
curl -sS http://localhost:7777/status
```

## Commands (Makefile)

| Command | Purpose |
|---------|---------|
| `make install` | Install deps |
| `make dev-backend` | `agent_os.serve()` on :7777 |
| `make dev-frontend` | Next dev server |
| `make dev` | Both |
| `make health` | `curl /status` |
| `make test` | `test_status.py` only |

## Run

```bash
make install
make dev-backend    # terminal 1
make dev-frontend   # terminal 2
```

Open `http://localhost:3000`.

## Validation scenarios

Same as spec — verify through **UI + curl**, not custom protocol code:

| ID | Scenario | How |
|----|----------|-----|
| VS-1 | Health | `make health` → 200, parseable JSON |
| VS-2 | 繁體中文串流 | UI: 輸入中文 → 觀察逐步回覆 |
| VS-3 | 多輪上下文 | UI: 兩輪對話 + 「剛才說什麼」 |
| VS-4 | 串流中送新訊息 | UI: 長回覆中再送 → 前一則取消 |
| VS-5 | Env 換 backend | 改 `NEXT_PUBLIC_AGUI_AGENT_URL`, 重啟 frontend |
| VS-6 | Backend 離線 | 停 backend → UI 5s 內錯誤 |
| VS-7 | 刷新頁面 | UI 清空; backend 記憶體仍保留 |

## References (source of truth — do not duplicate)

- AG-UI protocol: https://github.com/ag-ui-protocol/ag-ui
- assistant-ui AG-UI: https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart
- Agno AGUI: https://docs.agno.com/agent-os/interfaces/ag-ui/introduction
- Example repo: https://github.com/assistant-ui/assistant-ui/tree/main/examples/with-ag-ui

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS | Enable CORS on AgentOS for `localhost:3000` |
| No stream | Check `OPENAI_API_KEY`, `/agui` URL in env |
| Wrong backend | `NEXT_PUBLIC_AGUI_AGENT_URL` must be **full** `/agui` URL |
