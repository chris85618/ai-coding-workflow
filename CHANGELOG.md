# Changelog

All notable changes to the **Unified Agentic Workflow** package are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.1.2] — 2026-05-15

### Summary
架構強化版本。依 ADR-STR-007 移除 YAML 動態建圖路徑，強制 OO Builder 為唯一合法建圖機制。
636 unit tests, 100.00% coverage.

### Removed (Breaking Change — Architecture)
- `src/agentic_workflow/adapters/langgraph/graph_builder.py` — YAML 動態建圖模組已刪除
- `tests/test_graph_builder.py` — 對應測試已刪除
- `config.yaml` 的 `workflow_graph` 區段 — 圖拓樸不再可外部配置

### Changed
- `docs/adr/ADR-STR-006.md` — scope 縮窄至 models+prompts，排除 graph topology
- `src/agentic_workflow/domain/algorithms/invariants_verifier.py` — `__main__` 改為呼叫 `build_graph()` (OO Builder)
- `tests/test_invariants_verifier.py` — mock patch 路徑更新
- `tests/step_defs/test_langgraph_dag.py` — 全部改為使用 `build_graph()`
- `README.md` — 移除方式 B、Self-Bootstrap YAML 路徑、更新 Key Decisions 表格

### Added
- `docs/adr/ADR-STR-007.md` — 新建 ADR：單一建圖路徑原則

### Rationale (ADR-STR-007)
允許多條建圖路徑等同於允許 LLM 代理在面對壓力時合法化地選擇省略治理步驟。
此為使用者放棄 skill-based 架構的直接根因：彈性路徑最終必然導致流程跳過。

---

## [0.1.1] — 2026-05-15

### Summary
Post-production minor release of the LangGraph-based autonomous coding workflow system.
234 unit tests, 97.40% test coverage, Traceability Matrix features gap filled.

### Added
- Feature `FEA-012` and associated traceabilities (FR-031/032, UC-014/015, SC-017/018) for deterministic markdown-JSON conversion and external YAML configuration.
- Additional test cases covering MCP network timeout handling, LLM adapter provider mocking, and file repository path traversal boundary checks.

---

## [0.1.0] — 2026-05-15

### Summary
Initial production release of the LangGraph-based autonomous coding workflow system.
217 unit tests, 99% line+branch coverage, all P1+ technical debt resolved.

### Added

#### Domain Layer (Hexagonal Core)
- `domain/models/`: `Pipeline`, `Stage`, `TraceableID` + `TraceLink`, `RepoMap` + `SymbolDef`, `ModelConfig`, `HookEvent` enums (FR-001~FR-007, FR-009~FR-011)
- `domain/algorithms/`: 6 deterministic algorithms — convergence (ALG-001), context_budget (ALG-002), blast_radius (ALG-003), rice_scoring (ALG-004), model_selector (ALG-008), repo_map_builder (ALG-006)
- `domain/services/`: `HookRunner` (CLS-016) + `LLMStrategySelector` (CLS-017)
- `domain/contracts/`: icontract-based Design-by-Contract invariants (INV-001~INV-025)

#### Application Layer
- `application/ports/`: `PipelineRepository`, `CheckpointRepository`, `TraceableIDRepository`, `SequentialThinkingGateway`, `GitKrakenGateway`, `LLMGateway`, `DocumentIO` (FR-019~FR-030)

#### Adapter Layer
- `adapters/persistence/`: `FilePipelineRepository`, `FileCheckpointRepository`, `FileTraceableIDRepository`, `MarkdownDocumentIO`, `HookConfigLoader`
- `adapters/events/`: `InMemoryEventBus`
- `adapters/llm/`: `LLMAdapter` (OpenAI/Anthropic via LangChain)
- `adapters/mcp/`: `SequentialThinkingMCPAdapter`, `GitKrakenMCPAdapter`
- `adapters/langgraph/`: `WorkflowGraph` DAG + `StateMapper` (FEA-010, FR-031~FR-033)

#### Security Hardening (DEBT-004 — OWASP Layer 1~3)
- **SEC-001**: `hook_runner.py` — `subprocess` `shell=True` → `shlex.split` + list args; shell metachar sanitization
- **SEC-002**: `markdown_writer.py` — path traversal guard via `Path.relative_to(repo_root)` (raises `ValueError: SEC-002`)
- **SEC-003**: `file_repository.py` — ID sanitization (`..` → `__`, `/` → `_`) + directory escape check (raises `ValueError: SEC-003`)
- **SEC-004**: `sequential_adapter.py` — SSRF URL scheme whitelist (https for remote, http localhost-only; raises `ValueError: SEC-004`)

#### Supply Chain Security (DEBT-004)
- `skill-lock.json` — SkillFortify lockfile for Agent Skills (ECC)
- `agentic-workflow.cdx.json` — CycloneDX SBOM for Python dependencies

#### Test Suite
- 221 unit + BDD tests across 15 test files
- 99.04% line + branch coverage (up from initial 0%)
- Security regression suite (`test_security_fixes.py`): 18 tests for SEC-001~004
- Boundary branch suite (`test_repo_map_coverage.py`, `test_coverage_gap_fill.py`): 57 gap-fill tests

#### Governance
- `docs/requirements.md` — FR-001~FR-033, NFR-001~NFR-012, UC-001~UC-012
- `docs/algorithm-specs.md` — ALG-001~ALG-008 formal specifications
- `docs/invariants.md` — INV-001~INV-025 icontract-enforced invariants
- `docs/bdd-scenarios.md` — SC-001~SC-012 BDD/Gherkin scenarios
- `docs/traceability-matrix.md` — End-to-end BG→FEA→FR→UC→SC→TC traceability
- `docs/tech-debt-register.md` — DEBT-001~DEBT-005 registry (DEBT-001~004 resolved, DEBT-005 deferred)
- `docs/risk-register.md` — RISK-001~RISK-003 (all mitigated)
- `docs/adr/` — ADR-STR-001~004, ADR-SEC-001, ADR-GOV-001~006

### Technical Debt Status
| ID | Title | Status |
|----|-------|--------|
| DEBT-001 | icontract invariant stubs | ✅ Resolved |
| DEBT-002 | Adapter layer implementation | ✅ Resolved |
| DEBT-003 | repo_map_builder boundary branches | ✅ Resolved |
| DEBT-004 | Layer 1-3 security audit | ✅ Resolved |
| DEBT-005 | SonarCloud CI gate | ⏸️ Deferred (post v0.1.0) |

### Dependencies
- Python 3.12+
- `icontract` ≥ 2.7 (Design-by-Contract)
- `langgraph` ≥ 0.2 (DAG orchestration)
- `langchain-openai`, `langchain-anthropic` (LLM adapters)
- `pytest`, `pytest-bdd`, `pytest-cov` (test suite)

---

[0.1.0]: https://github.com/chris85618/My-Dotfiles/releases/tag/v0.1.0
