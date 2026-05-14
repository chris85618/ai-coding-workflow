# ADR-STR-003: Autonomous Execution Model (No HITL Gates)

**Status**: Accepted
**Date**: 2026-05-14
**Category**: STR (Architecture)
**Supersedes**: FR-014 (HITL convergence confirmation)

## Context

The original workflow design used Human-in-the-Loop (HITL) gates at every
stage exit to ensure quality. This design was appropriate for a document-driven
orchestration model where AI agents read Markdown skills.

With the migration to LangGraph (ADR-STR-002), the system becomes an
AI coding tool that runs the full pipeline in one shot. HITL gates would
break the autonomous execution flow and defeat the purpose of a tool
that "runs and produces results."

## Decision

1. Remove all HITL gates from the pipeline and iteration loops.
2. Replace `hitl_gate()` with `auto_gate()` (deterministic: fixed-point → PASS).
3. MAJOR-severity impacts are logged as warnings, not escalated to humans.
4. Max-iteration breaches auto-advance with warnings, not force-HITL.
5. Users correct errors by running the tool again with updated input.

## Consequences

- (+) Full pipeline runs autonomously in one shot
- (+) Simpler DAG: no interrupt/resume points for human input
- (+) Faster execution: no blocking waits
- (+) User errors are corrected iteratively (run again)
- (-) No human safety net during execution
- (-) Warnings may be missed if not surfaced in output docs
- (-) Quality depends entirely on LLM + deterministic algorithm quality

## Affected IDs

BG-003, FEA-005, FEA-010, FR-013, FR-014(superseded), FR-019(superseded),
FR-021(superseded), UC-003, UC-010, CLS-001, CLS-003, CLS-013,
INV-002(v2), INV-005(v2), ALG-001, EVT-001, EVT-006, SC-001, SC-003, SC-010

## Mitigation

- All warnings are written to `docs/warnings.md` in target repo
- Stage artifacts document what assumptions were made
- User can inspect output docs and re-run with corrections
