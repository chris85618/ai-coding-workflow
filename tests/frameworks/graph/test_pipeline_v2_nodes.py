"""Tests for the Pipeline v2 framework node facades and routing (ADR-STR-029)."""

from typing import Any, cast
from unittest.mock import patch

from agentic_workflow.frameworks.graph import absorb_debt as absorb_debt_node
from agentic_workflow.frameworks.graph import (
    align_stage,
    check_fixed_point,
    inject_assumptions,
    rollback_universal_base,
    route_debt,
    update_constraints,
)
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class TestPipelineV2Nodes:
    """Covers v2 facade delegation and continuous-flow routing."""

    def test_align_stage_delegates_to_adapter_node(self) -> None:
        """TC-V2-056: align_stage forwards to node_align_check."""
        state = WorkflowState(pipeline_id="p")
        with patch("agentic_workflow.adapters.langgraph.nodes.node_align_check", return_value=state) as target:
            assert align_stage(state) is state
        target.assert_called_once_with(state)

    def test_rollback_delegates_to_adapter_node(self) -> None:
        """TC-V2-057: rollback_universal_base forwards to node_rollback."""
        state = WorkflowState(pipeline_id="p")
        with patch("agentic_workflow.adapters.langgraph.nodes.node_rollback", return_value=state) as target:
            assert rollback_universal_base(state) is state
        target.assert_called_once_with(state)

    def test_inject_delegates_to_adapter_node(self) -> None:
        """TC-V2-058: inject_assumptions forwards to node_inject_assumptions."""
        state = WorkflowState(pipeline_id="p")
        with patch("agentic_workflow.adapters.langgraph.nodes.node_inject_assumptions", return_value=state) as target:
            assert inject_assumptions(state) is state
        target.assert_called_once_with(state)

    def test_absorb_debt_delegates_to_adapter_node(self) -> None:
        """TC-V2-059: absorb_debt forwards to node_absorb_debt."""
        state = WorkflowState(pipeline_id="p")
        with patch("agentic_workflow.adapters.langgraph.nodes.node_absorb_debt", return_value=state) as target:
            assert absorb_debt_node(state) is state
        target.assert_called_once_with(state)

    def test_update_constraints_delegates_to_adapter_node(self) -> None:
        """TC-V2-060: update_constraints forwards to node_update_constraints."""
        state = WorkflowState(pipeline_id="p")
        with patch("agentic_workflow.adapters.langgraph.nodes.node_update_constraints", return_value=state) as target:
            assert update_constraints(state) is state
        target.assert_called_once_with(state)

    def test_route_debt_on_fail(self) -> None:
        """TC-V2-061: A FAIL gate routes into debt absorption."""
        assert route_debt(WorkflowState(pipeline_id="p", last_gate_decision="fail")) == "debt"

    def test_route_debt_on_pass(self) -> None:
        """TC-V2-062: A PASS gate continues the normal flow."""
        assert route_debt(WorkflowState(pipeline_id="p", last_gate_decision="pass")) == "pass"

    def test_check_fixed_point_routes_diverging_to_rollback(self) -> None:
        """TC-V2-063: A strictly growing findings trend routes to rollback."""
        history = cast(Any, [["a"], ["a", "b"], ["a", "b", "c"]])
        state = WorkflowState(
            pipeline_id="p",
            iteration_count=3,
            findings_history=history,
            current_findings=["HIGH: new issue"],
        )
        assert check_fixed_point(state) == "rollback"
