"""Frameworks Layer — StateMapper Shell.

This is a thin wrapper that imports and re-exports the StateMapper class from the adapters layer
to maintain backward compatibility and eliminate duplicate code.
"""

from __future__ import annotations

from agentic_workflow.adapters.langgraph.state_mapper.state_mapper import StateMapper

__all__ = ["StateMapper"]
