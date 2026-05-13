# Skill: 工作流恢復協議

> **觸發條件**：Phase 0 偵測到 `docs/workflow-state.md` 存在
> **輸入**：workflow-state.md、docs/adr/、docs/change-log.md、docs/iteration-log.md
> **輸出**：恢復確認 + 繼續工作流

---

## 執行流程

```
workflow_resume():
  # Step 1: 載入狀態
  state = read("docs/workflow-state.md")
  gates = read_all("docs/adr/ADR-GATE-*.md")
  changelog = read("docs/change-log.md")
  iter_log = read("docs/iteration-log.md")

  # Step 2: 判定恢復點
  current = state.pipeline_position
  completed_gates = [g for g in gates if g.status == "Accepted"]
  pending_escalations = state.pending_escalations

  # Step 3: 組裝恢復摘要
  summary = {
    "pipeline_id": state.pipeline_id,
    "current_position": current,
    "completed_phases": completed_gates,
    "pending_work": state.wbs_tree.pending_leaves(),
    "pending_escalations": pending_escalations,
    "last_hitl_decision": iter_log.last_hitl_entry(),
    "last_updated": state.last_updated
  }

  # Step 4: 呈現摘要並與使用者確認
  present_to_user(summary):
    「偵測到既有工作流狀態。」
    「當前位置：{current_position}」
    「已通過閘門：{completed_gates}」
    「待處理工作：{pending_work}」
    IF pending_escalations:
      「⚠️ 有未處理的上報：{pending_escalations}」

    ask_user:
      [1] 從斷點繼續
      [2] 使用者有其他指令（記錄後再回到工作流）
      [3] 重置工作流（需確認）

  # Step 5: 執行恢復
  IF user_choice == [1]:
    IF pending_escalations:
      → 優先處理 ESCALATION
    ELIF current is in Stage 3-8:
      → 從該 Stage 的 Step A 開始新一輪迭代
      → 載入 iteration-log.md 的歷史作為上下文
    ELSE:
      → 從 current_position 的下一個 WBS leaf 開始

  IF user_choice == [2]:
    → 記錄使用者指令
    → 執行使用者指令
    → 完成後回到 Step 4 重新確認

  IF user_choice == [3]:
    → 歸檔當前 workflow-state.md → docs/archive/
    → 從 Phase 0 重新開始
```

---

## 恢復安全契約（DbC）

**前置條件（Precondition）**：
1. `docs/workflow-state.md` 存在且可讀取
2. `docs/adr/` 目錄可存取
3. Session 尚未執行任何 Stage 推進動作

**不變量（Invariant）**：
1. **已通過的 HITL 閘門不可重做**：ADR-GATE Accepted 的決策不重新要求確認
2. **未通過的 HITL 閘門不可跳過**：必須從當前 Stage 繼續
3. **進行中的迭代安全重啟**：從 Step A 重啟，人類決策已持久化為 ADR
4. **ESCALATION 優先**：有未處理的上報必須先解決

**後置條件（Postcondition）**：
1. Pipeline 從正確斷點恢復，position 未倒退 [INV-001]
2. 所有已通過的 Gate 狀態保持不變
3. 使用者已確認恢復方式（[1]/[2]/[3]）
4. 恢復摘要已呈現，進行中的上報已標記
