"""Additional test cases to achieve 100% test coverage for LangGraph adapter nodes.

Traceable to: FR-001, FR-012, FR-013, FR-019-v2, ADR-STR-002, ADR-STR-003.
"""

from collections.abc import Generator
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from agentic_workflow.adapters.langgraph.nodes import (
    node_agent_beta_resolve,
    node_root_cause_leftshift,
    node_step_2_forward_trace,
    node_step_3_backward_trace,
    node_step_4_semantic,
    node_step_5_5_lateral_trace,
    node_step_5_7_lesson_reuse,
    node_step_5_orphan,
    node_step_6_trigger_impact,
    node_step_7_record_change,
    set_container,
)
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


@pytest.fixture(autouse=True)
def cleanup_container() -> Generator[None, None, None]:
    """Ensure container is reset after each test."""
    yield
    set_container(None)


def test_node_agent_beta_resolve_success() -> None:
    """Covers node_agent_beta_resolve success path with container."""
    container = MagicMock()
    container.reasoner.reason.return_value = "Done"
    set_container(container)

    state = WorkflowState(pipeline_id="p1", current_findings=["RCA"], iteration_count=1, metadata={})
    res = node_agent_beta_resolve(state)
    assert res["iteration_count"] == 2
    assert res["metadata"]["recent_resolution"] == "Done"


def test_node_root_cause_leftshift_fail_path() -> None:
    """Covers node_root_cause_leftshift when gate_decision is fail."""
    container = MagicMock()
    mock_pipeline = MagicMock()
    container.pipeline_repo.get_by_id.return_value = mock_pipeline
    set_container(container)

    state = WorkflowState(pipeline_id="p1", gate_decision="fail", last_error="FORMAT_ERROR in line 1", metadata={})

    mock_fs = MagicMock()
    with patch("agentic_workflow.adapters.filesystem.get_filesystem", return_value=mock_fs):
        res = node_root_cause_leftshift(state)
        assert res is not None
        assert "rca_result" in res["metadata"]
        assert mock_fs.write_text.called


def test_node_step_2_forward_trace_fail() -> None:
    """Covers forward trace failure and exception handling."""
    # Failure condition: Invalid ID format (no '-' character or wrong subclass)
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["INVALID-ID-123"]})
    res = node_step_2_forward_trace(state)
    assert res.get("gate_decision") == "fail"

    # Exception path: mock TraceabilityValidator.validate_id_format to raise Exception
    with patch(
        "agentic_workflow.domain.algorithms.traceability_validator.traceability_validator.TraceabilityValidator.validate_id_format",
        side_effect=Exception("validator error"),
    ):
        state_err = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
        res_err = node_step_2_forward_trace(state_err)
        assert "validator error" in (res_err.get("last_error") or "")


def test_node_step_3_backward_trace_fail() -> None:
    """Covers backward trace failure and exception handling."""
    # Exception path: mock TraceabilityNode to raise Exception
    with patch(
        "agentic_workflow.domain.algorithms.traceability_validator.traceability_node.TraceabilityNode",
        side_effect=Exception("node error"),
    ):
        state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
        res = node_step_3_backward_trace(state)
        assert "node error" in (res.get("last_error") or "")


def test_node_step_3_backward_trace_no_downstream() -> None:
    """Covers backward trace failure path when there is no downstream."""
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"], "has_downstream": False})
    res = node_step_3_backward_trace(state)
    assert res.get("gate_decision") == "fail"
    assert "No downstream" in (res.get("last_error") or "")


def test_node_step_4_semantic_fail() -> None:
    """Covers semantic failure (invalid subclass) and exception handling."""
    # Failure path: Invalid ADR subclass
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["ADR-FOO-001"]})
    res = node_step_4_semantic(state)
    assert res.get("gate_decision") == "fail"
    assert "Invalid ADR subclass" in (res.get("last_error") or "")

    # Exception path: metadata of invalid type to raise Exception
    state_err = WorkflowState(pipeline_id="p1", metadata=cast(Any, 123))
    res_err = node_step_4_semantic(state_err)
    assert "object has no attribute" in (res_err.get("last_error") or "")


def test_node_step_5_orphan_exception() -> None:
    """Covers orphan node exception handling."""
    with patch(
        "agentic_workflow.domain.algorithms.traceability_validator.traceability_validator.TraceabilityValidator.orphan_check",
        side_effect=Exception("orphan error"),
    ):
        state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
        res = node_step_5_orphan(state)
        assert "orphan error" in (res.get("last_error") or "")


def test_node_step_5_orphan_fail() -> None:
    """Covers orphan node failure path."""
    with patch(
        "agentic_workflow.domain.algorithms.traceability_validator.traceability_validator.TraceabilityValidator.orphan_check",
        return_value=["BG-001"],
    ):
        state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
        res = node_step_5_orphan(state)
        assert res.get("gate_decision") == "fail"
        assert "Orphans detected" in (res.get("last_error") or "")


def test_node_step_5_5_lateral_trace_fail() -> None:
    """Covers lateral trace failure and exception handling."""
    # Failure path: RISK lacks lateral link
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["RISK-001"], "has_nfr_link": False})
    res = node_step_5_5_lateral_trace(state)
    assert res.get("gate_decision") == "fail"

    # Exception path
    state_err = WorkflowState(pipeline_id="p1", metadata=cast(Any, 123))
    res_err = node_step_5_5_lateral_trace(state_err)
    assert "object has no attribute" in (res_err.get("last_error") or "")


def test_node_step_5_7_lesson_reuse_enum_fallback() -> None:
    """Covers lesson reuse fallback for invalid enum and exception handling."""
    # Fallback path: Invalid enum string
    state = WorkflowState(pipeline_id="p1", metadata={"rca_result": {"category": "INVALID_ENUM_STRING"}})
    res = node_step_5_7_lesson_reuse(state)
    # Falls back to FORMAT_ERROR, and tries check_lesson_reuse with it
    # No error is raised
    assert res is not None

    # Exception path
    with patch(
        "agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_leftshift.RootCauseLeftShift.check_lesson_reuse",
        side_effect=Exception("reuse error"),
    ):
        res_err = node_step_5_7_lesson_reuse(state)
        assert "reuse error" in (res_err.get("last_error") or "")


def test_node_step_7_record_change_exception() -> None:
    """Covers record change exception handling."""
    state_err = WorkflowState(pipeline_id="p1", metadata=cast(Any, 123))
    res = node_step_7_record_change(state_err)
    assert "does not support item assignment" in (res.get("last_error") or "")


def test_node_step_2_forward_trace_success() -> None:
    """Covers forward trace success branch (gate_decision is not set)."""
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
    res = node_step_2_forward_trace(state)
    assert res.get("gate_decision") is None


def test_node_step_3_backward_trace_success() -> None:
    """Covers backward trace success and non-BG/S id branch."""
    # Omit BG-/S- IDs, pass FEA-001 which bypasses the startswith check
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["FEA-001"], "has_downstream": True})
    res = node_step_3_backward_trace(state)
    assert res.get("gate_decision") is None

    # Pass BG-001 with has_downstream=True (covers not not node.downstream)
    state2 = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"], "has_downstream": True})
    res2 = node_step_3_backward_trace(state2)
    assert res2.get("gate_decision") is None


def test_node_step_4_semantic_success() -> None:
    """Covers semantic success branch."""
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["ADR-STR-001"]})
    res = node_step_4_semantic(state)
    assert res.get("gate_decision") is None


def test_node_step_5_5_lateral_trace_success() -> None:
    """Covers lateral trace success and non-RISK id branch."""
    # Omit RISK- IDs, pass BG-001 which bypasses the startswith check
    state = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["BG-001"]})
    res = node_step_5_5_lateral_trace(state)
    assert res.get("gate_decision") is None

    # Pass RISK-001 with has_nfr_link=True
    state2 = WorkflowState(pipeline_id="p1", metadata={"recent_changed_ids": ["RISK-001"], "has_nfr_link": True})
    res2 = node_step_5_5_lateral_trace(state2)
    assert res2.get("gate_decision") is None


def test_node_step_5_7_lesson_reuse_no_match() -> None:
    """Covers lesson reuse no match branch."""
    state = WorkflowState(pipeline_id="p1", metadata={"rca_result": {"category": "COVERAGE_GAP"}})
    res = node_step_5_7_lesson_reuse(state)
    # Check that metadata does not contain reused_lesson_id since category is COVERAGE_GAP
    assert "reused_lesson_id" not in res.get("metadata", {})


def test_node_step_6_trigger_impact_no_partial() -> None:
    """Covers trigger impact when partial_state is None or raises Exception."""
    # When partial_state is None
    with (
        patch("agentic_workflow.adapters.langgraph.nodes._get_container"),
        patch(
            "agentic_workflow.adapters.langgraph.nodes.node_impact_analysis",
            return_value=None,
        ),
    ):
        state = WorkflowState(pipeline_id="p1")
        res = node_step_6_trigger_impact(state)
        assert res is not None

    # When Exception is raised
    with (
        patch("agentic_workflow.adapters.langgraph.nodes._get_container"),
        patch(
            "agentic_workflow.adapters.langgraph.nodes.node_impact_analysis",
            side_effect=Exception("mocked impact exception"),
        ),
    ):
        state2 = WorkflowState(pipeline_id="p1")
        res2 = node_step_6_trigger_impact(state2)
        assert res2 is not None


def test_node_step_6_trigger_impact_success() -> None:
    """Covers trigger impact success branch when partial_state is returned."""
    with (
        patch("agentic_workflow.adapters.langgraph.nodes._get_container"),
        patch(
            "agentic_workflow.adapters.langgraph.nodes.node_impact_analysis",
            return_value={"gate_decision": "pass"},
        ),
    ):
        state = WorkflowState(pipeline_id="p1")
        res = node_step_6_trigger_impact(state)
        assert res.get("gate_decision") == "pass"
