# ADR-STR-030: Archon 編排整合策略 — 引擎無關化而非直接替換 LangGraph

## 狀態
Accepted (2026-07-06) — 完全切換至 Archon 之最終決策標記為 **Pending HITL**
Implemented (2026-07-07) — `ArchonWorkflowMapper`（adapters/archon）、`ArchonOrchestrator`（frameworks）、`DependencyContainer.agent_orchestrator` 注入點與 TC-ARCHON-001~008 已落地；LangGraph 仍為行程內預設引擎

## 背景
kanban TODO 要求「全面改用 https://archon.diy/ 而非 LangGraph」。經調查（archon.diy, 2026-07）：

- Archon 是**外部 CLI 編排平台**：以 YAML 定義多步驟工作流（支援迴圈、條件、閘門），透過 terminal/Slack/GitHub/web 派發 **coding agents**（Claude Code、Codex 等），每次執行使用獨立 git worktree，產出 PR。
- Archon **不是 Python 函式庫**：無法在行程內執行本專案的領域節點（micro-validation、convergence detector、traceability validator 等純 Python 演算法）。
- 安裝方式為 `curl -fsSL https://archon.diy/install | bash`（外部二進位、需網路）。

**範圍限定詞保護（LESSON-034）**：「全面改用」在技術上等於放棄行程內領域邏輯執行模型 — 所有 Stage 節點退化為「派發給外部 coding agent 的 prompt」，DbC/不變量/微驗證鏈將不在編排引擎內強制。此為架構層級的重大取捨，不得暗中決定。

## 決策

1. **引擎無關化（立即執行）**：
   - Application 層新增 `IAgentOrchestratorGateway` port：`export_workflow()`（將主管線匯出為外部編排文件）與 `dispatch()`（派發執行）。
   - Adapters 層 `ArchonWorkflowMapper`：純字串邏輯，將 canonical stage 順序映射為 Archon YAML 工作流（worktree 隔離、每 stage 一步、品質閘門步驟）。
   - Frameworks 層 `ArchonOrchestrator` 實作 port：經 `FilesystemIO` 寫出 YAML、經 `SubprocessExecutor` 呼叫 `archon run`（DIP，ADR-STR-027；無 archon 二進位時 dispatch 回傳 False，優雅降級 ADR-GOV-017）。
   - `DependencyContainer.agent_orchestrator` 提供注入點。
2. **LangGraph 保留為行程內預設引擎**：領域邏輯執行、測試、100% 覆蓋率閘門全數依賴行程內模型；Archon 作為「外層派發模式」並存。
3. **完全切換 → Pending HITL**：需人類確認接受「領域節點退化為 agent prompts」的取捨後，才將 master graph 執行路徑切至 Archon。

## 後果

### 正面
- 主管線可一鍵匯出為 Archon 工作流（自舉管線可由外部 agent fleet 執行）。
- 編排引擎成為可替換細節（Clean Architecture 的本意）；未來任何編排平台只需新增一個 gateway 實作。
- 未偷偷縮小範圍：完全切換的成本與風險透明呈報。

### 負面 / 風險
- Archon YAML schema 由外部版本控制，映射器需隨其演進（隔離於單一 adapter 檔案）。
- 雙引擎並存期間，工作流語意需以 domain 為單一事實來源（stage 順序取自 Pipeline aggregate 的 canonical order）。

## 追溯
- 上游: kanban TODO「全面改用 Archon」、FEA-030、ADR-GOV-017（優雅降級）、LESSON-034（範圍限定詞保護）
- 下游: FR-073（工作流匯出）、FR-074（外部派發）、TC-ARCHON-001~008
- 相關: ADR-STR-002（LangGraph 選型）、ADR-STR-027（DIP）
