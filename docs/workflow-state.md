# Workflow State — 目標導向 WBS

> **用途**：工作流狀態機的持久化單一事實來源。
> **原則**：僅保留「尚未完成且需要做的事」。完成的項目在其他文件記錄後從此處移除。
> **更新頻率**：每完成一個 WBS leaf 後立即更新。

---

## Pipeline Position

**Pipeline ID**: `pipe-langgraph-migration-v1`
**Current Phase/Stage**: `Stage 8 (TDD) — COMPLETED. 93 tests pass, 96.84% coverage ≥ 95% threshold. Phase 9 Ship pending.`
**Last Updated**: `2026-05-14T11:37+00:00`
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
ROOT: {專案目標}
│
├── Phase 0: 環境啟動
│   ├── [leaf] gstack 首次引導
│   │   └── LRM: Session 開始時自動觸發，僅首次
│   ├── [leaf] Pipeline 完備性檢查
│   │   └── LRM: 環境就緒後立即執行
│   └── [leaf] 恢復協議檢查（若 Recovery Mode = true）
│       └── LRM: 偵測到 workflow-state.md 存在且 Recovery Mode = true
│
├── Phase 1: 程式碼理解（Path B）
│   ├── [leaf] /understand 知識圖譜建立
│   │   └── LRM: Pipeline 完備性檢查判定需要時
│   └── [leaf] 探索性問答（按需）
│       └── LRM: 人類主動發起
│
├── Phase 2: 專案分析
│   ├── [leaf] 2.0 專案章程 → BG-xxx
│   │   └── LRM: Phase 1 完成或跳過後
│   ├── [leaf] 2.1 /office-hours + 利害關係人 → S-xxx
│   │   └── LRM: 2.0 核准後
│   ├── [leaf] 2.2 範圍定義 + Red Team → FEA-xxx
│   │   └── LRM: 2.1 完成後
│   ├── [leaf] 2.3 /plan-ceo-review 策略驗證
│   │   └── LRM: 2.2 完成後
│   └── [leaf] Phase 2 出口閘門
│       └── LRM: 2.0-2.3 全部完成後
│
├── Stage 3: 技術規劃（7 維）
│   ├── [leaf] AI 自主收斂迭代（Agent α/β → 不動點）
│   │   └── LRM: Phase 2 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Stage 4: 演算法設計（22 維）
│   ├── [leaf] AI 自主收斂迭代
│   │   └── LRM: Stage 3 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Stage 5: OOAD + 安全審計（4 維 + 3 層）
│   ├── [leaf] AI 自主收斂迭代
│   │   └── LRM: Stage 4 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Stage 6: 形式化驗證設計（6 維）
│   ├── [leaf] AI 自主收斂迭代
│   │   └── LRM: Stage 5 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Stage 7: BDD/ATDD（9 維）
│   ├── [leaf] AI 自主收斂迭代
│   │   └── LRM: Stage 6 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Stage 8: TDD + 測試 + 修復（5 維）
│   ├── [leaf] AI 自主收斂迭代
│   │   └── LRM: Stage 7 出口通過後
│   └── [leaf] HITL 收斂確認
│       └── LRM: AI 報告已達不動點
│
├── Phase 9: Ship & Deploy
│   ├── [leaf] /ship
│   ├── [leaf] /land-and-deploy
│   ├── [leaf] /canary
│   └── [leaf] /document-release
│
└── Phase 10: 反思 & 學習
    ├── [leaf] /retro
    ├── [leaf] 全對話 RCA 掃描 + 左移
    ├── [leaf] 技術債登記冊更新
    ├── [leaf] /understand 增量更新
    ├── [leaf] /evolve 學習萃取
    └── [leaf] 追溯矩陣歸檔
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
| Stage 8 | ✅ (self-bootstrap) | — | 2026-05-13 |

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
| 1 | 執行 Stage 8 TDD: 實作 production code + pytest-bdd step defs + 95% coverage | 使用者確認啟動 | CRITICAL |
| 2 | 實作 CLS-017 LLMStrategySelector + ALG-008 ModelSelector (Strategy Pattern) | Stage 8 | P0 |
| 3 | 實作 CLS-015 RepoMap + ALG-006 RepoMapBuilder (tree-sitter + PageRank) | Stage 8 | P0 |
| 4 | 實作 CLS-016 HookRunner + lifecycle hooks (4 events) | Stage 8 | P1 |
| 5 | 實作 ALG-007 ContextBudgetAllocator | Stage 8 | P1 |
| 6 | 實作 MCPGateway.auto_commit() atomic git commits | Stage 8 | P1 |

---

## Session Summary

> 由 Session-End Hook 每次 session 結束時覆寫。
> 用於下次 session 的 Step 2（比對差異）。

- **Last Session Date**: 2026-05-14T19:12+08:00
- **Pipeline Position (recorded)**: Stage 7 (設計完成; 全部 feature absorption 完成; 283 條追溯; 待 Stage 8 TDD)
- **Actual Work Done**: (1) 使用者指令執行: 移除 multi-agent parallel 和 memory curation。(2) Strategy Pattern LLM 提升至 P0: CLS-017 LLMStrategySelector + CLS-018 ModelConfig + ALG-008 ModelSelector + INV-022 + TaskType enum。(3) 全部吸收: FR-026~030, NFR-008, UC-012/013, SC-012~016 BDD feature files。(4) ADR-STR-004 決策記錄。(5) OOAD v3 + formal-verification v3 + traceability 262→283。(6) src/ 新增 model_config.py, repo_map.py, TaskType enum。
- **State Diff**: +21 IDs, +5 BDD features, +1 ADR, +3 src files, OOAD/INV/matrix 更新
- **Pending Escalations Carried Over**: 無
