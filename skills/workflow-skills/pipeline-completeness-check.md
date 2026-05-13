# Skill: Pipeline 完備性檢查

> **觸發條件**：Phase 0 環境啟動後自動執行
> **目的**：判斷此框架是否已基於既有內容做出詳盡記錄、分析、開發
> **原則**：足夠完備但盡可能輕量

---

## Step 1: 快速掃描

檢查以下 10 項是否存在且含有效 ID：

| # | 檢查項 | 對應 Phase/Stage | 檢查條件 |
|---|--------|-----------------|----------|
| 1 | workflow_state | 跨切面 | `docs/workflow-state.md` 存在 |
| 2 | project_charter | Phase 2.0 | `docs/project-charter.md` 存在 且 含 BG- |
| 3 | stakeholders | Phase 2.1 | `docs/stakeholder-analysis.md` 存在 且 含 S- |
| 4 | scope | Phase 2.2 | `docs/scope-definition.md` 存在 且 含 FEA- |
| 5 | requirements | Stage 3 | `docs/requirements.md` 存在 且 含 FR- |
| 6 | use_cases | Stage 3 | `docs/use-cases.md` 存在 且 含 UC- |
| 7 | traceability | 跨切面 | `docs/traceability-matrix.md` 存在 |
| 8 | adr_registry | 跨切面 | `docs/traceability-matrix.md` 含 `ADR 登記簿` 段落 |
| 9 | iteration_log | Stage 3-8 | `docs/iteration-log.md` 存在 |
| 10 | gate_adrs | Stage 3-8 | `docs/adr/ADR-GATE-*.md` 數量 > 0 |

## Step 2: 計算完備度

1. passed = 通過的檢查項數量
2. completeness = passed / 10

## Step 3: 判定路徑

- **completeness == 1.0** → Pipeline 完整。判定 workflow-state.md 的 current position。若有中斷工作 → 觸發 `workflow-resume.md`
- **completeness >= 0.6** → Pipeline 部分完成。從 Gate Status 判定最後完成的 Stage → 觸發 `workflow-resume.md` 從斷點繼續
- **0 < completeness < 0.6** → Pipeline 剛起步。判定 Path A（Greenfield）或 Path B（既有 codebase 但未跑完管線）。Path B 判定：掃描專案目錄是否有非 docs/ 的原始碼。Path B → Phase 1。Path A → Phase 2
- **completeness == 0** → 全新專案。掃描目錄判定 Path A/B → 進入對應路徑

## Step 4: 報告

輸出：
- completeness_score: {passed}/10
- decision: {path}
- next_action: {action}
