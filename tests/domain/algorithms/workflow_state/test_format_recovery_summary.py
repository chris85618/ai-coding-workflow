"""Tests for recovery summary formatting."""

from agentic_workflow.domain.algorithms.workflow_resume import WorkflowResume


class TestFormatRecoverySummary:
    """Tests for recovery summary formatting."""

    def test_format_recovery_summary_contains_position(self) -> None:
        """TC-037: Recovery summary contains position."""
        state = {
            "pipeline_position": "Stage 3",
            "completed_gates": ["G1"],
            "pending_escalations": [],
        }
        summary = WorkflowResume.format_recovery_summary(state)
        assert "Stage 3" in summary
        assert "1" in summary  # 1 completed gate
