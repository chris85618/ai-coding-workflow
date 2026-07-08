"""Error path coverage for LangGraph nodes."""

from collections.abc import Generator

import pytest

from agentic_workflow.adapters.orchestration.nodes import (
    _get_container,
    node_advance_stage,
    node_iterate_stage,
    node_start_pipeline,
    set_container,
)
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


@pytest.fixture(autouse=True)
def reset_node_container() -> Generator[None, None, None]:
    """Ensure container is reset after each test."""
    yield
    set_container(None)


def test_get_container_uninitialized() -> None:
    """Cover the RuntimeError when container is missing."""
    set_container(None)
    with pytest.raises(RuntimeError, match="DependencyContainer not initialized"):
        _get_container()


def test_node_start_pipeline_error() -> None:
    """Cover exception path in node_start_pipeline."""
    # Ensure container is set but use case fails
    from unittest.mock import MagicMock

    container = MagicMock()
    container.start_pipeline.execute.side_effect = Exception("Start failed")
    set_container(container)

    state = WorkflowState(pipeline_id="p1")
    result = node_start_pipeline(state)
    assert result.get("last_error") == "Start failed"


def test_node_advance_stage_error() -> None:
    """Cover exception path in node_advance_stage."""
    from unittest.mock import MagicMock

    container = MagicMock()
    container.advance_pipeline.execute.side_effect = Exception("Advance failed")
    set_container(container)

    state = WorkflowState(pipeline_id="p1", last_gate_decision="pass")
    result = node_advance_stage(state)
    assert result.get("last_error") == "Advance failed"


def test_node_iterate_stage_error() -> None:
    """Cover exception path in node_iterate_stage."""
    from unittest.mock import MagicMock

    container = MagicMock()
    container.run_iteration.execute.side_effect = Exception("Iterate failed")
    set_container(container)

    state = WorkflowState(pipeline_id="p1")
    result = node_iterate_stage(state)
    assert result.get("last_error") == "Iterate failed"
