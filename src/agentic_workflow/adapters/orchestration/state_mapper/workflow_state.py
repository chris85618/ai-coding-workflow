"""Adapter Layer — WorkflowState TypedDict.

Traceable to: FR-019-v2, FR-021-v2, UC-001, UC-010, ADR-STR-033
Defines the canonical engine-neutral state schema for the agentic pipeline.
"""

from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """State dictionary for the workflow pipeline.

    All fields are optional (total=False) so nodes can return
    partial updates that are merged into the checkpointed state.
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
    findings_history: list[list[str]]
    current_findings: list[str]
    gate_decision: str | None
