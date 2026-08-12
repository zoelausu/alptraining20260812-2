# Feature Specification: Agent Chat App

**Feature Branch**: `001-agent-chat-app`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "建立一個簡單的 agent chat app。使用者可在 web 介面輸入繁體中文訊息，並收到由 backend agent 串流回傳的回覆。v1 只需要單一聊天 thread；不包含登入、資料庫、RAG、tools、上傳附件或 production deployment。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 串流對話 (Priority: P1)

使用者開啟 web 介面，在輸入框以繁體中文輸入訊息並送出。系統將訊息傳給 backend agent，並在畫面上逐步顯示（串流）agent 的回覆文字，直到回覆完成。所有對話發生在同一個聊天 thread 中，使用者可連續送出多則訊息並看到對應回覆。

**Why this priority**: 這是產品的核心價值——使用者能與 agent 即時對話。沒有串流對話，其餘功能無意義。

**Independent Test**: 僅實作此故事即可展示可用的 MVP：開啟頁面、輸入繁體中文、送出、觀察回覆逐步出現。

**Acceptance Scenarios**:

1. **Given** 使用者已開啟聊天頁面且 backend 可用，**When** 使用者輸入繁體中文訊息並送出，**Then** 使用者訊息出現在對話區，且 agent 回覆以串流方式逐步顯示於同一 thread。
2. **Given** 使用者已收到一則完整回覆，**When** 使用者再次送出新訊息，**Then** 新訊息與新回覆依序追加至同一 thread，先前內容仍可見。
3. **Given** agent 正在串流回覆，**When** 回覆尚未結束，**Then** 使用者可看到回覆文字持續更新直至完成狀態。

---

### User Story 2 - 服務健康檢查 (Priority: P2)

開發者或操作者需要確認 backend 是否就緒。系統提供可檢查的 health/status endpoint，回傳明確的就緒或異常狀態，無需透過聊天介面間接推斷。

**Why this priority**: 支援本地開發與除錯；與使用者指定的 acceptance criteria 直接對應。不依賴登入或資料庫。

**Independent Test**: 直接請求 health/status endpoint，驗證就緒時回傳成功狀態、異常時回傳可辨識的失敗狀態。

**Acceptance Scenarios**:

1. **Given** backend 正常運作，**When** 請求 health/status endpoint，**Then** 回應表明服務就緒（可解析的成功狀態）。
2. **Given** backend 尚未啟動或處於不可服務狀態，**When** 請求 health/status endpoint，**Then** 回應表明非就緒或連線失敗可被檢測者辨識。

---

### User Story 3 - 可設定的 Backend 位址 (Priority: P3)

開發者需將前端指向不同的 backend（例如本機、同事機器、不同 port）。前端連線的 backend 位址必須透過 environment variable 設定，無需修改原始碼。

**Why this priority**: 滿足 acceptance criteria #3，並支援本地與團隊開發時的彈性配置。

**Independent Test**: 設定不同 environment variable 值啟動前端，驗證請求送往對應 backend（可搭配 health endpoint 或送出訊息確認）。

**Acceptance Scenarios**:

1. **Given** environment variable 指向 backend A，**When** 使用者送出訊息，**Then** 請求由 backend A 處理。
2. **Given** 僅變更 environment variable 指向 backend B（不修改程式碼），**When** 重新啟動前端並送出訊息，**Then** 請求由 backend B 處理。

---

### Edge Cases

- 使用者送出空白或僅含空白字元的訊息時，系統不應送出無效請求，並向使用者提示需輸入內容。
- Backend 在串流過程中中斷連線時，使用者應看到可理解的錯誤或中斷提示，而非無限等待。
- Backend 完全無法連線時（未啟動、位址錯誤），送出訊息後使用者應收到明確的失敗回饋。
- 使用者連續快速送出多則訊息時，回覆應與對應訊息順序一致，不應錯亂或覆蓋。
- 頁面重新整理後，v1 不保留歷史對話（無持久化）；使用者看到空的單一 thread。
- 極長訊息或極長串流回覆時，介面應可捲動檢視完整內容。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 提供 web 介面，讓使用者輸入並送出訊息。
- **FR-002**: 系統 MUST 支援使用者以繁體中文輸入訊息（輸入與顯示皆支援繁體中文文字）。
- **FR-003**: 系統 MUST 將使用者訊息傳送至 backend agent 並接收回覆。
- **FR-004**: 系統 MUST 以串流方式在 web 介面顯示 agent 回覆（逐步顯示，非僅在完成後一次顯示）。
- **FR-005**: v1 MUST 僅使用單一聊天 thread（單一連續對話區，無多 thread 切換或管理）。
- **FR-006**: Backend MUST 提供可檢查的 health/status endpoint，供外部判斷服務就緒狀態。
- **FR-007**: 前端連線的 backend 位址 MUST 透過 environment variable 設定，無需修改原始碼即可變更。
- **FR-008**: 系統 MUST 在 backend 錯誤或連線失敗時向使用者顯示可理解的回饋。
- **FR-009**: v1 MUST NOT 包含使用者登入或身份驗證。
- **FR-010**: v1 MUST NOT 使用資料庫或跨 session 持久化對話歷史。
- **FR-011**: v1 MUST NOT 包含 RAG、外部 tools 整合、檔案或附件上傳。
- **FR-012**: v1 MUST NOT 包含 production deployment 流程或相關產品化部署需求（範圍限於本地/開發用途）。

### Key Entities

- **Message**: 單則對話內容，包含角色（使用者或 agent）、文字內容、在 thread 中的順序。v1 僅存在於當前頁面 session，不持久化。
- **Chat Thread**: v1 中唯一的對話容器，依序承載使用者與 agent 的訊息。無多 thread 識別或切換。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者可在 30 秒內完成「開啟頁面 → 輸入繁體中文 → 送出 → 看到串流回覆開始出現」的完整流程。
- **SC-002**: 在 backend 正常運作時，health/status endpoint 於 2 秒內回傳可解析的就緒狀態。
- **SC-003**: 變更 frontend environment variable 後，100% 的聊天與健康檢查請求送往新設定的 backend（以可重複的驗證步驟確認）。
- **SC-004**: 串流回覆期間，使用者可在回覆完成前看到文字逐步出現（非僅在完成後一次顯示）。
- **SC-005**: Backend 無法連線時，使用者在 5 秒內收到可理解的錯誤回饋（非無限等待）。

## Assumptions

- 目標使用者為開發者或內部測試人員，在本地或開發環境使用；非對外 production 服務。
- 「Agent」指 backend 上負責產生回覆的邏輯；具體模型或供應商不在本規格範圍，由實作階段決定。
- 單一瀏覽器分頁對應單一 thread；無多使用者同時編輯同一 thread 的需求。
- 頁面重新整理後對話歷史清空為可接受行為（無資料庫）。
- 網路連線穩定足以支援串流；極端離線情境以錯誤回饋處理即可。
- 繁體中文涵蓋常用 CJK 字元顯示與輸入，無需額外語系切換功能。
- Health/status endpoint 無需認證（與 v1 無登入一致）。

## Out of Scope (v1)

- 使用者登入、註冊、權限
- 資料庫與對話持久化
- RAG、知識庫檢索
- Agent tools / 外部 API 工具呼叫
- 檔案或附件上傳
- 多聊天 thread 管理
- Production deployment、擴展性與高可用設計
