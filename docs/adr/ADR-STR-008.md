# ADR-STR-008: Token Budget & Long Response Continuation Mechanism

## 1. 狀態與背景

* **狀態**: Accepted
* **日期**: 2026-05-15
* **受影響範圍**: `llm_adapter.py`, `orchestrator.py`
* **FR 追溯**: FR-034

### 背景與現狀問題
目前在使用 LLM 生成內容時，若模型的輸出超過 `max_tokens` (如 4096 tokens)，API 會中斷生成並回傳 `finish_reason="length"` 或 `stop_reason="length"`。
現有的 `LangChainLLMAdapter` 與 `AstraflowProvider` 機制下，系統僅將被截斷的字串原樣返回。由於 LangGraph 節點依賴此輸出進行後續解析（如 JSON 反序列化或 Markdown 抽取），這通常會導致 `JSONDecodeError`，隨後被 Agent 迴圈當作一般格式錯誤而盲目重試，浪費時間與 Token 預算。

### 為什麼原本這樣處理？
1. **無狀態抽象**：Adapter 層為簡化設計，通常作為無狀態的 API 封裝，不主動干預上下文管理。
2. **格式隔離**：無法確定當前任務類型是否適合直接字串拼接（例如拼接 JSON 可能破壞語法）。

## 2. 決策

針對長回覆場景建立「動態且具備任務意識的 Token 應對機制」（Token Continuation Mechanism）：

1. **偵測層 (Detection)**:
   在 `LangChainLLMAdapter.complete` 攔截 `finish_reason` / `stop_reason` 是否為 `length` 或 `max_tokens`。
2. **策略層 (Task-Aware Strategy)**:
   * **策略 A: 自動續寫 (Auto-Continuation)**:
     針對純文字、Markdown 等非嚴格結構化任務 (`TaskType.CRITIQUE`, `TaskType.COMPREHEND`, `TaskType.CHARTER`)，由 Adapter 自動發送 `HumanMessage` ("Response truncated due to length. Please continue exactly where you left off...")，並將多次結果字串無縫拼接。設定最大續寫次數 `max_continuations=3` 以防無限迴圈。
   * **策略 B: 快速失敗與攔截 (Fast-Fail for Structured Data)**:
     針對需要保證語法完整的任務 (`TaskType.RESOLVE`, `TaskType.FORMAT`)，直接拋出 `TokenLimitExceededError`。交由 LangGraph 的錯誤恢復機制或 Agentic Loop，以 Prompt 策略指導 LLM 進行「分塊輸出」或重構要求，避免破壞 JSON 語法。

## 3. 結果與影響

* **優點**: 
  - 長文本生成不再無故斷尾或拋出無意義的 Parser Error。
  - 結構化資料透過 `TokenLimitExceededError` 獲得精確的例外處理與 RCA 線索。
* **缺點**: 
  - 自動續寫可能會增加 token 消耗，但受限於 `max_continuations` 閥值，風險可控。
