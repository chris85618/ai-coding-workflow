# Changelog

All notable changes to the **Unified Agentic Workflow** package are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.2.0] — 2026-07-07

### Summary
Repository scope consolidation & autonomous pipeline completion release.
Aggregates all work since 0.1.6 (kanban backlog fully landed) and narrows the repository to its executable-pipeline identity per ADR-STR-032.
1169 tests, 100.00% statement & branch coverage, Ruff/Mypy clean.

### Added
- **Design by Contract (ADR-STR-028)**: full migration icontract → `deal` (src 14 files, tests 12 files); contract-coverage gate TC-CONTRACT-005 (100% of domain concrete public methods carry contracts); contract-driven fuzzing suite `tests/test_contract_fuzz.py` (TC-FUZZ-001~011).
- **Formal verification**: `docs/formal/PipelineStateMachine.tla` (TC-TLA-001~005), `tests/formal/test_z3_invariants.py` (TC-Z3-001~005), `docs/formal/PipelineInvariants.v` with all theorems Qed-closed (TC-COQ-001~005); structural gates degrade gracefully when TLC/coqc are absent (ADR-GOV-017).
- **Archon engine-agnostic orchestration (ADR-STR-030)**: `IAgentOrchestratorGateway` port, `ArchonWorkflowMapper` (adapters), `ArchonOrchestrator` (frameworks) with graceful degradation when the archon CLI is missing (TC-ARCHON-001~008).
- **DSPy prompt optimization stack (ADR-STR-031)**: `IPromptOptimizer` port, `FewShotPromptOptimizer` fallback (adapters), `DSPyPromptOptimizer` (frameworks, optional extra); α/β node prompts routed through the optimizer.
- **Self-bootstrap (Ouroboros)**: `scripts/self_bootstrap.py` composition root runs the master graph end-to-end with real adapters (phase10/completed, gate pass); `OfflineReasoner` no-API-key degradation (FR-076, TC-BOOT-001~018); `ReadOnlyVersionControl` rollback guard by default.
- **SonarCloud tooling (SONAR-01~06)**: full metric/issue retrieval in `SonarCloudAdapter`; `scripts/fetch_sonar_metrics_detail.py`, `scripts/fetch_sonar_issues.py`; package-level `.pyi` type stubs for `langchain_openai`, `langchain_anthropic`, `sonarqube`, `z3`.
- **Frameworks quality guards (TC-QUALITY-004~011)**: AST-enforced NLOC ≤ 6, CC ≤ 2, nesting ≤ 1, single-return, inner-abstraction-only methods, no module-level functions in the frameworks layer.
- `docs/adr/ADR-STR-032.md` — repository scope consolidation decision record.
- **CI SBOM job (resolves DEBT-010)**: `.github/workflows/build.yml` now generates the CycloneDX SBOM dynamically via `cyclonedx-py environment` and uploads it as a build artifact.
- `README.md` — Optional Integrations section: DSPy extra (`pip install -e ".[dspy]"`) and Archon CLI install, both with documented graceful-degradation paths; `.archon/` added to `.gitignore`.

### Changed
- `README.md` — refreshed to current state: no submodules, Sphinx (not MkDocs), self-bootstrap quick start, scripts overview, current quality gates.
- `docs/ARCHITECTURE.md` — repository tree and key-files table realigned with the DDD/Clean Architecture layout.
- `config.yaml` — reviewer/left-shift prompts now reference the workflow protocol via `docs/ARCHITECTURE.md` instead of the removed AGENTS.md copy.
- `tasks/clean_architecture_scan.py` → `scripts/clean_architecture_scan.py` (CLI utilities consolidated under `scripts/`; `tasks/` removed).
- `docs/requirements.md` — NFR-002 (read-only submodules) and NFR-003 (AGENTS.md compatibility) marked SUPERSEDED by ADR-STR-032.
- **DEBT-008 ID collision resolved**: the register's type-ignore cleanup debt renumbered to DEBT-011, the matrix/retro Sonar-async debt renumbered to DEBT-012 (now also formally registered in the tech-debt register).

### Removed (ADR-STR-032)
- `skills/` git submodules (everything-claude-code, gstack, understand-anything, skillfortify) and `.gitmodules` — zero references from src/tests/CI/scripts.
- `AGENTS.md` repository copy — stale duplicate; the protocol's single source of truth lives in the framework repo (`$FRAMEWORK_ROOT`).
- `skill-lock.json`, `agentic-workflow.cdx.json` — stale supply-chain artifacts (SBOM regeneration tracked as DEBT-010).
- `test_ruff_include/`, `test_ruff_include_dir/`, `test_ruff_whitelist/` — orphaned experiment fixtures with zero references.
- `coverage_report.txt` — generated artifact removed from tracking (already gitignored).
- `kanban.md` — retired after verifying every item is reflected in `docs/workflow-state.md` WBS, ADRs, src, and tests.

---

## [0.1.6] — 2026-05-17

### Summary
Domain Governance & Persistence Hardening.
Semanticized governance algorithms and fully encapsulated LangGraph persistence via Repository Checkpointer.

### Added
- **Governance**: `OrchestratorService` and `SecurityAuditService` (Semantic Domain Services).
- **Persistence**: `RepositoryCheckpointer` (LangGraph ↔ Repository bridge).
- **Workflow**: `node_security_audit` integrated into the Master DAG.

### Fixed
- Decoupled Orchestrator from procedural dict-based logic to Pipeline aggregate.
- Wired LangGraph checkpointing to use the clean architecture `CheckpointRepository`.

## [0.1.5] — 2026-05-17

### Summary
Comprehensive Clean Architecture & DDD Hardening release.
Successfully completed the migration of core domain aggregates and application use cases with 100.00% test coverage and full static analysis (Ruff/Mypy) compliance.

### Added
- **Domain Layer**: `Pipeline` Aggregate Root, `Stage` Entity, and multiple Value Objects (`Findings`, `SymbolDef`, `TraceLink`, `TraceableIdVO`).
- **Application Layer**: Use Case encapsulation for all operations (`StartPipeline`, `AdvancePipeline`, `RunIteration`).
- **Infrastructure Layer**: `IPipelineRepository` port and `MarkdownPipelineRepository` adapter for document-based persistence.
- **Reasoning**: `IAgentReasoner` port and `AnthropicReasoner` adapter for LLM decoupling.
- **Tests**: 100% statement and branch coverage across the entire core package.
- **Granular Coverage**: Dedicated suites for abstract port interfaces and defensive error paths.

### Fixed
- Standardized all type-hinting and docstring issues across the repository (Ruff/Mypy clean).
- Resolved test suite environmental instability by hardening `DependencyContainer` initialization.
- Finalized alignment of LangGraph nodes with the Clean Architecture Use Case layer.

## [0.1.4] — 2026-05-16

### Summary
Domain-Driven Design (DDD) Refactoring release.
Surgically migrated from OOAD to a strict DDD architecture with proper Aggregates, Entities, and Value Objects.

### Changed
- `src/agentic_workflow/domain/` — Reorganized into `aggregates/`, `entities/`, and `value_objects/`.
- `Pipeline` — Refactored into the primary Aggregate Root with icontract-enforced invariants.
- `Stage` — Refactored into a Domain Entity managed by the `Pipeline` aggregate.
- `application/use_cases/` — Implemented explicit Use Case layer to encapsulate business logic.
- `tests/` — Fully realigned test suite hierarchy and terminology with DDD standards.

### Removed
- Legacy `models/` directory in both `src/` and `tests/`.

## [0.1.3] — 2026-05-16

### Summary
Granular Test Architecture & Quality Hardening release.
Implemented "One-Class-Per-File" testing model (FEA-024) and unified all configurations into `pyproject.toml` as SSOT.
789 unit tests, 100.00% coverage.

### Added
- Feature `FEA-024`: Granular Test Architecture (One-Class-Per-File) for improved modularity and maintenance.
- Feature `FEA-015`: `SonarCloudAdapter` providing real-time quality gate metrics via Web API.
- Feature `FEA-016`: `pyproject-mkdocs-plugin` for automated documentation metadata synchronization.
- Feature `FEA-021`: Hardened Mypy configuration within `pyproject.toml`.
- Feature `FEA-022`: Automated pre-commit formatting via Git hooks.

### Changed
- `tests/` directory — Complete hierarchical restructuring to mirror the `src/` production codebase.
- `pyproject.toml` — Consolidated all scattered tool settings into a single source of truth.
- `docs/macros.py` — Migrated from legacy `main.py` and implemented SEC-005 environment filtering.
- `README.md` — Refactored to act as a high-level entry point with cross-links to specialized docs.

### Fixed
- BDD collection errors by adopting `@staticmethod` pattern for scenario methods within test classes.
- Numerous namespace collisions and import file mismatch errors in the test suite.
- Type hint inconsistencies in `SonarCloudAdapter` and `ModelConfig`.


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
