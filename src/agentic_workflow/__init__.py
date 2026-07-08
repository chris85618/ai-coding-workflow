"""Agentic Workflow — Archon-orchestrated AI Coding Tool.

Transforms document-driven workflow orchestration into
autonomous Archon workflow execution with deterministic-first design
(ADR-STR-033: Archon is the sole orchestration engine).

Architecture: Clean Architecture (4 layers)
    - domain/   : Pure business logic, zero external deps
    - application/ : Use case interactors + port interfaces
    - adapters/  : orchestration nodes, MCP, LLM, file I/O
    - frameworks/ : Archon dispatch, config, DI, entry point
"""

__version__ = "0.1.0"
