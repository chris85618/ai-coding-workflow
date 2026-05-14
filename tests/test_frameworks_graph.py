"""Tests for StateGraph wiring."""
from agentic_workflow.frameworks.graph import (
    build_micro_validation_graph,
    build_iteration_graph,
    build_graph,
)

def test_build_micro_validation_graph():
    app = build_micro_validation_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None

def test_build_iteration_graph():
    app = build_iteration_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None

def test_build_graph():
    app = build_graph()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None
