"""Cover Stage.add_finding() logic."""

from agentic_workflow.domain.entities.stage import Stage


class TestStageAddFinding:
    """Cover Stage.add_finding() logic."""

    def test_add_finding_appends(self) -> None:
        """add_finding appends finding string to findings list."""
        s = Stage(stage_id="s3", name="Stage 3")
        s.add_finding("CRITICAL: missing invariant")
        s.add_finding("HIGH: unclear domain")
        assert len(s.findings) == 2
        assert "CRITICAL: missing invariant" in s.findings
