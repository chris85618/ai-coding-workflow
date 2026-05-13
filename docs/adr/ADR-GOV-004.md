# ADR-GOV-004: UC↔CLS 覆蓋斷言強制化

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-005, FR-017

---

## 背景

- **觸發 Stage/Phase**: Stage 6 入口自驗
- **觸發事件**: UC-002/006/009 缺少 CLS 覆蓋。限界上下文表覆蓋 9/9 但 CLS 類別只定義了 6/9
- **前置條件**: s2c-domain-model.md 無 UC↔CLS 覆蓋斷言
- **約束**: LLM 將「限界上下文涵蓋」等同於「CLS 建模完成」

## 決策

我們決定在 s2c-domain-model.md 中加入逐一 UC→CLS 映射驗證，覆蓋斷言必須從實際內容 grep 而非 LLM 自我報告。格式：`UC-001→CLS-001 ✅, UC-002→CLS-012 ✅, ...`

## 理由

- **支持證據**: 3 個 UC 完全缺少 CLS 覆蓋，加上 2 個 EVT 未建立
- **權衡取捨**: 增加 Stage 5 驗證步驟，但消除覆蓋缺口
- **風險接受**: 無

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 允許泛稱「N/N 覆蓋」 | 快速 | LESSON-002 證明泛稱不可靠 | 根因未消除 |
| 僅在 completion-check 驗證 | 集中化 | 錯誤累積至 Phase 9 | 違反左移原則 |

## 後果

**正面**：覆蓋缺口在 Stage 5 內即被發現並修正
**負面**：Stage 5 產出時間增加（逐一驗證）

## 影響分析

- **爆炸半徑**: 4（CLS-010, CLS-011, CLS-012, EVT-005 新增）
- **嚴重度**: MAJOR
- **受影響 ID**: CLS-010, CLS-011, CLS-012, EVT-005

## 流程變更

- **修改前規則**: s2c-domain-model.md 無覆蓋斷言
- **修改後規則**: PGVG-1 逐一 UC→CLS 映射 + PGVG-2 限界上下文一致性 + PGVG-3 自動化計數
- **影響範圍**: Stage 5

## 變更紀錄 (Implementation Records)

### 變更 #1: UC-002/006/009 CLS 覆蓋補全

- **日期**: 2026-05-13（Stage 6 入口自驗）
- **類型**: FIX
- **檔案**: docs/domain-model.md
- **影響 ID**: CLS-010, CLS-011, CLS-012, EVT-005（新增）
- **爆炸半徑**: 4（新增 4 個 ID）
- **嚴重度**: MAJOR
- **微驗證**: 部分執行（更新矩陣但無紀錄）

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-002: 泛稱覆蓋不可靠

- **根因分類**: COVERAGE_GAP + LLM_HALLUCINATION
- **根因描述**: LLM 將「限界上下文涵蓋」等同於「CLS 建模完成」，用泛稱覆蓋掩蓋缺口
- **5 Whys**:
  1. 為什麼 3 個 UC 沒有 CLS？→ 限界上下文表覆蓋 9/9 但 CLS 類別只定義了 6/9
  2. 為什麼沒被阻止？→ s2c-domain-model.md 無 UC↔CLS 覆蓋斷言
  3. 為什麼驗證沒偵測？→ 完成報告用泛稱 "9/9 UC 覆蓋" 未逐一列出
  4. 為什麼流程允許？→ LLM 將「限界上下文涵蓋」等同於「CLS 建模完成」
  5. 結構性修正？→ **s2c-domain-model.md 加入逐一 UC→CLS 映射驗證 + 覆蓋斷言必須從實際內容 grep**
- **左移守衛**:
  - s2c-domain-model.md: 加入 "FOR each UC-xxx: ASSERT exists CLS with trace to UC-xxx"
  - micro-validation.md Step 4: 加入交叉覆蓋驗證
  - completion-check.md: 加入自動化計數
- **更新 Skill**: micro-validation.md ✅, s2c-domain-model.md ✅, completion-check.md ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-002 | 泛稱覆蓋不可靠 |
