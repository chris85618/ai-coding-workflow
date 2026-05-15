# ADR-STR-007: 單一建圖路徑 — OO Builder 為唯一合法圖建構方式

**Status**: Accepted
**Date**: 2026-05-15T22:03+08:00
**Category**: STR (Architecture)
**Supersedes**: ADR-STR-006 中的 workflow_graph 部分

## Context

原系統存在兩種建圖方式：
1. **OO Builder**（`frameworks/graph.py`）：硬性編碼的 Python 類別層次
2. **YAML 動態建圖**（`adapters/langgraph/graph_builder.py`）：讀取 `config.yaml` 的 `workflow_graph` 區段動態構建

這種「多條路徑」設計被識別為架構性危害，原因如下：

**根本問題**：允許 YAML 配置圖拓樸等同於允許在執行期「合法地重新定義流程」。
- LLM 自主代理在面對「多條合法路徑」時，會合理化省略治理步驟
- YAML 動態建圖本質上是一個「繞過 OO Builder 的後門」
- 任何「可選的執行路徑」最終都會在壓力下被選擇以省略步驟
- 這是使用者放棄 skill-based 架構的直接原因：LLM 持續利用彈性路徑跳過剛性限制

## Decision

**移除 YAML 動態建圖路徑，OO Builder 是唯一合法的建圖機制。**

具體決策：
1. 刪除 `src/agentic_workflow/adapters/langgraph/graph_builder.py`
2. 刪除 `tests/test_graph_builder.py`
3. 從 `config.yaml` 移除 `workflow_graph` 區段
4. 修訂 ADR-STR-006 scope：`config.yaml` 僅保留 `models` 和 `prompts` 區段
5. `invariants_verifier.py` 的 `__main__` 改為呼叫 `build_graph()`
6. BDD step definitions 更新為使用 `build_graph()`

**圖結構的唯一合法變更路徑**：
- 修改 `frameworks/graph.py` 中的 Builder 類別
- 建立對應 ADR（如本 ADR-STR-007）
- 通過完整的 Stage 3-8 治理管線驗證

## Consequences

- (+) 消除了「多條執行路徑」這個架構性危害
- (+) 任何圖拓樸變更必須通過代碼審查和 ADR 治理，不可繞過
- (+) LLM 代理無法在不修改受版本控制的 Python 程式碼的情況下改變流程
- (+) 強制嚴格執行全流程，符合使用者的最高優先原則
- (-) 圖拓樸修改需修改 Python 程式碼（這是正確的代價）

## FR/NFR Justification

- 抑制 RISK-004（AI 省略治理步驟的根本架構誘因）
- 強化 NFR-003（工作流剛性 — 所有步驟必須強制執行）
- LESSON-050（源自本次修正）：多條建圖路徑 = 允許流程跳過的架構授權
