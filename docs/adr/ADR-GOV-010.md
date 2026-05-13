# ADR-GOV-010: Session-End Hook Precondition Gate (INV-CM-005)

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-007

---

## 背景

- **觸發 Stage/Phase**: 使用者 RCA 要求
- **觸發事件**: AI 將「完成本輪檔案修改」（Step 1）視為 CM 流程完成，跳過 Steps 2-5
- **前置條件**: CM Step 6 只寫「每次回覆前執行」，無 precondition 要求
- **約束**: AI 的線性假設（完成生成 = 完成 CM）

## 決策

我們決定在 Session-End Hook (CM Step 6) 加入顯式 precondition_check()：FOR each FIX/MODIFY 逐一 ASSERT Steps 0-5 complete。未通過則 STOP，禁止輸出「📍 當前狀態 & 下一步」。新增 INV-CM-005 結構不變量。

## 理由

- **支持證據**: AI 在完成 Step 1 後直接觸發 Step 6，Steps 2-5 全部跳過
- **權衡取捨**: 增加 Step 6 前置檢查成本，但阻止 CM 跳步

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 依賴 AI 自主遵守步驟順序 | 零成本 | 已證明 AI 會跳步 | 根因未消除 |
| 在每個 Step 末加 checkpoint | 更細粒度 | 過度設計 | Ockham |

## 後果

**正面**：CM 跳步在 Step 6 被 hard gate 攔截
**負面**：AI 必須在每次回覆前自我審計所有變更的 CM 狀態

## 影響分析

- **爆炸半徑**: 3 檔案
- **嚴重度**: MAJOR
- **受影響 ID**: INV-CM-005（新增）

## 流程變更

- **修改前規則**: Step 6 無前置斷言
- **修改後規則**: Step 6 含 precondition_check() + INV-CM-005
- **影響範圍**: 全切面（所有含 FIX/MODIFY 的 session）

## 變更紀錄 (Implementation Records)

### 變更 #1: Session-End Hook 前置斷言

- **日期**: 2026-05-14T01:48+08:00
- **類型**: FIX (MODIFY × 3 files)
- **檔案**: AGENTS.md, CHANGE-MANAGEMENT.md, change-log.md
- **爆炸半徑**: 3
- **嚴重度**: MAJOR
- **微驗證**: PASS

**變更明細**:

| 檔案 | 變更 |
|------|------|
| AGENTS.md | session_end_hook 新增 Step 0 (CM 前置斷言 Precondition Gate) |
| CHANGE-MANAGEMENT.md | Step 6 新增顯式 Precondition Gate 區塊；新增 INV-CM-005 |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-009: CM 多步驟流程缺少「前置步驟完成」強制斷言

- **根因分類**: PROCESS_GAP
- **根因描述**: CM Step 6 只寫「每次回覆前執行」，無 precondition 要求 Steps 0-5 已完成
- **5 Whys**:
  1. 為什麼 Session-End Hook 在 CM Steps 2-5 未完成前觸發？→ AI 將「完成本輪檔案修改」視為 CM 流程完成
  2. 為什麼 AI 有這個誤判？→ CM Step 6 只寫「每次回覆前執行」，無 precondition
  3. 為什麼 Step 6 沒有 precondition？→ 設計時假設「線性流程自然前進」
  4. 為什麼 AI 可能跳步？→ Step 4 有免除條件出口，AI 誤判可用此出口
  5. 結構性修正？→ Step 6 加入顯式前置斷言清單
- **瓶頸識別**:
  - 問題發生點: Session 回覆前 / CM Step 6 觸發時
  - 逃逸路徑: CM Step 6 只寫「每次回覆前執行」→ 無 precondition 要求 Steps 0-5 已完成 → AI 從 Step 1 跳到 Step 6
  - 最早可偵測點: CM Step 6 入口
  - 瓶頸位置: `change-management-protocol.md` Step 6 缺少 precondition_check()
  - 介入類型: STEP_ADDITION
  - 預期覆蓋: 所有 CM 跳步行為
- **左移守衛**:
  1. AGENTS.md session_end_hook Step 0：precondition_check()（已實施 ✅）
  2. CHANGE-MANAGEMENT.md Step 6 Precondition Gate（已實施 ✅）
  3. INV-CM-005（已實施 ✅）
- **守衛驗證證據**: 模擬原始情境 → Step 0 ASSERT step_2_pgvg_passed FAIL → STOP

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-009 | CM 多步驟缺少前置斷言 |
