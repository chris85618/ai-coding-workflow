"""Tests for the Assumption value object (FR-070, ADR-STR-029)."""

import pytest

from agentic_workflow.domain.value_objects.assumption import Assumption


class TestAssumption:
    """Covers Assumption construction validation."""

    def test_valid_construction_defaults_active(self) -> None:
        """TC-V2-005: A well-formed assumption defaults to active."""
        assumption = Assumption(assumption_id="ASM-001", statement="No pragma comments", source_id="LESSON-024")
        assert assumption.active is True
        assert assumption.source_id == "LESSON-024"

    def test_invalid_id_prefix_rejected(self) -> None:
        """TC-V2-006: Construction rejects ids without the ASM- prefix."""
        with pytest.raises(ValueError, match="must start with"):
            Assumption(assumption_id="ADR-001", statement="stmt")

    def test_empty_statement_rejected(self) -> None:
        """TC-V2-007: Construction rejects an empty statement."""
        with pytest.raises(ValueError, match="non-empty"):
            Assumption(assumption_id="ASM-002", statement="")
