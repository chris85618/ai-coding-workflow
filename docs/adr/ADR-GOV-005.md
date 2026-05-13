# ADR-GOV-005: TC 斷言設計指引

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-016

---

## 背景

- **觸發 Stage/Phase**: Stage 8 自驗
- **觸發事件**: TC-005/008 使用 multi-keyword regex 假設同行出現，但目標文件為多行佈局
- **前置條件**: TC 生成無斷言模式指引
- **約束**: LLM 未考慮目標文件的多行佈局特性

## 決策

我們決定建立 TC 斷言設計指引：(1) 每個斷言測試一個關鍵字，不合併多關鍵字 (2) 考慮多行佈局 (3) TC 生成後立即執行一遍驗證 (4) CJK 編碼安全

## 理由

- **支持證據**: TC-005/008 的 `COSMETIC.*MINOR.*MODERATE.*MAJOR` 正則在多行佈局下永遠不匹配
- **權衡取捨**: 斷言數量增加，但可靠性大幅提升

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 不設計指引，依賴 LLM 判斷 | 無額外步驟 | 已證明不可靠 | 根因未消除 |
| 只修正這兩個 TC | 最快 | 未來新 TC 會重複犯錯 | 未左移 |

## 後果

**正面**：TC 斷言在生成時即具備正確的匹配模式
**負面**：s2c-bdd-scenarios.md 增加指引內容

## 影響分析

- **爆炸半徑**: 2（TC-005, TC-008）
- **嚴重度**: MINOR
- **受影響 ID**: TC-005, TC-008

## 流程變更

- **修改前規則**: TC 生成無斷言模式指引
- **修改後規則**: s2c-bdd-scenarios.md 含 4 條 TC 斷言設計規則
- **影響範圍**: Stage 7, Stage 8

## 變更紀錄 (Implementation Records)

### 變更 #1: TC-005/008 測試斷言模式修正

- **日期**: 2026-05-13（Stage 8 自驗）
- **類型**: FIX
- **檔案**: docs/test-cases.md (TC-005 line 99, TC-008 line 118)
- **影響 ID**: TC-005, TC-008
- **爆炸半徑**: 2
- **嚴重度**: MINOR
- **微驗證**: 未執行

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-003: multi-keyword regex 錯誤

- **根因分類**: LLM_HALLUCINATION
- **根因描述**: LLM 使用 multi-keyword regex 假設所有嚴重度關鍵字出現在同一行
- **5 Whys**:
  1. 為什麼斷言錯誤？→ 使用 multi-keyword regex（`COSMETIC.*MINOR.*MODERATE.*MAJOR`）假設同行
  2. 為什麼沒被阻止？→ TC 生成無測試模式指引
  3. 為什麼驗證沒偵測？→ TC 未在生成後立即執行
  4. 為什麼流程允許？→ LLM 未考慮目標文件的多行佈局
  5. 結構性修正？→ **TC 斷言規範: 每個斷言測試一個關鍵字，不合併多關鍵字 + TC 生成後立即執行一遍**
- **左移守衛**: s2c-bdd-scenarios.md 加入斷言模式指引
- **更新 Skill**: s2c-bdd-scenarios.md ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-003 | multi-keyword regex 錯誤 |
