"""Tests for StateGraph wiring."""

from agentic_workflow.frameworks.graph import (
    IterationGraphBuilder,
    MasterGraphBuilder,
    MicroValidationGraphBuilder,
)


def test_build_micro_validation_graph() -> None:
    """TC-073: Build micro-validation graph."""
    app = MicroValidationGraphBuilder.build()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None


def test_build_iteration_graph() -> None:
    """TC-074: Build iteration graph."""
    app = IterationGraphBuilder.build()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None


def test_build_graph() -> None:
    """TC-075: Build master pipeline graph."""
    from unittest.mock import MagicMock

    from agentic_workflow.adapters.langgraph.nodes import set_container
    from agentic_workflow.frameworks.dependency_container import DependencyContainer

    # Initialize container with mocks to satisfy nodes
    container = DependencyContainer(
        pipeline_repo=MagicMock(),
        checkpoint_repo=MagicMock(),
        doc_io=MagicMock(),
        reasoner=MagicMock(),
    )
    set_container(container)

    app = MasterGraphBuilder.build()
    assert app is not None
    state = {"pipeline_id": "test", "stage_status": "pending"}
    res = app.invoke(state)
    assert res is not None
