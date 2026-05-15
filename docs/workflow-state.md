# Workflow State — 目標導向 WBS

> **用途**：工作流狀態機的持久化單一事實來源。
> **原則**：僅保留「尚未完成且需要做的事」。完成的項目在其他文件記錄後從此處移除。
> **更新頻率**：每完成一個 WBS leaf 後立即更新。

---

## Pipeline Position

**Pipeline ID**: `pipe-langgraph-migration-v1`
**Current Phase/Stage**: `Phase 10 COMPLETE — LESSON-045~049 歸檔，RISK-004 降評，追溯矩陣已影片化。`
**Last Updated**: `2026-05-15T17:43:00+08:00`
**Recovery Mode**: false

---

## WBS Tree

> 格式說明：
> - `✅` = 已完成（下次更新時移除）
> - `🔄` = 進行中
> - `⏳` = 待執行
> - `🚫` = 已決定不執行（附理由）
> - 每個 leaf 標注 **LRM 判定條件**（見下方定義）
> - 完成項移除前，確認產出物已持久化至對應 docs/ 文件

```
ROOT: {零容忍警告治理}
│
└── ⏳ 等待人類發起下一階段任務 (Phase 11)
```

---

## Gate Status

| Phase/Stage | Status | ADR Reference | Timestamp |
|-------------|--------|---------------|-----------|
| Phase 0 | ✅ | — | 2026-05-13 |
| Phase 1 | ✅ | — | 2026-05-13 |
| Phase 2 | ✅ | ADR-STR-001 | 2026-05-13 |
| Stage 3 | ✅ (self-bootstrap) | ADR-GOV-001, ADR-GOV-002 | 2026-05-13 |
| Stage 4 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 5 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 6 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 7 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 8 | ✅ (Strict Error) | ADR-GOV-026 | 2026-05-15 |
| Phase 9 | ✅ | — | 2026-05-15 |
| Phase 10 | ✅ | — | 2026-05-15 |

> 每個 Phase/Stage 通過後新增一行。已歸檔的行保留作為恢復判定依據。

---

## Pending Escalations

| ID | Type | Trigger | Context | Status |
|----|------|---------|---------|--------|
| (none) | — | — | — | — |

> ESCALATION 解決後移除此行，決策記錄至對應 ADR。

---

## Current Iteration Context

> 僅在 Stage 3-8 進行中時填寫。Stage 出口通過後清空此區塊。

- **Stage**: —
- **Iteration Round**: —
- **Agent α Status**: —
- **Agent β Status**: —
- **Fixed-point Reached**: —

---

## Last Responsible Moment (LRM) 判定框架

> 每個 WBS leaf 的 LRM 由以下四條件的**最早者**決定：

| 條件類型 | 定義 | 範例 |
|----------|------|------|
| **依賴驅動** | 下游任務需要此任務的輸出 | Stage 4 依賴 Stage 3 的 FR-xxx |
| **資訊驅動** | 所有上游輸入已可用，延遲不增加資訊量 | Phase 2 所有步驟完成 → 出口閘門的 LRM 到達 |
| **風險驅動** | 延遲使風險超過閾值 | ESCALATION pending 超過 1 個迭代輪次 |
| **閘門驅動** | 所在 Stage/Phase 即將進入出口閘門 | Stage 內所有 leaf 完成 → 出口 LRM 到達 |

### LRM 判定協議

```
FOR each pending WBS leaf L:
  dep_ready = all upstream dependencies of L are satisfied
  info_available = no pending information that would change L's decision
  risk_threshold = delay cost > decision-reversal cost
  gate_imminent = containing Stage/Phase is ready for exit

  IF any(dep_ready, info_available, risk_threshold, gate_imminent):
    L.lrm_reached = true
    → 執行 L
  ELSE:
    L.lrm_reached = false
    → 延遲（但記錄延遲理由）
```

---

## WBS 維護協議

```
每完成一個 WBS leaf:
  1. 確認產出物已持久化至 docs/ 對應文件
  2. 確認相關 ADR 變更紀錄已記錄
  3. 將該 leaf 狀態標為 ✅
  4. 檢查是否需拆分新 leaf（發現了原始規劃未預見的工作）
  5. 更新 Gate Status（若為閘門類 leaf）
  6. 清理：移除所有 ✅ leaf（產出物已在其他文件，此處不重複）
# Workflow State — 目標導向 WBS

> **用途**：工作流狀態機的持久化單一事實來源。
> **原則**：僅保留「尚未完成且需要做的事」。完成的項目在其他文件記錄後從此處移除。
> **更新頻率**：每完成一個 WBS leaf 後立即更新。

---

## Pipeline Position

**Pipeline ID**: `pipe-langgraph-migration-v1`
**Current Phase/Stage**: `Stage 3 COMPLETE — ADR-STR-008 建立，Token 機制實作。`
**Last Updated**: `2026-05-15T22:30:00+08:00`
**Recovery Mode**: false

---

## WBS Tree

> 格式說明：
> - `✅` = 已完成（下次更新時移除）
> - `🔄` = 進行中
> - `⏳` = 待執行
> - `🚫` = 已決定不執行（附理由）
> - 每個 leaf 標注 **LRM 判定條件**（見下方定義）
> - 完成項移除前，確認產出物已持久化至對應 docs/ 文件

```
ROOT: {零容忍警告治理}
│
└── ⏳ 等待人類發起下一階段任務 (Phase 11)
```

---

## Gate Status

| Phase/Stage | Status | ADR Reference | Timestamp |
|-------------|--------|---------------|-----------|
| Phase 0 | ✅ | — | 2026-05-13 |
| Phase 1 | ✅ | — | 2026-05-13 |
| Phase 2 | ✅ | ADR-STR-001 | 2026-05-13 |
| Stage 3 | ✅ (self-bootstrap) | ADR-GOV-001, ADR-GOV-002 | 2026-05-13 |
| Stage 4 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 5 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 6 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 7 | ✅ (self-bootstrap) | — | 2026-05-13 |
| Stage 8 | ✅ (Strict Error) | ADR-GOV-026 | 2026-05-15 |
| Phase 9 | ✅ | — | 2026-05-15 |
| Phase 10 | ✅ | — | 2026-05-15 |

> 每個 Phase/Stage 通過後新增一行。已歸檔的行保留作為恢復判定依據。

---

## Pending Escalations

| ID | Type | Trigger | Context | Status |
|----|------|---------|---------|--------|
| (none) | — | — | — | — |

> ESCALATION 解決後移除此行，決策記錄至對應 ADR。

---

## Current Iteration Context

> 僅在 Stage 3-8 進行中時填寫。Stage 出口通過後清空此區塊。

- **Stage**: —
- **Iteration Round**: —
- **Agent α Status**: —
- **Agent β Status**: —
- **Fixed-point Reached**: —

---

## Last Responsible Moment (LRM) 判定框架

> 每個 WBS leaf 的 LRM 由以下四條件的**最早者**決定：

| 條件類型 | 定義 | 範例 |
|----------|------|------|
| **依賴驅動** | 下游任務需要此任務的輸出 | Stage 4 依賴 Stage 3 的 FR-xxx |
| **資訊驅動** | 所有上游輸入已可用，延遲不增加資訊量 | Phase 2 所有步驟完成 → 出口閘門的 LRM 到達 |
| **風險驅動** | 延遲使風險超過閾值 | ESCALATION pending 超過 1 個迭代輪次 |
| **閘門驅動** | 所在 Stage/Phase 即將進入出口閘門 | Stage 內所有 leaf 完成 → 出口 LRM 到達 |

### LRM 判定協議

```
FOR each pending WBS leaf L:
  dep_ready = all upstream dependencies of L are satisfied
  info_available = no pending information that would change L's decision
  risk_threshold = delay cost > decision-reversal cost
  gate_imminent = containing Stage/Phase is ready for exit

  IF any(dep_ready, info_available, risk_threshold, gate_imminent):
    L.lrm_reached = true
    → 執行 L
  ELSE:
    L.lrm_reached = false
    → 延遲（但記錄延遲理由）
```

---

## WBS 維護協議

```
每完成一個 WBS leaf:
  1. 確認產出物已持久化至 docs/ 對應文件
  2. 確認相關 ADR 變更紀錄已記錄
  3. 將該 leaf 狀態標為 ✅
  4. 檢查是否需拆分新 leaf（發現了原始規劃未預見的工作）
  5. 更新 Gate Status（若為閘門類 leaf）
  6. 清理：移除所有 ✅ leaf（產出物已在其他文件，此處不重複）
  7. 更新 Last Updated 時間戳
  8. 更新 Pipeline Position
  9. 更新 Next Actions（見下方）
  10. 更新 Session Summary（見下方）
```

---

## Next Actions

> 由 Session-End Hook（AGENTS.md Step 12）自動維護。
> 列出所有 LRM 已到達的 pending WBS leaf + HITL 待決項。
> 每次 session 結束時覆寫此區塊。

| # | 行動 | 觸發條件 / LRM 判定 | 優先級 |
|---|------|---------------------|--------|
| 1 | 新開發週期計畫 (Phase 11) | 人類主動發起新功能需求 | P2 |
| 2 | DEBT-005 SonarCloud CI 閘門 | 視需求設定 | P3 |

---

## Session Summary

> 由 Session-End Hook 每次 session 結束時覆寫。
> 用於下次 session 的 Step 2（比對差異）。

- **Last Session Date**: 2026-05-15T22:30+08:00
- **Pipeline Position (recorded)**: Stage 3 COMPLETE (架構設計 ADR-STR-008)
- **Actual Work Done**: 建立 ADR-STR-008 (Token 機制)，修改 `llm_adapter.py` 以實作 TaskType-aware 的自動續寫與快速失敗機制，新增 `exceptions.py`。更新 `traceability-matrix.md`，新增 FR-034 追溯。
- **State Diff**: 架構性擴展完成。
- **Pending Escalations Carried Over**: 無

