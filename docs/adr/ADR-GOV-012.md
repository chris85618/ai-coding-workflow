# ADR-GOV-012: Session-Start Hard Gate

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-019

---

## 背景

- **觸發 Stage/Phase**: 使用者 RCA 要求「對話開始為什麼沒有照 workflow 走」
- **觸發事件**: AI 收到 DbC 補全任務後直接開始掃描和修改，未讀取 workflow-state.md
- **前置條件**: AGENTS.md Phase 0 描述為「自動」，但無 structural hard gate
- **約束**: Session-End 有 precondition_check()（見 ADR-GOV-010），但 Session-Start 沒有對等機制

## 決策

我們決定在 AGENTS.md 新增完整 Session-Start Hook 協議：
1. Step 1: 讀取 workflow-state.md
2. Step 2: 若有既有狀態則執行 workflow-resume.md
3. Step 3: 報告當前位置
4. Step 4: Hard Gate — ASSERT session_start_completed = TRUE
5. 在 Step 1-4 完成前禁止任何 CREATE/MODIFY/FIX

## 理由

- **支持證據**: 對話紀錄 step_index 0-15 證明 AI 直接開始工作，未讀取狀態
- **權衡取捨**: 每個 session 增加啟動開銷，但保障工作流完整性

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 依賴 AI 自主執行 Phase 0 | 零開銷 | 已證明 AI 會跳過 | 根因未消除 |
| 僅加提醒文字 | 低成本 | AI 可能忽略提醒 | 非 hard gate |

## 後果

**正面**：session 開始時必定讀取工作流狀態
**負面**：每個 session 增加啟動延遲

## 影響分析

- **爆炸半徑**: 1（AGENTS.md）
- **嚴重度**: MAJOR
- **受影響 ID**: N/A

## 流程變更

- **修改前規則**: Phase 0 為「自動」但無 hard gate
- **修改後規則**: Session-Start Hook 含 4 步 + Hard Gate + DbC 三元組
- **影響範圍**: 每個 session 的第一個動作

## 變更紀錄 (Implementation Records)

### 變更 #1: Session-Start Hook 建立 + 核心原則 #8

- **日期**: 2026-05-14T02:47+08:00
- **類型**: FIX
- **檔案**: AGENTS.md
- **嚴重度**: MAJOR

| # | 檔案 | 修改內容 |
|---|------|---------|
| 1 | AGENTS.md 核心原則 | 新增 #8 啟動閘門 |
| 2 | AGENTS.md | 新增完整 Session-Start Hook（4 步驟 + DbC + Hard Gate）|

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-011: SESSION_START_BYPASS — Session 啟動無 Hard Gate

- **根因分類**: SESSION_START_BYPASS
- **根因描述**: AGENTS.md 有 Session-End Hook precondition_check() 但沒有對等的 Session-Start Hook，AI 可直接繞過
- **5 Whys**:
  1. 為什麼 AI 直接開始工作？→ 將使用者指令視為最高優先，跳過 Phase 0
  2. 為什麼認為可以跳過？→ Phase 0 描述為「自動」但無 structural hard gate
  3. 為什麼沒有 hard gate？→ workflow-resume.md 是被動觸發的 skill
  4. 為什麼收尾有但啟動沒有？→ Session-End precondition 是 ADR-GOV-010 後才加入的
  5. Root Cause → Session-Start 沒有等價於 Session-End 的 hard gate
- **左移守衛**:
  1. AGENTS.md 核心原則新增 #8「啟動閘門」 ✅
  2. AGENTS.md 新增「啟動協議」含 Hard Gate ✅
  3. 協議含 DbC 三元組 ✅
- **守衛驗證證據**: 模擬「急迫任務」→ Hard Gate 要求先讀取 workflow-state.md → 無法繞過

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-011 | SESSION_START_BYPASS |
