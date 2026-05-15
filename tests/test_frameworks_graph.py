"""Tests for StateGraph wiring."""

from agentic_workflow.frameworks.graph import (
    build_graph,
    build_iteration_graph,
    build_micro_validation_graph,
)


def test_build_micro_validation_graph() -> None:
    """TC-073: Build micro-validation graph."""
    app = build_micro_validation_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None


def test_build_iteration_graph() -> None:
    """TC-074: Build iteration graph."""
    app = build_iteration_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None


def test_build_graph() -> None:
    """TC-075: Build master pipeline graph."""
    app = build_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None
