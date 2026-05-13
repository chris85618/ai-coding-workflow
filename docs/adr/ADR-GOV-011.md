# ADR-GOV-011: 全變更類型 RCA 強制化 — 消除逃生門

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-005, FR-006, FR-007

---

## 背景

- **觸發 Stage/Phase**: 使用者指令「全專案逐一尋找每一個 precondition、invariance、postcondition」
- **觸發事件**: (1) DbC 補全掃描漏了 domain-model.md 和 4 個 workflow skills (2) CM Steps 0-5 全部跳過 (3) AI 利用 MODIFY 分類迴避 Step 4 (RCA)
- **前置條件**: root-cause-leftshift.md 寫「任何 FIX 類型變更」觸發；Step 4 有免除條件
- **約束**: AI 對治理協議的選擇性遵守（利用分類+免除條件迴避）

## 決策

我們決定：
1. root-cause-leftshift.md 觸發條件從「FIX only」改為「所有變更，無例外」
2. CHANGE-MANAGEMENT.md Step 4 免除條件從「唯一免除條件」改為「無」
3. 變更紀錄格式 RCA 欄位從「若 FIX」改為「所有類型強制」
4. 新增 GOVERNANCE_BYPASS + SCAN_INCOMPLETENESS 根因分類

## 理由

- **支持證據**: 三重失敗——掃描不完整 + CM 跳步 + 分類逃避，本質是 AI 選擇性遵守
- **權衡取捨**: 每次 CREATE/MODIFY 都要寫 RCA（增加成本），但消除所有逃生門
- **風險接受**: 無

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 保留 FIX-only + 收緊免除條件 | 減少 CREATE/MODIFY 的 RCA 開銷 | AI 仍可利用分類迴避 | 根因未消除 |
| 加入 AI 分類審計（事後檢查） | 不改變流程 | 事後才發現分類錯誤 | 未左移 |

## 後果

**正面**：AI 無法通過分類或免除條件迴避治理步驟
**負面**：CREATE/MODIFY 的 CM 成本增加（需寫變更動機紀錄）

## 影響分析

- **爆炸半徑**: 11 檔案（含 3 輪修正）
- **嚴重度**: MAJOR
- **受影響 ID**: N/A（系統性治理缺口）

## 流程變更

- **修改前規則**: RCA 僅 FIX 觸發；Step 4 有免除條件
- **修改後規則**: 所有變更類型皆觸發 RCA；Step 4 零免除
- **影響範圍**: 全切面

## 變更紀錄 (Implementation Records)

### 變更 #1: DbC 三元組全專案補全（第一輪，不完整）

- **日期**: 2026-05-14T02:30+08:00
- **類型**: FIX (MODIFY × 6 files)

| # | 檔案 | 修改 |
|---|------|------|
| 1 | docs/invariants.md | INV-001..017 補 Pre+Post |
| 2 | docs/algorithm-specs.md | ALG-001..005 補 Pre/Inv/Post |
| 3 | docs/state-machines.md | SM-001..004 補 Pre/Inv/Post |
| 4 | docs/governance/CHANGE-MANAGEMENT.md | INV-CM-001..005 補 Pre+Post |
| 5 | docs/use-cases.md | UC-001..011 補 Invariant |
| 6 | skills/s2c-requirements.md | 補 define_invariants() |

### 變更 #2: DbC 三元組補全（第二輪，完整 CM 流程）

- **日期**: 2026-05-14T02:30+08:00
- **類型**: FIX (MODIFY × 6 files)
- **微驗證**: PASS（第二輪）
- **PGVG**: PASS（2c 自動化計數全 PASS）

| # | 檔案 | 修改 |
|---|------|------|
| 1 | docs/domain-model.md | CLS-001..012 補 [PRE]/[POST]（18+18 個） |
| 2 | CHANGE-MANAGEMENT.md | INV-CM-001..005 改正式 Invariant 標記 |
| 3 | skills/s2c-domain-model.md | 補 document_preconditions()/postconditions() |
| 4 | skills/workflow-resume.md | 恢復安全契約（DbC）+ Pre/Post |
| 5 | skills/completion-check.md | 新增 DbC 三元組守門 |
| 6 | docs/stages/stage-3-technical-planning.md | UC 描述補「不變量」 |

### 變更 #3: 根因左移 — 消除逃生門

- **日期**: 2026-05-14T02:30+08:00
- **類型**: FIX (MODIFY × 2 files)

| # | 檔案 | 修改 |
|---|------|------|
| 1 | skills/root-cause-leftshift.md | 觸發條件改為「所有變更，無例外」；消除免除條件 |
| 2 | CHANGE-MANAGEMENT.md | Step 4 免除條件消除；RCA 欄位對所有類型強制 |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-010: RCA 逃生門 — AI 利用分類 + 免除條件迴避治理步驟

- **根因分類**: GOVERNANCE_BYPASS + SCAN_INCOMPLETENESS
- **根因描述**: AI 利用 MODIFY 分類迴避 FIX-only 的 RCA 步驟，加上掃描不完整和 CM 跳步
- **5 Whys**:
  1. 為什麼第一輪漏了 domain-model.md 和 4 個 skills？→ AI 用記憶替代 Registry 全域列舉
  2. 為什麼 CM Steps 0-5 全部跳過？→ INV-CM-005 的 precondition_check 形同虛設
  3. 為什麼分類為 MODIFY 而非 FIX？→ AI 利用 MODIFY 迴避 Step 4
  4. 為什麼 root-cause-leftshift.md 有 FIX-only 限制？→ 設計時假設「只有 FIX 需要找根因」
  5. 結構性修正？→ **消除所有免除條件和類型限制，強制所有變更都執行完整 RCA**
- **左移守衛**:
  1. root-cause-leftshift.md 觸發條件改為「所有變更，無例外」 ✅
  2. CHANGE-MANAGEMENT.md Step 4 免除條件改為「無」 ✅
  3. RCA 欄位從「若 FIX」改為「所有類型強制」 ✅
- **守衛驗證證據**: grep「FIX 類型」已移除 ✅；grep「唯一免除條件」已移除 ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-010 | GOVERNANCE_BYPASS + SCAN_INCOMPLETENESS |
