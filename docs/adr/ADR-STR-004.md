# ADR-STR-004: AI Tool Feature Absorption — Strategy Pattern + Hooks + RepoMap

**Status**: Accepted
**Date**: 2026-05-14
**Category**: STR (Architecture)

## Context

Analysis of OpenCode, Aider, and Claude Code identified features that improve
our LangGraph system. User directives: absorb all except multi-agent parallel
and memory curation. Strategy Pattern is P0 for cost optimization.

## Decision

1. **Strategy Pattern LLM** (CLS-017, ALG-008): Deterministic model routing
   per task_type. Agent alpha uses reasoning model, beta uses editing model.
   Configurable per-project. Graceful degradation on disabled providers.
2. **RepoMap** (CLS-015, ALG-006): tree-sitter AST + PageRank for context.
3. **Lifecycle Hooks** (CLS-016): Deterministic enforcement at 4 lifecycle events.
4. **Atomic Git Commits**: Auto-commit via GitKraken MCP at stage completion.
5. **Context Budget** (ALG-007): Token budget allocation across context sources.
6. **REMOVED**: Multi-agent parallel (not supported), Memory curation (Step 12 handles).

## Consequences

- (+) Cost optimization via model routing
- (+) Better LLM context via RepoMap
- (+) Deterministic quality via hooks (ruff format/check)
- (+) Full git traceability via atomic commits
- (-) tree-sitter dependency added
- (-) networkx dependency added for PageRank

## Affected IDs

New: FR-026~030, NFR-008, UC-012/013, CLS-017/018, ALG-008,
INV-022~024, EVT-009/010, SC-012~016 (21 IDs total)
