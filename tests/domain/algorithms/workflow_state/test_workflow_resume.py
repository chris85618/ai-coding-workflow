"""Test suite for workflow resumption algorithms (ALG-001)."""

from typing import Any

from agentic_workflow.domain.algorithms.workflow_resume import WorkflowResume


class TestWorkflowResume:
    """Test suite for workflow resumption algorithms."""

    def test_load_state_returns_dict(self) -> None:
        """TC-036: Load state returns dictionary."""
        state = WorkflowResume.load_state("some workflow state content")
        assert isinstance(state, dict)
        assert "pipeline_position" in state

    def test_format_recovery_summary_contains_position(self) -> None:
        """TC-037: Recovery summary contains position."""
        state = {
            "pipeline_position": "Stage 3",
            "completed_gates": ["G1"],
            "pending_escalations": [],
        }
        summary = WorkflowResume.format_recovery_summary(state)
        assert "Stage 3" in summary
        assert "1" in summary

    def test_determine_next_action_reset(self) -> None:
        """TC-038: Action is reset."""
        state: dict[str, Any] = {"pending_escalations": []}
        result = WorkflowResume.determine_next_action(state, user_choice=3)
        assert result == "RESET_PHASE_0"

    def test_determine_next_action_with_escalations(self) -> None:
        """TC-039: Action is resolve escalations."""
        state = {"pending_escalations": ["ESC-001"]}
        result = WorkflowResume.determine_next_action(state, user_choice=1)
        assert result == "RESOLVE_ESCALATIONS"

    def test_determine_next_action_resume(self) -> None:
        """TC-040: Action is resume."""
        state: dict[str, Any] = {"pending_escalations": []}
        result = WorkflowResume.determine_next_action(state, user_choice=1)
        assert result == "RESUME_AT_POSITION"
