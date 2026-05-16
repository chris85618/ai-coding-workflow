"""Cover missing branches in CLS-001 pipeline.py."""

import pytest

from agentic_workflow.domain.models.enums import GateDecision, PipelineStatus
from agentic_workflow.domain.models.pipeline import Pipeline


class TestPipelineBranches:
    """Cover missing branches in CLS-001 pipeline.py."""

    def test_invalid_position_raises(self) -> None:
        """Invalid current_position raises ValueError."""
        with pytest.raises(ValueError, match="Invalid position"):
            Pipeline(pipeline_id="x", current_position="invalid_stage")

    def test_complete_transitions(self) -> None:
        """complete() sets status to COMPLETED."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS)
        p.complete()
        assert p.status == PipelineStatus.COMPLETED

    def test_advance_at_final_stage_raises(self) -> None:
        """Advance from final stage raises ValueError."""
        p = Pipeline(pipeline_id="x", current_position="phase10")
        p.start()
        p.record_gate(GateDecision.PASS)
        with pytest.raises(ValueError, match="final stage"):
            p.advance()

    def test_advance_pass_with_warnings(self) -> None:
        """PASS_WITH_WARNINGS also allows advance (INV-002-v2)."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS_WITH_WARNINGS)
        p.advance()
        assert p.current_position == "phase1"
