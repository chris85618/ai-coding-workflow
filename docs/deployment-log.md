# Deployment Log

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
