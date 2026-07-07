# ADR-STR-031: DSPy Prompt 最佳化整合與論文導向設計映射

## 狀態
Accepted (2026-07-07)

## 背景
kanban TODO 要求：(1) 套 DSPy 最佳化 prompt；(2) 參考 SWE-agent、Live-SWE-agent、DAIRA、OpenHands、Constitutional Spec-Driven Development、LLMLOOP 改善專案設計；(3) 參考 EvoMAC、Voyager、Agent-RLVR 改善反思、迭代改善工作流、根因左移流程。

DSPy 的完整威力（MIPROv2 / teleprompter compile）需要已配置的 LM（API key）與訓練集。依 ADR-GOV-017「外部工具僅為加速器，核心流程具備純 LLM 降級路徑」，DSPy 必須為可選加速器而非硬依賴。

## 決策

### 1. Prompt 最佳化三層堆疊（FR-075）
- **Port（application）**：`IPromptOptimizer.optimize(base_prompt, examples) -> str` — prompt 最佳化成為可替換細節。
- **Adapters**：`FewShotPromptOptimizer` — 純字串 bootstrap few-shot（鏡射 DSPy LabeledFewShot 的結構），永遠可用的降級路徑。
- **Frameworks**：`DSPyPromptOptimizer` — dspy 已安裝時將示範例經 `dspy.Example` 正規化後渲染；未安裝時 `DSPyModuleLoader` 回傳 None 並降級至 few-shot adapter。teleprompter compile（需 LM）為文件化升級路徑。
- **注入點**：`DependencyContainer.prompt_optimizer`；`node_agent_alpha_critique` / `node_agent_beta_resolve` 的 prompt 一律經 optimizer，示範例取自 `metadata.prompt_examples`（Ouroboros/lesson 回注的天然掛載點）。
- **依賴宣告**：`pyproject.toml` optional-dependencies `dspy = ["dspy>=3.2"]`（opt-in，不增加基礎安裝重量）。

### 2. 論文 → 設計元素映射（透明盤點，LESSON-034）

| 論文/系統 | 核心概念 | 本專案對應設計 | 狀態 |
|-----------|---------|---------------|------|
| SWE-agent | Agent-Computer Interface（結構化 repo 視圖） | `RepoMapBuilder`（Phase 1 知識圖譜） | ✅ 既有 |
| Live-SWE-agent | 執行中自我演化、最小 scaffold | 動態債務迴圈（失敗即回饋，ADR-STR-029 #1） | ✅ 既有 |
| OpenHands | 事件流 + 沙箱化執行 | LangGraph state 事件流 + `SubprocessExecutor` port 隔離 | ✅ 既有 |
| Constitutional SDD | 憲法級約束前置注入（security by construction） | `node_inject_assumptions`（ASM-xxx 剛性注入，ADR-STR-029 #4） | ✅ 既有 |
| LLMLOOP | 自動化迭代回饋迴圈（code+tests） | 微驗證鏈 + α/β 迭代圖 + RCA 左移 | ✅ 既有 |
| DAIRA | 分工式代理角色 | Agent α（發散批判）/ Agent β（收斂整合） | ✅ 既有 |
| Self-Correction as Feedback Control | 誤差動力學、穩定性分析、發散偵測 | `ConvergenceDetector` 三向路由 + rollback 退化路徑（ADR-STR-029 #3）、`AlignmentChecker` 對齊迴圈（#5） | ✅ 既有 |
| EvoMAC | 文本反向傳播（測試失敗 → 更新 agent 指令） | align/gate 失敗回饋 Agent α 深度延伸（ADR-STR-029 #5） | ✅ 既有 |
| Voyager | 技能庫（skill library）與課程學習 | `metadata.prompt_examples` few-shot 示範庫 + LESSON 重用（FR-023）+ ASM 註冊表 | ✅ 本 ADR 補完掛載點 |
| Agent-RLVR | 可驗證獎勵（verifiable rewards）引導改善 | 品質閘門（coverage/ruff/mypy/sonar）作為客觀 reward signal 餵入債務迴圈 | ✅ 既有 |

**結論**：論文清單的概念已由 ADR-STR-029 的五項重構與本 ADR 的 prompt optimizer 堆疊全數覆蓋；Voyager 式技能庫以 `prompt_examples` 示範庫落地，供 Phase 10 retro 回填。

## 後果

### 正面
- Prompt 工程成為可替換、可測試的 port；DSPy 隨時可全量啟用（安裝 extra + 配置 LM）。
- α/β agent prompts 取得 lesson 回注的統一掛載點，Ouroboros 閉環延伸至 prompt 層。

### 負面 / 風險
- 未配置 LM 時 DSPy 路徑僅做示範例正規化（非 compile 級最佳化）；升級路徑已文件化。
- dspy 主版本演進可能改變 Example API；隔離於單一 frameworks 檔案。

## 追溯
- 上游: kanban TODO「套DSPy來最佳化prompt」「詳盡參考論文改善設計」、FEA-030、ADR-GOV-017
- 下游: FR-075、TC-DSPY-001~010
- 相關: ADR-STR-029（回饋控制迴圈）、ADR-STR-030（引擎無關化前例）、ADR-STR-027（DIP）
