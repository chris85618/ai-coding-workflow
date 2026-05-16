"""Adapter Layer — WorkflowState TypedDict for LangGraph.

Traceable to: FR-019-v2, FR-021-v2, UC-001, UC-010, ADR-STR-002
Defines the canonical LangGraph state schema for the agentic pipeline.
"""

from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """LangGraph state dictionary for the workflow pipeline.

    All fields are optional (total=False) so partial updates work
    correctly with LangGraph's reducer system.
    """

    pipeline_id: str
    pipeline_status: str
    current_position: str
    last_gate_decision: str | None
    current_stage_id: str | None
    stage_status: str | None
    iteration_count: int
    max_iterations: int
    last_error: str | None
    metadata: dict[str, Any]
