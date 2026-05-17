"""Frameworks Layer — WorkflowState TypedDict Shell.

This is a thin wrapper that imports and re-exports the WorkflowState TypedDict from the adapters layer
to maintain backward compatibility and eliminate duplicate code.
"""

from __future__ import annotations

from agentic_workflow.adapters.langgraph.state_mapper.workflow_state import WorkflowState

__all__ = ["WorkflowState"]
