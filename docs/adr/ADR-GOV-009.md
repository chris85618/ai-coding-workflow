# ADR-GOV-009: Skill 版本升級級聯協議

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-024

---

## 背景

- **觸發 Stage/Phase**: 使用者指令「仔細掃描每一個 docs/ 下的文件」
- **觸發事件**: iter-loop.md 從「HITL-per-iteration（3 選項）」演化為「AI-first 收斂（Step F + 2 選項）」，但 6 個 Stage 文件各含過期的 inline 副本
- **前置條件**: 無「Skill 版本升級 → 引用方掃描」協議

## 決策

我們決定：(1) Stage 文件迭代協議區塊必須以引用開頭（`完整迭代協議定義見 iter-loop.md`），消除副本 (2) PGVG Step 2e 在修改 iter-loop.md 時必須掃描 docs/stages/*.md 驗證一致性

## 理由

- **支持證據**: 6 個 Stage 文件各含 iter-loop 的「快照副本」，升級後全部過期
- **權衡取捨**: Stage 文件失去自包含性，但消除版本漂移

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 保留 inline 副本 + 手動同步 | Stage 文件自包含 | 已證明漂移不可避免 | 根因未消除 |
| 自動化副本生成 | 自包含 + 一致性 | 工具複雜度高 | 過度設計 (Ockham) |

## 後果

**正面**：Skill 升級自動級聯至引用方
**負面**：Stage 文件需查閱 skill 原始碼才能了解完整迭代協議

## 影響分析

- **爆炸半徑**: 13 檔案
- **嚴重度**: MAJOR
- **受影響 ID**: N/A（結構性同步問題）

## 流程變更

- **修改前規則**: Stage 文件含 iter-loop 完整副本
- **修改後規則**: Stage 文件以引用方式引用 iter-loop.md
- **影響範圍**: Stage 3-8, Phase 2, Phase 9

## 變更紀錄 (Implementation Records)

### 變更 #1: 全面追溯審計 — iter-loop AI-first 模型傳播修正

- **日期**: 2026-05-14T01:43+08:00
- **類型**: FIX (MODIFY × 13 files)
- **嚴重度**: MAJOR
- **微驗證**: PASS

**變更明細**:

| # | 檔案 | 修正內容 |
|---|------|----------|
| 1-6 | docs/stages/stage-{3-8}*.md | 迭代協議加 iter-loop.md 引用 |
| 7 | docs/phases/phase-2*.md | 移除未定義 ASM-xxx 前綴 |
| 8 | skills/s2c-requirements.md | 新增 PGVG 區塊 |
| 9 | docs/phases/phase-9*.md | 新增 completion-check.md 引用 |
| 10 | docs/requirements.md | FR-013/014 更新 |
| 11 | docs/bdd-scenarios.md | SC-003 場景更新 |
| 12 | docs/adr/ADR-TEMPLATE.md | GATE 區塊更新 |
| 13 | docs/iteration-log.md | HITL Decision 格式更新 |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-008: Skill 版本演化未觸發下游文件級聯更新

- **根因分類**: PROCESS_GAP
- **根因描述**: iter-loop.md 演化後沒有機制確保引用方同步更新
- **5 Whys**:
  1. 為什麼 Stage docs 仍有舊版？→ 升級前已建立，升級後未 cascade
  2. 為什麼沒有 cascade？→ 無「Skill 版本升級 → 引用方掃描」協議
  3. 為什麼有 inline 副本？→ 建立時為說明具體化
  4. 為什麼無同步驗證？→ Step 5.5 僅追溯 ID，不追溯 skill 版本
  5. 結構性修正？→ Stage 文件改為引用 iter-loop.md，消除副本
- **左移守衛**: Stage 文件迭代協議必須以引用開頭 ✅
- **更新 Skill**: stage-3 到 stage-8 ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-008 | Skill 版本演化未觸發級聯 |
