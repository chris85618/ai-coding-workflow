# Skill: 工作流恢復協議

> **觸發條件**：Phase 0 偵測到 `docs/workflow-state.md` 存在
> **輸入**：workflow-state.md、docs/adr/、docs/iteration-log.md
> **輸出**：恢復確認 + 繼續工作流

---

## Step 1: 載入狀態

1. 讀取 `docs/workflow-state.md` → 取得 pipeline_position
2. 讀取所有 `docs/adr/ADR-GATE-*.md` → 取得已通過閘門
3. 讀取 `docs/adr/` 中各 ADR → 取得變更歷史與教訓
4. 讀取 `docs/iteration-log.md` → 取得迭代歷史

## Step 2: 判定恢復點

1. 取得 `current = state.pipeline_position`
2. 列出 `completed_gates`（status == Accepted 的 ADR-GATE）
3. 列出 `pending_escalations`

## Step 3: 組裝恢復摘要

組裝以下資訊：
- pipeline_id
- current_position
- completed_phases（已通過的閘門）
- pending_work（WBS 樹中待執行的 leaf）
- pending_escalations
- last_hitl_decision（iteration-log 最後一筆 HITL 決策）
- last_updated

## Step 4: 呈現摘要並與使用者確認

向使用者呈現：
- 「偵測到既有工作流狀態。」
- 「當前位置：{current_position}」
- 「已通過閘門：{completed_gates}」
- 「待處理工作：{pending_work}」
- 若有 pending_escalations → 「⚠️ 有未處理的上報：{pending_escalations}」

使用者選擇：
- **[1] 從斷點繼續**
- **[2] 使用者有其他指令**（記錄後再回到工作流）
- **[3] 重置工作流**（需確認）

## Step 5: 執行恢復

- 若 [1]：
  - 有 pending_escalations → 優先處理 ESCALATION
  - current 在 Stage 3-8 → 從該 Stage 的 Step A 開始新一輪迭代，載入 iteration-log 歷史作為上下文
  - 其他 → 從 current_position 的下一個 WBS leaf 開始
- 若 [2]：記錄使用者指令 → 執行 → 完成後回到 Step 4 重新確認
- 若 [3]：歸檔 workflow-state.md → `docs/archive/` → 從 Phase 0 重新開始

---

## DbC 安全契約

**前置條件（Precondition）**：
1. `docs/workflow-state.md` 存在且可讀取
2. `docs/adr/` 目錄可存取
3. Session 尚未執行任何 Stage 推進動作

**不變量（Invariant）**：
1. 已通過的 HITL 閘門不可重做（ADR-GATE Accepted 的決策不重新要求確認）
2. 未通過的 HITL 閘門不可跳過（必須從當前 Stage 繼續）
3. 進行中的迭代安全重啟（從 Step A 重啟，人類決策已持久化為 ADR）
4. ESCALATION 優先（有未處理的上報必須先解決）

**後置條件（Postcondition）**：
1. Pipeline 從正確斷點恢復，position 未倒退 [INV-001]
2. 所有已通過的 Gate 狀態保持不變
3. 使用者已確認恢復方式（[1]/[2]/[3]）
4. 恢復摘要已呈現，進行中的上報已標記
