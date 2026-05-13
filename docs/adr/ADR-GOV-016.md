# ADR-GOV-016: 務實簡潔性最高元原則 (Ockham's Razor)

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: NFR-001, FR-014
> **整合來源**: Omega v9.8 Foundry Generation

---

## 背景

- **觸發 Stage/Phase**: 治理層（Omega v9.8 整合）
- **觸發事件**: 分析 Omega v9.8 識別出「過度設計」為 LLM 系統的結構性風險
- **前置條件**: 無明確元原則約束設計簡潔性

## 決策

我們決定將「務實簡潔性 (Ockham's Razor)」列為核心原則 #10：所有決策強制優先選擇線性、無條件的最簡路徑，拒絕推測性的未來需求（YAGNI）。雙 Agent 迭代中 Agent β 的決策流強制包含「奧坎剃刀」步驟。

## 理由

- **支持證據**: LLM 傾向產生過度設計方案（LESSON-010 中 AI 利用分類逃避即為複雜度衍生問題）
- **權衡取捨**: 某些靈活性設計可能被排除，但系統複雜度可控

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 不設約束，依賴審查 | 保留靈活性 | LLM 傾向複雜化 | 根因未消除 |
| 僅在 YAGNI 步驟提示 | 低成本 | 非強制性 | 不夠強 |

## 後果

**正面**：系統設計保持精簡，認知負擔降低
**負面**：可能需要後期重構以添加原本排除的靈活性

## 影響分析

- **爆炸半徑**: 1（AGENTS.md 核心原則）
- **嚴重度**: MODERATE
- **受影響 ID**: N/A

## 流程變更

- **修改前規則**: 核心原則 9 條
- **修改後規則**: 核心原則 11 條（#10 Ockham's Razor）
- **影響範圍**: 所有設計決策

## 變更紀錄 (Implementation Records)

### 變更 #1: 全 Skill 順序化重構 — 16 檔案轉為 Step N 格式

- **日期**: 2026-05-14T03:49+08:00
- **類型**: MODIFY (16 files)
- **嚴重度**: MAJOR（結構性重構，跨所有 Stage）
- **微驗證**: PASS（grep "## Step" 驗證 16/16 files 皆含 Step N 格式 ✅; grep "┌──" = 0 殘留 ✅）

**變更明細**:

| 批次 | 檔案 | Step 數 |
|------|------|:-------:|
| A | iter-loop.md | 6 |
| A | micro-validation.md | 10 |
| A | root-cause-leftshift.md | 8 |
| A | impact-analysis-exec.md | 6 |
| A | workflow-resume.md | 5 |
| B | pipeline-completeness-check.md | 4 |
| B | completion-check.md | 8 |
| B | security-audit-3layer.md | 4 |
| B | sonarcloud-gate.md | 5 |
| B | tech-debt-collect.md | 4 |
| C | s2c-charter.md | 5 |
| C | s2c-stakeholder.md | 5 |
| C | s2c-scope-redteam.md | 7 |
| C | s2c-requirements.md | 7 |
| C | s2c-domain-model.md | 5 |
| C | s2c-bdd-scenarios.md | 6 |

### 變更 #2: AGENTS.md + README.md 順序化重構

- **日期**: 2026-05-14T03:55+08:00
- **類型**: MODIFY (2 files)
- **嚴重度**: MAJOR
- **微驗證**: PASS（grep "┌──" AGENTS.md = 0 殘留 ✅）

| 檔案 | 變更區段 |
|------|----------|
| AGENTS.md | 核心原則新增 #12；迭代協議 → Step 1-6；啟動協議 → Step 1-5；收尾協議 → Step 0-4 |
| README.md | Architecture 更新；Skill Protocol Format 新增；Key Files 更新 |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-014: 混合格式 Skill 增加 LLM 解析負擔

- **根因分類**: IMPROVEMENT
- **根因描述**: 原 skill 文件使用混合格式（code blocks + box-drawing + Track N），LLM 需先理解結構才能執行
- **5 Whys**:
  1. 為什麼 LLM 解析 skill 慢？→ 格式不統一：有 code block、function-style、Track 平行結構
  2. 為什麼格式不統一？→ 各 skill 在不同 session 建立
  3. 為什麼沒有統一格式？→ 無「skill 格式規範」
  4. 為什麼無格式規範？→ 初版未考慮 LLM 解析效率
  5. 結構性修正？→ **全部 skill 統一為 `## Step N` 格式**
- **瓶頸識別**:
  - 問題發生點: Skill 建立時（各 session 獨立建立）
  - 逃逸路徑: 無「skill 格式規範」→ 各 skill 在不同 session 建立 → 格式不統一
  - 最早可偵測點: Skill CREATE 時
  - 瓶頸位置: 所有 `workflow-skills/*.md`（無統一格式規範）
  - 介入類型: NEW_GUARD
  - 預期覆蓋: Skill 格式不一致導致的 LLM 解析效率問題
- **左移守衛**: 新建 skill 時必須使用 `## Step N` 格式
- **更新 Skill**: 16 個 workflow-skills/*.md 全部 ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 來源 | Omega v9.8 | Ockham's Razor 元原則 |
| 教訓 | LESSON-014 | 混合格式 Skill 增加 LLM 解析負擔 |
