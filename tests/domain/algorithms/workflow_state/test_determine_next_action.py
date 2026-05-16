"""Tests for next action determination logic."""

from typing import Any

from agentic_workflow.domain.algorithms.workflow_resume import WorkflowResume


class TestDetermineNextAction:
    """Tests for next action determination logic."""

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
