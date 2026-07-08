# Workflow State — Unified Agentic Workflow System

**Pipeline Position**: Phase 10 (ADR-STR-033 完全切換 Archon；LangGraph 全面移除) — ✅ DONE
**Last Position**: Phase 10 (Repository 範圍收斂 ADR-STR-032; kanban 退役)
**Status**: HITL 決策落地（ADR-STR-030 Pending 解除 → ADR-STR-033 Accepted）：Archon 為唯一編排引擎、langgraph 依賴/模組/builders 全刪、單節點執行模型（NodeExecutor + scripts/run_node.py）、內部編排引擎禁令、確定型演算法零損失保留。1139 tests, 100.00% statement & branch coverage, Ruff/Mypy clean.
**Last Updated**: 2026-07-08

## ⏳ WBS (Work Breakdown Structure)

- [x] DDD-01: 建立 ADR-STR-020 (DDD 實施準則) — ✅ DONE
- [x] DDD-02: 建立 `Findings`, `RepoMap`, `SymbolDef` 等值物件 (VO) — ✅ DONE
- [x] DDD-03: 將 `Stage` 重構為實體 (Entity) 並移至 `entities/` — ✅ DONE
- [x] DDD-04: 將 `Pipeline` 重構為聚合根 (Aggregate Root) — ✅ DONE
- [x] DDD-05: 實作應用層 Use Cases (Start, Advance, RunIteration) — ✅ DONE
- [x] DDD-06: 更新 `StateMapper` 與 LangGraph `nodes.py` 對齊 DDD — ✅ DONE
- [x] DDD-07: 修復 100% 類型檢查 (Mypy) 與格式 (Ruff) 錯誤 — ✅ DONE
- [x] DDD-08: 移除 `src/` 下所有 Legacy `models/` 檔案 — ✅ DONE
- [x] DDD-09: 重構 `tests/` 下所有內容改用 DDD 術語與結構 — ✅ DONE
- [x] DDD-10: 修復 `Pipeline` 與 `StateMapper` 的覆蓋率缺口 (100% Coverage) — ✅ DONE
- [x] CAD-01: 建立 ADR-STR-021 (Clean Architecture 深度對齊) — ✅ DONE
- [x] CAD-09: 語意化 Orchestrator 與 SecurityAudit 領域服務 — ✅ DONE
- [x] CAD-10: 實作 RepositoryCheckpointer 並接入 LangGraph — ✅ DONE
- [x] CAD-11: 更新測試套件對齊新 DI 結構 (828 Tests Pass) — ✅ DONE
- [x] CAD-02: 提煉 `TraceableIdVO` 與 `Findings` VO — ✅ DONE
- [x] CAD-03: 實作 `IPipelineRepository` 與 `MarkdownPipelineRepository` — ✅ DONE
- [x] CAD-04: 建立 `DependencyContainer` 並重構 Use Cases 依賴注入 — ✅ DONE
- [x] CAD-05: 隔離 LLM 邏輯至 `IAgentReasoner` Port — ✅ DONE
- [x] CAD-06: 重構 `nodes.py` 使用 DI 與通用語言 (Alpha/Beta) — ✅ DONE
- [x] CAD-07: 實作 `AnthropicReasoner` Adapter — ✅ DONE
- [x] CAD-08: 重構 `ImpactAnalysis` 為 Domain Service — ✅ DONE
- [x] CAD-09: 重構 `BlastRadius` 為 Specification — ✅ DONE
- [x] CAD-10: 補齊 DI Container 與 Use Case 單元測試 — ✅ DONE
- [x] LLM-01: 擴充 Domain `ModelConfig` VO 支援 `base_url` — ✅ DONE
- [x] LLM-02: 擴充 Framework `ModelConfig` Pydantic 支援 `base_url` — ✅ DONE
- [x] LLM-03: 修改 `OpenAIProvider` 整合 `base_url` — ✅ DONE
- [x] LLM-04: 更新測試案例驗證自定義 Endpoint 注入 — ✅ DONE
- [x] LLM-05: 更新 `config.yaml` 範例與 `.env.example` — ✅ DONE
- [x] CAD-12: 徹底重構 `nodes.py` 與 `sonar_adapter.py` 以使用 `SonarCloudConfig` 與 `InvariantsConfig` 依賴反轉，消除全域 singleton — ✅ DONE
- [x] CAD-13: 修正 Mock 引起的 truthiness 問題，以真實 value objects 取代測試中的 MagicMock 確保可靠測試 — ✅ DONE
- [x] CAD-14: 達成 100.00% 程式碼覆蓋率與 842 個測試案例全數通過，Mypy 與 Ruff 無 any 錯誤 — ✅ DONE
- [x] CAD-15: 徹底移除 domain/algorithms/invariants_verifier.py 中 frameworks 之外層動態 imports，並於 frameworks/graph/ 下建立獨立 invariants_run.py 指令碼以符合依賴反轉原則，100% 覆蓋通過 — ✅ DONE
- [x] CAD-16: 建立 `CleanArchitectureBoundaryScanner` 類別，透過 AST 靜態掃描架構層級依賴關係 — ✅ DONE
- [x] CAD-17: 實作 8 大違規偵測類別（包含靜態/動態 imports, 類型標註, sys.modules, DI 容器濫用, 環境變數, 直接檔案 I/O） — ✅ DONE
- [x] CAD-18: 建立 16 個涵蓋全面違規模式與正常場景之測試套件 `test_clean_architecture_scanner.py` — ✅ DONE
- [x] CAD-19: 建立 CLI 執行指令碼 `tasks/clean_architecture_scan.py` 以利 pipeline 整合與主動防護 — ✅ DONE
- [x] CAD-20: 成功重構 Domain 層違規演算法並達成生產 Codebase 0 violations 狀態，專案 857 個測試案例 100% 通過 — ✅ DONE
- [x] CAD-21: 改善 AST 掃描器測試覆蓋率，消除 AST subscript / type annotations / walk filters 所有分支缺口，達成 100.00% statement 與 branch 完美覆蓋且完全不使用 pragma no cover — ✅ DONE
- [x] CAD-22: 改善 AST Scanner 嵌套相對/絕對導入 (ImportFrom) 解析邏輯，確保其完整解析，並新增 `pydantic` 白名單消除 domain 層誤判 violations — ✅ DONE
- [x] CAD-24: 重新設計導入路徑並移除 checkpointer 中所有 `# type: ignore`，100% 通過 Mypy 與 Ruff — ✅ DONE
- [x] CAD-25: 修改 ADR-STR-027 與技術債登錄表，正式宣示全面絕對禁止 `# type: ignore`（0 Exceptions） — ✅ DONE
- [x] CAD-26: 全面擴展白名單白名單至內三層（Domain/Application/Adapters），並重構 `adapters/filesystem.py` 與 `adapters/subprocess.py` 去除 OS 依賴。 — ✅ DONE
- [x] CAD-27: 生產環境（`src/`）全面 eradication 所有 `# type: ignore`，100% 通過 Mypy。 — ✅ DONE
- [x] CAD-28: 排除測試覆蓋率缺口，執行 `fget` 測試反射以達成測試套件 919 案 100.00% Statement 與 Branch 全面覆蓋。 — ✅ DONE
- [x] CAD-29: 消除測試套件中所有 Mypy 類型錯誤且完全不使用 `# type: ignore`，確保測試的高強度類型安全性。 — ✅ DONE
- [x] CAD-30: 修改 AST 掃描器硬化 "# type" 與 "# pragma" 封鎖規則，實現內三層 100% 絕對禁用所有 type 註解， entry point 以外 100% 禁用所有 pragma 註解 — ✅ DONE
- [x] CAD-31: 補齊 scanner 所有註解後綴 Permutations 測試，測試套件 920 案 100.00% Statement 與 Branch 覆蓋無死角且通過 Ruff/Mypy 檢驗 — ✅ DONE
- [x] CAD-32: 硬化 "# type" 與 "# pragma" 封鎖規則，實現內三層 100% 絕對禁用所有 type 註解， entry point 以外 100% 禁用所有 pragma 註解，修正靜態掃描邏輯並達成 fallback 程式碼 100% Statement 與 Branch 覆蓋無死角且通過 Ruff/Mypy 檢驗 — ✅ DONE
- [x] CAD-33: 在 `tests/test_code_quality.py` 中實現 Ruff Check 與 Mypy pytest 自動化測試，防範不退化 — ✅ DONE
- [x] CAD-34: 實施 DEBT-009 自動化 AST 檢查並修復 SonarAdapterProtocol 覆蓋率缺口，完美維持 100.00% 覆蓋與 0 type: ignore/pragma/ellipsis 違規 — ✅ DONE
- [x] SONAR-01: 於 SonarCloudAdapter 實作 get_all_available_metrics、get_detailed_component_measures 與 get_all_metrics_with_values 方法 — ✅ DONE
- [x] SONAR-02: 在 tests/adapters/test_adapters_coverage.py 中新增對應測試以確保 100% Statement 與 Branch 覆蓋 — ✅ DONE
- [x] SONAR-03: 撰寫 scripts/fetch_sonar_metrics_detail.py 工具指令碼以支援所有指標及其對應細節的 Markdown 格式拉取與美化輸出 — ✅ DONE
- [x] SONAR-04: 實作拉取 Sonar 既有 issue 腳本 scripts/fetch_sonar_issues.py 並落實 100% 覆蓋 — ✅ DONE
- [x] SONAR-05: 修復 Sonar 偵測出的 6 筆嚴重問題，並硬化測試套件至 970 個測試 100.00% Coverage 通過 — ✅ DONE
- [x] SONAR-06: 導入 `types-requests` 依賴並為 `langchain_openai`, `langchain_anthropic`, `sonarqube` 建立封裝套件層級 `.pyi` 類型存存根，實現 100% 潔淨 Mypy / Ruff 綠燈 — ✅ DONE
- [x] CAD-35: 實作 frameworks layer 不要包含領域邏輯之 6 項 pytest 靜態檢查 AST 演算法與檢驗機制 (TC-QUALITY-004 ~ TC-QUALITY-009) — ✅ DONE
- [x] CAD-36: 對 frameworks/ 下指定檔案進行系統性重構，完全滿足 NLOC <= 6、CC <= 2 等 6 大品質守衛門檻 — ✅ DONE
- [x] CAD-37: 實作方法必須實作內層抽象的方法之 pytest AST / 動態雙重反射檢驗機制 (TC-QUALITY-010) — ✅ DONE
- [x] CAD-38: 實作 frameworks layer 中禁止存在任何模組層級（class 之外）的 function 或 async function 定義之 pytest AST 靜態檢查 (TC-QUALITY-011) — ✅ DONE
- [x] CAD-39: 修正 file_repository.py 與 llm/providers 中 NLOC > 6 的 NLOC 違規，將方法行數嚴格縮限至 6 行以內 — ✅ DONE
- [x] CAD-40: 修正 OSFilesystemIO, OSSubprocessExecutor, AnthropicReasoner, UrllibHttpClient, AnthropicProvider, OpenAIProvider 之中方法 override 與繼承關係 violations (TC-QUALITY-010)，100% 通過品質檢查 — ✅ DONE
- [x] CAD-41: 修正 workflow_config.py 中的 Mypy 類型安全、Cyclomatic Complexity (<= 2) 與 Branch count (<= 1) 違規，確保 100% 綠燈 — ✅ DONE
- [x] CAD-42: 修復 file_repository.py 中的 _to_dict, _from_dict 與 filesystem_io.py 中的 class_symbol 使得 NLOC <= 6 且單一 return 語意 100% 通過品質檢查 — ✅ DONE
- [x] CAD-43: 修復 nodes.py 中所有剩餘分支覆蓋率缺口，達成 1004 案 100.00% Statement 與 Branch 覆蓋無死角 — ✅ DONE
- [x] CAD-44: 系統性修正框架骨架節點實作，包含實體領域狀態完全未被推進的 Unwired Use Cases (Start, Advance, RunIteration) — ✅ DONE
- [x] CAD-45: 解決 Passive Passthroughs 痛點，串聯大腦運算核心，並引入安全合約 (DbC) 以保障防禦性編程 — ✅ DONE
- [x] CAD-46: 建立雙 Agent (Alpha/Beta) 與 RCA RCA/左移驗證，克服微驗證與 RCA 失去控制 — ✅ DONE
- [x] CAD-47: 確保 1023 個測試案例 100.00% Coverage (Statement & Branch) 通過與 Ruff/Mypy 檢驗 — ✅ DONE
- [x] DEAL-01: icontract → deal 全面遷移（src 14 檔、tests 12 檔、pyproject、docs/conf.py），移除 sphinx-icontract/pyicontract-lint/icontract-hypothesis 並解除 hypothesis/astroid pin — ✅ DONE
- [x] DEAL-02: snapshot/OLD 合約重設計（Stage.transition 用 ensure+reason；Pipeline.advance 用前驅 PASSED 後置條件），INV-016 以 _default_stages factory 左移至 setattr 強制 — ✅ DONE
- [x] DEAL-03: 建立 ADR-STR-028 並改寫 docs/formal-verification-spec.md v4（INV-001..024 全面 deal 化） — ✅ DONE
- [x] DEAL-04: TC-CONTRACT-001~004 遷移至 deal lint / deal.cases / crosshair --analysis_kind deal — ✅ DONE
- [x] CC-01: 建立 TC-CONTRACT-005 合約覆蓋率閘門（deal.introspection 掃描 domain concrete public methods），紅燈起步 — ✅ DONE
- [x] CC-02: 為 domain 80 個未合約化方法系統性補齊 pre/ensure/post/inv/has 合約，覆蓋率 8/88 → 83/83 (100%) — ✅ DONE
- [x] FUZZ-01: 建立 tests/test_contract_fuzz.py (TC-FUZZ-001~011) deal.cases 合約驅動模糊測試套件 — ✅ DONE
- [x] FUZZ-02: 修復模糊測試發現的 BlastRadiusClassifier.classify 負數輸入合約缺口（左移 deal.pre 基數約束） — ✅ DONE
- [x] ARC-01: 建立 src/z3/__init__.pyi 型別存根修復 test_mypy_type_safety（沿用 SONAR-06 stub 慣例） — ✅ DONE
- [x] ARC-02: 實作 ArchonWorkflowMapper (adapters/archon) 純字串 YAML 映射 — ✅ DONE
- [x] ARC-03: 實作 ArchonOrchestrator (frameworks) 經 FilesystemIO/SubprocessExecutor 匯出與派發，無 archon CLI 時優雅降級 — ✅ DONE
- [x] ARC-04: DependencyContainer.agent_orchestrator 注入點 + TC-ARCHON-001~008 — ✅ DONE
- [x] COQ-01: 建立 docs/formal/PipelineInvariants.v（5 定理全 Qed 封閉）+ tests/formal/test_coq_proof_gate.py (TC-COQ-001~005) — ✅ DONE
- [x] DSPY-01: 建立 IPromptOptimizer port + FewShotPromptOptimizer (adapters 降級) + DSPyPromptOptimizer (frameworks) — ✅ DONE
- [x] DSPY-02: α/β 節點 prompt 統一經 prompt_optimizer（metadata.prompt_examples 掛載點）+ TC-DSPY-001~010 + ADR-STR-031 — ✅ DONE
- [x] BOOT-01: 建立 OfflineReasoner (adapters/llm) 無 API key 純降級推理器 (FR-076) — ✅ DONE
- [x] BOOT-02: 建立 scripts/self_bootstrap.py 組合根（真實 adapters、rollback 預設唯讀防護） — ✅ DONE
- [x] BOOT-03: 根因修復 MarkdownPipelineRepository stub → 真 round-trip 持久化（TC-BOOT-005~009） — ✅ DONE
- [x] BOOT-04: 根因修復 advance 語意錯位 → AdvancePipelineUseCase.execute_to 位置對齊 + phase9/10 推進 + complete 聚合持久化（TC-BOOT-010~018） — ✅ DONE
- [x] BOOT-05: 自舉管線端對端執行驗證（phase10/completed/gate pass、stage3-8 各 1 次 α/β 迭代、無錯誤無 rollback） — ✅ DONE
- [x] ARCX-01: 建立 ADR-STR-033（HITL 解除 ADR-STR-030 Pending：Archon 唯一引擎、內部引擎禁令、演算法保留）+ ADR-STR-002/030 狀態更新 — ✅ DONE
- [x] ARCX-02: LangGraph 全面移除（frameworks/graph×7、frameworks/langgraph×5、gateways/graph_builder 刪除；adapters/langgraph → adapters/orchestration 更名；pyproject 移除 langgraph 依賴） — ✅ DONE
- [x] ARCX-03: 單節點執行模型落地（NodeExecutor + NODE_REGISTRY/ROUTER_REGISTRY + scripts/run_node.py；無邊無序列無迴圈，排程權威在匯出文件） — ✅ DONE
- [x] ARCX-04: ArchonWorkflowMapper 完整主管線拓撲（α/β loop、fixed-point/HITL/debt 條件路由、rollback 路徑、quality gate）+ self_bootstrap 改道 export→dispatch — ✅ DONE
- [x] ARCX-05: 測試套件遷移收尾（7 收集錯誤修復、退役 LangGraph 測試×8 刪除、BDD 改綁 archon_workflow.feature、TC-ARCHON-009~021 新增、set_container 洩漏根因修復 teardown） — ✅ DONE
- [x] ARCX-06: 品質閘門全綠（TC-QUALITY-014/015 違規修復、invariants_run 豁免規則更新、殘留 _autosummary 清除、1139 tests 100.00% coverage、Ruff/Mypy 潔淨） — ✅ DONE


## 🚦 Gate Status

- [✅] Phase 0: 環境啟動
- [✅] Phase 1: 程式碼理解
- [✅] Phase 2: 專案分析
- [✅] Stage 3: 技術規劃 (ADR-STR-025)
- [✅] Stage 4: 演算法設計
- [✅] Stage 5: OOAD + 安全審計 (Clean Architecture compliance audit)
- [✅] Stage 6: 形式化驗證設計 (Boundary rules invariants)
- [✅] Stage 7: BDD/ATDD
- [✅] Stage 8: TDD + 測試 + 修復 (1023 Pass, 100.00% Statement & Branch Coverage)
- [✅] Phase 10: 反思與學習 (Clean Architecture Boundary Hardened) — ✅ DONE

## 📌 Pending Escalations

- 無

## 📝 Session Summary

-2. **完全切換 Archon (2026-07-08, ADR-STR-033)**: HITL 解除 ADR-STR-030 Pending 項——接受領域節點外部化、Archon 唯一編排引擎、LangGraph 全面淘汰、內部編排引擎禁令、確定型演算法全數保留。實作：單節點執行模型（NodeExecutor/node_registry/run_node.py，無邊無序列）、mapper 生成完整主管線 Archon YAML（loop/route/when 構件承載拓撲，路由判定仍為行程內確定型演算法）、self_bootstrap 改道 export→dispatch（無 fallback runner）、DAGInvariantVerifier 改繫匯出拓撲。測試側：8 個退役測試刪除、BDD 改綁 archon_workflow.feature、TC-ARCHON-009~021 新增、set_container 全域洩漏根因修復。登錄：FR-077/078、RISK-006 (AC)、矩陣合計 370→375。1139 tests、100.00% coverage、Ruff/Mypy 潔淨。
-1. **治理修正 + CI SBOM (2026-07-07 續)**: DEBT-008 ID 碰撞以雙重編號解決（register type-ignore 債 → DEBT-011；matrix/retro Sonar 異步債 → DEBT-012 並補登 register）；DEBT-010 以 build.yml `sbom` job（cyclonedx-py 動態生成 + artifact 上傳）解決；README 新增 DSPy/Archon 選用整合章節（兩者均自動偵測、優雅降級，config.yaml 零改動相容）；`.archon/` 進 .gitignore。
0. **Repository 範圍收斂 (2026-07-07, ADR-STR-032)**: kanban.md 逐條驗證全數反映後退役刪除；移除零引用的框架宿主殘留（skills/ 子模組×4 + .gitmodules、過期 AGENTS.md 副本、skill-lock.json、agentic-workflow.cdx.json、test_ruff_* 孤兒 fixtures×3、被追蹤的 coverage_report.txt）；tasks/ 併入 scripts/（CLI 高內聚）；NFR-002/003 標記 SUPERSEDED；新增 DEBT-010 (P3, SBOM CI 再生)；README/CHANGELOG(0.2.0)/ARCHITECTURE 全面對齊現況。
1. **Kanban TODO 全數完成 (2026-07-07)**: Archon 引擎無關化實作落地 (ADR-STR-030 Implemented)、DSPy prompt 最佳化三層堆疊 + 論文映射 (ADR-STR-031)、Coq 定理閘門補完 TLA+/Z3 形式化矩陣、SonarQube 資料利用與 NFR 左移確認既有完成。
2. **自舉管線端對端驗證 (Ouroboros 實證)**: scripts/self_bootstrap.py 以真實 adapters 組合 container 跑通 master graph 至 phase10/completed，並在過程中根因修復三個 skeleton 缺陷（MarkdownPipelineRepository stub 持久化、advance 位置錯位、complete 節點不持久化）。
3. **降級路徑補完**: OfflineReasoner (無 API key)、ReadOnlyVersionControl (自舉防 rollback)、DSPy/archon CLI 缺席時全部優雅降級 (ADR-GOV-017)。
4. **品質閘門全綠**: 1169 tests、100.00% statement & branch coverage、Ruff/Mypy/format 潔淨、合約覆蓋率閘門與模糊測試保持通過。

