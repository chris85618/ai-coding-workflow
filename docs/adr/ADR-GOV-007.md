# ADR-GOV-007: 跨檔案增量演化同步治理

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-024

---

## 背景

- **觸發 Stage/Phase**: Phase 10 /retro 自我檢驗
- **觸發事件**: 全庫自我檢驗發現 14 個跨檔案不一致（精簡路徑殘留、步數過期、幽靈引用等）
- **前置條件**: 治理文件多次增量演化，但每次僅更新直接相關文件
- **約束**: 多檔案系統中增量修改的一致性難以維護

## 決策

我們決定每次增量演化後強制執行跨檔案 grep 掃描 + policy 一致性檢查。後升級為 CHANGE-MANAGEMENT Step 5（跨切面一致性驗證）。

## 理由

- **支持證據**: 12 個檔案存在 14 處不一致，根因是增量演化未觸發全庫掃描
- **權衡取捨**: 增加 Step 5 驗證成本，但消除跨檔案漂移

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 僅依賴 /retro 發現 | 不增加日常成本 | Phase 10 才發現，修復成本高 | 已證明不足 |
| 每次修改只檢查直接引用者 | 減少掃描範圍 | 間接引用漏掃 | 爆炸半徑計算不完整 |

## 後果

**正面**：跨檔案 policy 漂移在變更時即被偵測
**負面**：跨切面驗證增加 session 時間

## 影響分析

- **爆炸半徑**: 14（跨 12 個檔案）
- **嚴重度**: MODERATE
- **受影響 ID**: N/A（結構性同步問題）

## 流程變更

- **修改前規則**: 微驗證僅驗證 ID 追溯，不驗證跨檔案 policy 一致性
- **修改後規則**: CHANGE-MANAGEMENT Step 5 + micro-validation Step 5.5
- **影響範圍**: 全切面

## 變更紀錄 (Implementation Records)

### 變更 #1: 全庫自我檢驗批次修正

- **日期**: 2026-05-13T23:27+08:00
- **類型**: FIX
- **觸發**: Phase 10 /retro 自我檢驗
- **嚴重度**: MODERATE (blast_radius=14, cross_stage=ALL)
- **微驗證**: 未執行

**變更明細** (12 個檔案):

| # | 檔案 | 修正內容 | 嚴重度 |
|---|------|----------|--------|
| 1 | CLAUDE.md | 移除「精簡路徑」，改為「無簡化路徑」 | CRITICAL |
| 2 | CLAUDE.md | 雙Agent協議補 Step M（4步→5步） | CRITICAL |
| 3 | CLAUDE.md | Phase 9 補 /document-release | MAJOR |
| 4 | CLAUDE.md | Phase 10 補 技術債更新 | MAJOR |
| 5 | WORKFLOW.md | adr/ listing 補 ADR-GOV-001.md | MAJOR |
| 6 | WORKFLOW.md | 呼叫鏈補 root-cause-leftshift.md | MAJOR |
| 7 | README.md | 移除「825 行」過期數字 | MODERATE |
| 8 | README.md | 移除「精簡路徑」 | MODERATE |
| 9 | requirements.md | FR-007「6 步」→「8 步」 | MODERATE |
| 10 | TRACEABILITY.md | 微驗證迴圈 6 步→8 步 | MODERATE |
| 11 | project-charter.md | governance/ (3)→(5), Skills 13→14 | MODERATE |
| 12 | domain-model.md | CLS-009 補缺失 ``` | MINOR |
| 13 | GEMINI.md | 路徑反斜線→正斜線 | MINOR |
| 14 | 6 個檔案 | docs/impact-log.md→docs/change-log.md | MINOR |
| 15 | security-audit-stage8.md | 技能檔案 13→14 | MINOR |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-006: 跨檔案增量演化同步斷裂

- **根因分類**: PROCESS_GAP
- **根因描述**: 治理文件在多次迭代中增量演化，每次演化僅更新直接相關文件，未觸發全庫交叉引用掃描
- **5 Whys**:
  1. 為什麼 CLAUDE.md 有精簡路徑？→ 建立時從較早版本複製，之後 WORKFLOW.md 才移除
  2. 為什麼沒被偵測？→ 微驗證僅驗證 ID 追溯，不驗證跨檔案 policy 一致性
  3. 為什麼 impact-log.md 幽靈引用存在？→ 改名為 change-log.md 時未全庫 grep
  4. 為什麼 6 步/8 步不一致？→ ALG-002 升級時只改了 CHANGE-MANAGEMENT.md
  5. 結構性修正？→ **每次增量演化後，強制執行跨檔案 grep 掃描 + policy 一致性檢查**
- **瓶頸識別**:
  - 問題發生點: 治理文件增量演化時（多次 session 跨越）
  - 逃逸路徑: 微驗證 Step 0-7 僅驗證 ID 追溯 → 不驗證跨檔案 policy 一致性
  - 最早可偵測點: 變更管理流程（每次修改後）
  - 瓶頸位置: `change-management-protocol.md` 缺少跨切面驗證步驟 + `micro-validation.md` 缺少 Step 5.5
  - 介入類型: NEW_GUARD
  - 預期覆蓋: 跨檔案 policy 漂移、幽靈引用、步數不一致
- **左移守衛**: CHANGE-MANAGEMENT Step 5（跨切面一致性驗證）+ Step 2f（FR/NFR 合規驗證）+ micro-validation.md Step 5.5（全方向連結追溯）
- **更新 Skill**: micro-validation.md ✅
- **守衛強化歷程**:
  - 2026-05-13 初版守衛: micro-validation.md Step 0（僅格式 lint）
  - 2026-05-14 GUARD_STRENGTHENING: 根因重現 → 守衛升級至 CHANGE-MANAGEMENT Step 5 + Step 2f + micro-validation.md Step 5.5

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-006 | 跨檔案增量演化同步斷裂 |
