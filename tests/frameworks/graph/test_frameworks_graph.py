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

    mock_pipeline = MagicMock()
    mock_pipeline.pipeline_id = "test"
    mock_pipeline.status.value = "running"
    mock_pipeline.current_position = "stage3"

    mock_gate = MagicMock()
    mock_gate.value = "pass"
    mock_pipeline.last_gate_decision = mock_gate

    mock_stage = MagicMock()
    mock_stage.iteration_count = 0
    mock_stage.stage_id = "stage3"
    mock_stage.status.value = "pending"
    mock_pipeline.stages = {"stage3": mock_stage}
    mock_pipeline.id = "test"
    import typing

    typing.cast(MagicMock, container.pipeline_repo).get_by_id.return_value = mock_pipeline

    try:
        set_container(container)
        app = MasterGraphBuilder.build()
        assert app is not None
        state = {"pipeline_id": "test", "stage_status": "pending"}
        res = app.invoke(state)
        assert res is not None
    finally:
        set_container(None)
