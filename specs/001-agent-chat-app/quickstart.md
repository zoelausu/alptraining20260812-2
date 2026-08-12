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
export BACKEND_BASE_URL=http://localhost:7777

# Frontend — full AG-UI endpoint URL (assistant-ui convention)
export NEXT_PUBLIC_AGUI_AGENT_URL=http://localhost:7777/agui
```

Health check uses `BACKEND_BASE_URL` (same backend as chat):

```bash
curl -sS "${BACKEND_BASE_URL}/status"
# or
make health
```

## Commands (Makefile)

| Command | Purpose |
|---------|---------|
| `make install` | Install deps |
| `make dev-backend` | `agent_os.serve()` on :7777 |
| `make dev-frontend` | Next dev server |
| `make dev` | Both |
| `make health` | `curl ${BACKEND_BASE_URL}/status` |
| `make test` | `test_status.py` (200 + JSON + <2s) |

## Run

```bash
make install
make dev-backend    # terminal 1
make dev-frontend   # terminal 2
```

Open `http://localhost:3000`.

## Validation scenarios

| ID | Scenario | How |
|----|----------|-----|
| VS-1 | Health | `make health` → 200, parseable JSON, <2s |
| VS-2 | 繁體中文串流 | UI: 輸入中文 → 觀察逐步回覆 |
| VS-3 | 多輪上下文 | UI: 兩輪對話 + 「剛才說什麼」 |
| VS-4 | 串流中送新訊息 | UI: 長回覆中再送 → 前一則取消 |
| VS-5 | Env 換 backend | 改 `BACKEND_BASE_URL` + `NEXT_PUBLIC_AGUI_AGENT_URL`，重啟 frontend；`make health` 與聊天皆指向新 backend |
| VS-6 | Backend 離線 | 停 backend → UI 5s 內錯誤 |
| VS-7 | 刷新頁面 | UI 清空; backend 記憶體仍保留 |
| VS-8 | 串流中斷連線 | 串流進行中停 backend → UI 顯示可理解的中斷/錯誤（非無限等待） |
| VS-9 | 長內容捲動 | 極長回覆時 Thread 可捲動檢視完整內容 |

## References (source of truth — do not duplicate)

- AG-UI protocol: https://github.com/ag-ui-protocol/ag-ui
- assistant-ui AG-UI: https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart
- Agno AGUI: https://docs.agno.com/agent-os/interfaces/ag-ui/introduction
- Pinned versions: [contracts/versions.json](./contracts/versions.json)
- Example repo: https://github.com/assistant-ui/assistant-ui/tree/main/examples/with-ag-ui

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS | Enable CORS on AgentOS for `localhost:3000` |
| No stream | Check `OPENAI_API_KEY`, `/agui` URL in env |
| Wrong backend | Sync `BACKEND_BASE_URL` and `NEXT_PUBLIC_AGUI_AGENT_URL` to same host/port |
| Health fails | `echo $BACKEND_BASE_URL` then `curl $BACKEND_BASE_URL/status` |
