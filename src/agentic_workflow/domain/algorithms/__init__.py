"""Pure deterministic algorithms — no LLM, no I/O.

OO Design: all algorithms implemented as classes (ALG-010 OO mandate).
Module-level facade functions retained for backward compatibility.

ALG-001: ConvergenceDetector (convergence — iteration fixed-point detection)
ALG-002: MicroValidation (6-step validation sequence)
ALG-003: BlastRadiusClassifier (impact graph traversal + severity)
ALG-004: RiceScorer (RICE prioritization formula)
ALG-005: trace_traversal (BFS/DFS graph algorithm — in traceability_validator)
ALG-006: RepoMapBuilder (tree-sitter AST + PageRank) — from Aider
ALG-007: ContextBudgetAllocator (token budget allocation) — from Aider
ALG-008: ModelSelector (Strategy Pattern for LLM model routing)
ALG-009: Markdown <-> JSON bidirectional conversion (future)
ALG-010: Stage 8 TDD skeleton-first protocol
"""
