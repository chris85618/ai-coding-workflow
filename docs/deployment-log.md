# Deployment Log

## [0.1.7] — 2026-05-18T22:57+08:00
- **Pipeline Position**: Phase 9 (Release & Deployment)
- **Branch**: `master`
- **Changes**: Concrete framework graph nodes logic implemented, replacing passthroughs. Integrated DbC, dual-agent iteration loops, and RCA left-shift checks.
- **Validation**: 1023 tests passed, reaching exactly 100.00% statement and branch coverage without single type:ignore/pragma.

## [0.1.6] — 2026-05-17T05:51+08:00
- **Pipeline Position**: Phase 11 (Feature Implementation)
- **Branch**: `master`
- **Changes**: FEA-029 (OpenAI-compatible Provider support), extended ModelConfig and OpenAIProvider with `base_url`.
- **Validation**: TC-LLM-021 verified, all tests passed. ADR-STR-023 accepted.

## [0.1.5] — 2026-05-16T20:45+08:00
- **Pipeline Position**: Phase 10 -> 11 Transition
- **Branch**: `master`
- **Changes**: Coverage hardening (100% coverage reached), Use Case test alignment.
- **Validation**: 787 tests passed. All quality gates green.

## [0.1.4] — 2026-05-16T19:54+08:00
- **Pipeline Position**: Phase 10
- **Branch**: `master`
- **Changes**: DDD refactoring (Aggregates, Entities, Use Cases).
- **Validation**: Refactored test suite passes. Architectural consistency verified.

## [0.1.3] — 2026-05-16T18:55+08:00
- **Pipeline Position**: Phase 9 -> 10 Transition
- **Branch**: `main`
- **Changes**: FEA-024 (Granular Test Architecture), FEA-015 (SonarCloud Adapter), FEA-016 (MkDocs Plugin), SSOT config consolidation.
- **Validation**: All 789 tests passed. 100.00% coverage. Mypy/Ruff/SonarCloud quality gates verified.
- **Rollback Plan**: Revert to v0.1.2 tag.

## [0.1.1] — 2026-05-15T02:24+08:00
- **Pipeline Position**: Phase 9 -> 10
- **Branch**: `langgraph-coding`
- **Changes**: Added deterministic markdown parsing and YAML configuration. Pushed test coverage to 97.40%.
- **Validation**: All 234 tests passed. Security bounds tested.
- **Rollback Plan**: Revert commit if upstream integration fails.

## [0.1.0] — 2026-05-15T01:00+08:00
- **Pipeline Position**: Phase 9
- **Branch**: `langgraph-coding`
- **Changes**: Initial autonomous coding workflow framework.
- **Validation**: All 217 tests passed, 99.04% coverage.
