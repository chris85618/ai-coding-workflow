"""TC-070: LangGraph adapter nodes exception handling path tests.

Verifies that all nodes correctly suppress exceptions and proceed gracefully when dependent services fail.
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

from agentic_workflow.adapters.langgraph.nodes import (
    node_agent_alpha_critique,
    node_agent_beta_resolve,
    node_phase_0_init,
    node_phase_1_understanding,
    node_phase_2_analysis,
    node_phase_9_ship,
    node_phase_10_retro,
    node_root_cause_leftshift,
    node_stage_6_formal,
    node_step_0_format,
    node_step_1_id_structure,
    node_step_6_trigger_impact,
)
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


def test_node_phase_0_init_exception() -> None:
    """Verifies node_phase_0_init exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", side_effect=Exception("mock error")):
        res = node_phase_0_init(state)
        assert res is state


def test_node_phase_1_understanding_exception() -> None:
    """Verifies node_phase_1_understanding exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.filesystem.get_filesystem", side_effect=Exception("mock error")):
        res = node_phase_1_understanding(state)
        assert res is state


def test_node_phase_2_analysis_exception() -> None:
    """Verifies node_phase_2_analysis exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.filesystem.get_filesystem", side_effect=Exception("mock error")):
        res = node_phase_2_analysis(state)
        assert res is state


def test_node_stage_6_formal_exception() -> None:
    """Verifies node_stage_6_formal exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    target_path = (
        "agentic_workflow.domain.algorithms.invariants_verifier."
        "DAGInvariantVerifier.run_all_verifications"
    )
    with patch(target_path, side_effect=Exception("mock error")):
        res = node_stage_6_formal(state)
        assert res is state


def test_node_phase_9_ship_exception() -> None:
    """Verifies node_phase_9_ship exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.filesystem.get_filesystem", side_effect=Exception("mock error")):
        res = node_phase_9_ship(state)
        assert res is state


def test_node_phase_10_retro_exception() -> None:
    """Verifies node_phase_10_retro exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.filesystem.get_filesystem", side_effect=Exception("mock error")):
        res = node_phase_10_retro(state)
        assert res is state


def test_node_agent_alpha_critique_exception() -> None:
    """Verifies node_agent_alpha_critique exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", side_effect=Exception("mock error")):
        res = node_agent_alpha_critique(state)
        assert res is state


def test_node_agent_beta_resolve_exception() -> None:
    """Verifies node_agent_beta_resolve exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", side_effect=Exception("mock error")):
        res = node_agent_beta_resolve(state)
        assert res is state


def test_node_root_cause_leftshift_exception() -> None:
    """Verifies node_root_cause_leftshift exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", side_effect=Exception("mock error")):
        res = node_root_cause_leftshift(state)
        assert res is state


def test_node_step_0_format_exception() -> None:
    """Verifies node_step_0_format exception handling."""
    # Using cast to trigger the attribute error in type-safe manner
    state = cast(Any, WorkflowState(pipeline_id="error-pipe", metadata=cast(Any, None)))
    res = node_step_0_format(state)
    assert res is state


def test_node_step_0_format_failure() -> None:
    """Verifies node_step_0_format failure path."""
    state = WorkflowState(
        pipeline_id="fail-pipe",
        metadata={"recent_changes_content": "some text from vibe here"}
    )
    res = node_step_0_format(state)
    assert res.get("gate_decision") == "fail"
    last_error = res.get("last_error")
    assert isinstance(last_error, str)
    assert "FORMAT_ERROR" in last_error


def test_node_step_1_id_structure_exception() -> None:
    """Verifies node_step_1_id_structure exception handling."""
    # Using cast to trigger the attribute error in type-safe manner
    state = cast(Any, WorkflowState(pipeline_id="error-pipe", metadata=cast(Any, None)))
    res = node_step_1_id_structure(state)
    assert res is state


def test_node_step_1_id_structure_failure() -> None:
    """Verifies node_step_1_id_structure failure path."""
    state = WorkflowState(
        pipeline_id="fail-pipe",
        metadata={"recent_changed_ids": ["INVALID-ID-123"]}
    )
    res = node_step_1_id_structure(state)
    assert res.get("gate_decision") == "fail"
    last_error = res.get("last_error")
    assert isinstance(last_error, str)
    assert "STRUCTURAL_ERROR" in last_error


def test_node_step_6_trigger_impact_exception() -> None:
    """Verifies node_step_6_trigger_impact exception handling."""
    state = WorkflowState(pipeline_id="error-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", side_effect=Exception("mock error")):
        res = node_step_6_trigger_impact(state)
        assert res is state


def test_node_root_cause_leftshift_pipeline_none() -> None:
    """Verifies node_root_cause_leftshift when pipeline is None."""
    state = WorkflowState(pipeline_id="none-pipe")
    mock_container = MagicMock()
    mock_container.pipeline_repo.get_by_id.return_value = None
    with patch("agentic_workflow.adapters.langgraph.nodes._get_container", return_value=mock_container):
        res = node_root_cause_leftshift(state)
        assert res is state
        mock_container.pipeline_repo.get_by_id.assert_called_once_with("none-pipe")
        mock_container.security_audit.audit_pipeline.assert_not_called()


def test_node_step_6_trigger_impact_partial_none() -> None:
    """Verifies node_step_6_trigger_impact when partial_state is None."""
    state = WorkflowState(pipeline_id="some-pipe")
    with patch("agentic_workflow.adapters.langgraph.nodes.node_impact_analysis", return_value=None):
        res = node_step_6_trigger_impact(state)
        assert res is state
