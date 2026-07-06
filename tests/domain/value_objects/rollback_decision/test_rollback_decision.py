"""Tests for the RollbackDecision value object (FR-069, ADR-STR-029)."""

import pytest

from agentic_workflow.domain.value_objects.rollback_decision import RollbackDecision


class TestRollbackDecision:
    """Covers RollbackDecision construction validation."""

    def test_valid_construction_defaults(self) -> None:
        """TC-V2-008: Defaults resolve to the universal base ref."""
        decision = RollbackDecision(should_rollback=True, reason="drift")
        assert decision.target_ref == "universal-base"
        assert decision.should_rollback is True

    def test_empty_target_ref_rejected(self) -> None:
        """TC-V2-009: Construction rejects an empty target ref."""
        with pytest.raises(ValueError, match="non-empty"):
            RollbackDecision(should_rollback=False, target_ref="")
