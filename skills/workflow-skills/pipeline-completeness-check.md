# Skill: Pipeline 完備性檢查

> **觸發條件**：Phase 0 環境啟動後自動執行
> **目的**：判斷此框架是否已基於既有內容做出詳盡記錄、分析、開發
> **原則**：足夠完備但盡可能輕量

---

## 檢查協議

```
pipeline_completeness_check():
  # Step 1: 快速掃描（< 30 秒）
  checks = {
    "workflow_state":  exists("docs/workflow-state.md"),
    "project_charter": exists("docs/project-charter.md") AND has_ids("BG-"),
    "stakeholders":    exists("docs/stakeholder-analysis.md") AND has_ids("S-"),
    "scope":           exists("docs/scope-definition.md") AND has_ids("FEA-"),
    "requirements":    exists("docs/requirements.md") AND has_ids("FR-"),
    "use_cases":       exists("docs/use-cases.md") AND has_ids("UC-"),
    "traceability":    exists("docs/traceability-matrix.md"),
    "adr_index":       exists("docs/adr/ADR-INDEX.md"),
    "iteration_log":   exists("docs/iteration-log.md"),
    "gate_adrs":       count("docs/adr/ADR-GATE-*.md") > 0
  }

  # Step 2: 計算完備度
  passed = count(v for v in checks.values() if v)
  total = len(checks)
  completeness = passed / total

  # Step 3: 判定
  IF completeness == 1.0:
    → Pipeline 完整：所有 Phase/Stage 的產出物皆存在且有 ID
    → 等同 HITL-P0-01 通過
    → 進一步判定：workflow-state.md 的 current position
    → 若有中斷的工作 → 觸發 workflow-resume.md

  ELIF completeness >= 0.6:
    → Pipeline 部分完成：已有基礎記錄
    → 判定最後完成的 Stage（從 Gate Status 讀取）
    → 觸發 workflow-resume.md 從斷點繼續

  ELIF completeness > 0 AND completeness < 0.6:
    → Pipeline 剛起步或不完整
    → 判定是 Path A（Greenfield）還是 Path B（既有 codebase 但未跑完管線）
    → Path B 判定：掃描專案目錄是否有非 docs/ 的原始碼
    → 若 Path B → Phase 1（/understand）→ Phase 2
    → 若 Path A → Phase 2

  ELSE (completeness == 0):
    → 全新專案
    → 掃描專案目錄判定 Path A/B
    → 進入對應路徑

  # Step 4: 報告（輕量輸出）
  REPORT:
    completeness_score: {passed}/{total}
    decision: {path}
    next_action: {action}
```

---

## 檢查項說明

| 檢查項 | 對應 Phase/Stage | 為什麼需要 |
|--------|-----------------|-----------|
| workflow_state | 跨切面 | 狀態機存在 = 管線曾經啟動 |
| project_charter | Phase 2.0 | BG-xxx 存在 = 商業目標已定義 |
| stakeholders | Phase 2.1 | S-xxx 存在 = 利害關係人已分析 |
| scope | Phase 2.2 | FEA-xxx 存在 = 範圍已定義 |
| requirements | Stage 3 | FR-xxx 存在 = 需求已分解 |
| use_cases | Stage 3 | UC-xxx 存在 = 使用案例已識別 |
| traceability | 跨切面 | 追溯矩陣存在 = 追溯系統運作中 |
| adr_index | 跨切面 | ADR 索引存在 = 決策記錄系統運作中 |
| iteration_log | Stage 3-8 | 迭代紀錄存在 = 至少一輪迭代已執行 |
| gate_adrs | Stage 3-8 | 閘門 ADR 存在 = 至少一個閘門已通過 |
