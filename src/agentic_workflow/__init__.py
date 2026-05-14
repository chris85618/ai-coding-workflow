"""Agentic Workflow — LangGraph-based AI Coding Tool.

Transforms document-driven workflow orchestration into
autonomous LangGraph DAG execution with deterministic-first design.

Architecture: Clean Architecture (4 layers)
    - domain/   : Pure business logic, zero external deps
    - application/ : Use case interactors + port interfaces
    - adapters/  : LangGraph nodes, MCP, LLM, file I/O
    - frameworks/ : Graph wiring, config, DI, entry point
"""

__version__ = "0.1.0"
