# ADR-GOV-024: 強制循序輸出協議

**狀態**: Accepted
**日期**: 2026-05-14
**決策者**: 人類 HITL
**追溯**: FR-001, FR-005, FR-019

---

## 背景

AI 在執行 Step 0-12 管線時，將「已通過 Gate 的 Step」和「不適用的 Step」靜默跳過，未在回覆中輸出任何標題行。使用者無法從回覆中驗證 AI 是否確實考慮了每個 Step。

## 決策

1. 在 AGENTS.md Core Directives 新增原則 #15：強制循序輸出
2. 在 Execution Protocol 區段新增「Step 輸出協議」，定義四種 STATUS 值
3. 在每個 Step 0-12 的定義中加入 `> **輸出**: 強制` 標注

## 後果

### 正面
- 使用者可從每次回覆驗證 AI 是否遍歷了所有 Step
- 靜默跳過行為不再可能：未輸出的 Step 立即可見為 GOVERNANCE_BYPASS
- 回覆結構標準化，便於 Meta-RCA 自檢

### 負面
- 回覆長度增加（每個 SKIP 行約 40 字元 × 最多 13 行）
- 對簡單任務可能顯得冗餘

### 風險
- RISK: 回覆過長導致 token 浪費 → 緩解：SKIP/N/A 行僅需標題行，不含內容

---

## LESSON

**LESSON-028**: AI 將「已通過 Gate 的 Step」靜默跳過，未在輸出中 acknowledge，導致使用者無法驗證管線完整性。

- **根因分類**: GOVERNANCE_BYPASS
- **瓶頸識別**: AGENTS.md 未明確要求「即使 Step 為 SKIP 也必須輸出標題行」。原則 #1「無簡化路徑」僅要求「執行」，未定義「輸出」的最低要求。
- **左移守衛**: Core Directives #15 + Step 輸出協議 + 每個 Step 的 `> **輸出**: 強制` 標注

---

## 變更紀錄

| # | 檔案 | 變更內容 | 分類 |
|---|------|---------|------|
| 1 | AGENTS.md | Core Directives #15 新增 | GOVERNANCE_RULE |
| 2 | AGENTS.md | Step 輸出協議段落新增 | GOVERNANCE_RULE |
| 3 | AGENTS.md | Step 0-12 各加 `> **輸出**: 強制` | GOVERNANCE_RULE |
| 4 | traceability-matrix.md | ADR-GOV-024 追溯新增 | TRACEABILITY |
| 5 | ADR-GOV-024.md | 本檔案建立 | ADR_CREATE |
