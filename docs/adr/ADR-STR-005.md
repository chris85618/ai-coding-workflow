# ADR-STR-005: Markdown ↔ JSON 雙向轉換策略 (確定型優先與 LLM 輔助)

**Status**: Accepted
**Date**: 2026-05-15
**Category**: STR (Architecture)

## Context

系統的單一事實來源（SSOT）是 Markdown 文件（如 `docs/` 下的各類矩陣與規格），但 LangGraph 與外部 LLM 之間資料傳遞必須依賴結構化的 JSON。
當系統需要讀取 Markdown 並將其轉換為狀態機內的 JSON 格式時，有兩種主要方法：
1. 全面交由 LLM 解析（容錯率高，但可能產生幻覺、成本高、執行慢）。
2. 使用正規表達式或解析器（確定型演算法，快速、便宜，但在面對不規則 Markdown 格式時容易失敗）。

此外，系統必須確保從 JSON 寫回 Markdown 時，不會遺失原有的任何細節。

## Decision

我們決定採用 **「確定型演算法優先，LLM 輔助容錯」** 的混合策略：
1. **確定型解析優先 (Deterministic First)**：實作 `ALG-009 MarkdownParser`，利用 Python (如 `marko` 或自建 Regex 狀態機) 解析標準 Markdown Table、Headers 等結構化元素。
2. **結構驗證**：解析結果必須符合預定義的 Pydantic 結構。
3. **LLM 輔助容錯 (LLM Fallback)**：當且僅當確定型解析失敗（格式不吻合）時，將 Markdown 原始碼與期望的 JSON Schema 送給 LLM（較便宜的模型），請求其進行修復並輸出 JSON。
4. **增量更新寫回 (AST-based Update)**：將 JSON 寫回 Markdown 時，不覆寫全檔，而是定位到特定的 Table 或 Section 進行「節點替換」，保留人工撰寫的註解與上下文。任何結構性變更均需執行「根因左移 (Root-Cause Left-Shift)」以提示格式規範。

## Consequences

- (+) 確保大部分情況下零 Token 消耗、執行速度快。
- (+) 兼顧了高容錯度（LLM Fallback），確保工作流不會因為人類在 Markdown 中多打了一個空格而崩潰。
- (+) 增量寫回保留了既有要求。
- (-) 必須維護一套強健的 Markdown AST 更新演算法（ALG-009）。

## FR/NFR Justification

- FR-031 (Markdown ↔ JSON 雙向轉換能力)
- NFR-009 (轉換容錯與一致性保證)
- 遵循 ADR-GOV-016 (務實簡潔性) 與 ADR-GOV-017 (LLM 原生與優雅降級)
