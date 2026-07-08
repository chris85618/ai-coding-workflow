# ADR-STR-033: 完全切換至 Archon — 唯一編排引擎與 LangGraph 全面移除

**狀態**: Accepted; Verified against real archon CLI v0.5.0 (2026-07-08) — mapper 對齊真實 nodes-DAG schema（`steps:` 格式已被 CLI 拒絕），`archon validate workflows` 通過，沙箱 dispatch 實證 7 個確定型 bash 節點（inject→stage3）成功執行、checkpoint round-trip 正常；AI loop 節點需 `CLAUDE_BIN_PATH` + archon 憑證（RISK-006 範疇）
**日期**: 2026-07-07
**決策者**: HITL（使用者最終決策，解除 ADR-STR-030 Pending 項）+ Agent α/β 收斂
**追溯**: FEA-030, FR-073, FR-074, FR-077, FR-078, ADR-STR-030 (partially superseded), ADR-STR-002 (superseded), ADR-GOV-017, LESSON-034, RISK-006

---

## Context

ADR-STR-030 完成引擎無關化（`IAgentOrchestratorGateway` port、`ArchonWorkflowMapper`、`ArchonOrchestrator`），但將「完全切換至 Archon」標記為 Pending HITL，因為該切換等於接受「領域節點外部化」的架構取捨。

2026-07-07 使用者做出最終 HITL 決策：

1. **接受**領域節點外部化的取捨。
2. Archon 的功能**全面替代** LangGraph，成為唯一編排引擎。
3. LangGraph **全面淘汰移除**。
4. **禁止**所有內部自行撰寫的編排引擎（自寫或引入其他編排引擎，不如繼續用 LangGraph — 即本決策否決任何中間路線）。
5. 既有的**所有確定型演算法設計均需保留**（ALG-001 α/β 迭代迴圈、ALG-002 微驗證、ConvergenceDetector、DebtAccumulator、AlignmentChecker、RollbackPolicy、TraceabilityValidator、RootCauseLeftShift 等）。

技術現實（ADR-STR-030 已查證）：Archon 是外部 CLI 編排平台（YAML 工作流，支援迴圈、條件、閘門），非 Python 函式庫，無法在行程內執行領域節點。

## Decision

1. **編排拓撲唯一定義於 Archon YAML**：`ArchonWorkflowMapper`（adapters，純字串邏輯）從 domain canonical order（`Pipeline` aggregate，SSOT）生成完整主管線工作流：inject → start → phase 0-2 → stage 3-8（每個 stage 一個 α/β 迭代迴圈區塊，以 Archon 原生 loop/until 構件表達）→ sonar gate → 條件式 debt 吸收 → security audit → 條件式 debt 吸收 → phase 9 → phase 10 → update constraints → complete。條件路由（route_debt、check_fixed_point、hitl_gate_choice）以 Archon condition 構件承載，判定邏輯仍由行程內確定型演算法執行（見 2）。
   - **真實 schema 對齊（2026-07-08 驗證）**：目標為 archon CLI v0.5.0 的 nodes-DAG 格式（唯一合法格式）——序列以 `depends_on` 鏈、α/β 迴圈以 `loop`（收斂由 `until_bash` 執行行程內 `check_fixed_point` 確定型判定，非 AI 輸出）、條件路由以 `when: "$node.output == '...'"`、HITL 閘門以原生 `approval` 節點、debt 連續流以 `trigger_rule: none_failed_min_one_success` 表達。文件寫入 `.archon/workflows/<name>.yaml`，派發指令 `archon workflow run <name>`。self-bootstrap 語意固定 `worktree.enabled: false`（在目標 repo 上執行；rollback 由 ReadOnlyVersionControl 防護）。
2. **單節點執行模型（確定型演算法保留）**：每個 Archon step 執行 `python scripts/run_node.py --node <name> --pipeline-id <id>`。`NodeExecutor`（adapters/orchestration）載入 checkpoint 狀態 → 執行**恰好一個**節點函式（呼叫既有 use cases / domain algorithms，一行不改）→ 持久化狀態。路由節點以 stdout 輸出路由名供 Archon 條件消費。`NodeExecutor` 無邊、無序列、無迴圈 — 不構成編排引擎。
3. **LangGraph 全面移除**：
   - `frameworks/graph/`（MasterGraphBuilder、IterationGraphBuilder、MicroValidationGraphBuilder 與其節點包裝）刪除；stage 節點的 position 設定包裝與 route_debt 併入 `adapters/orchestration`。
   - `frameworks/langgraph/`（RepositoryCheckpointer 等 LangGraph 橋接）刪除；跨行程狀態改由既有引擎中立的 `FileCheckpointRepository` 承載。
   - `adapters/langgraph/` 更名為 `adapters/orchestration/`（nodes、StateMapper、WorkflowState 均為引擎中立邏輯，原樣保留）。
   - `application/ports/gateways/graph_builder.py`（LangGraph 形狀的 builder ports）刪除；`IAgentOrchestratorGateway` 為唯一編排 port。
   - `pyproject.toml` 移除 `langgraph` 依賴（`langchain-core` 保留 — 由 LLM providers 使用，與編排無關）。
4. **內部編排引擎禁令**：禁止任何 Python 端 YAML 直譯器、graph runner、步驟序列器。`archon` CLI 不可用時的降級路徑（ADR-GOV-017）為：匯出工作流文件 + 逐步以 `run_node.py` 執行（由人或 AI 依 YAML/AGENTS.md 協議推進）— 排程權威永遠在匯出文件，不在 Python 程式碼。
5. **自舉入口改道**：`scripts/self_bootstrap.py` 不再 in-process invoke master graph，改為 export workflow → `archon run` dispatch；dispatch 失敗時透明報告降級（不偽裝成功、不 fallback 到內部 runner）。
6. **形式化驗證目標改繫**：`DAGInvariantVerifier` 的驗證對象由 compiled LangGraph 改為匯出的工作流拓撲/WorkflowState（INV 不變量本身不變）。

## Consequences

- **正面**：編排引擎徹底成為可替換細節；主管線可由外部 agent fleet 執行；`src/` 內不再有任何引擎綁定的圖構建程式碼；所有確定型演算法（domain/application 層）零損失保留且仍受 100% 覆蓋率、合約（deal）、Coq/Z3 閘門保護。
- **負面（HITL 已明示接受）**：
  - 行程內端對端自舉（BOOT-05 的 in-process 驗證模式）退場；端對端執行依賴外部 `archon` 二進位。無 archon 時只能逐步執行（登錄 RISK-006）。
  - 跨節點排程的 DbC 強制（如 stage 順序推進）由 LangGraph 邊移轉到 Archon YAML + 節點內 `AdvancePipelineUseCase` 的 deal 合約雙重防線；行程間狀態一致性依賴 checkpoint round-trip。
  - Archon YAML schema 由外部版本控制；演進風險隔離於 `ArchonWorkflowMapper` 單一檔案（沿 ADR-STR-030）。
- **中性**：`WorkflowState`/`StateMapper`/全部節點函式僅換包名（`adapters.orchestration`），行為與測試語意不變。

## 替代方案（已否決）

- **雙引擎並存（ADR-STR-030 現狀）**：HITL 明示否決 — Archon 必須唯一。
- **自寫輕量 graph runner 替代 LangGraph**：違反本決策第 4 點禁令（「不如繼續用 LangGraph」）。
- **引入其他編排引擎（Temporal/Prefect 等）**：同上禁令。
