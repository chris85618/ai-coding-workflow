"""Cover missing severity branches in ALG-003."""

from agentic_workflow.domain.algorithms.blast_radius import BlastRadiusClassifier
from agentic_workflow.domain.models.enums import Severity


class TestBlastRadiusBranches:
    """Cover missing severity branches in ALG-003."""

    def test_medium_severity(self) -> None:
        """blast_radius 2-4 ->MEDIUM."""
        assert BlastRadiusClassifier.classify(2, 0) == Severity.MEDIUM
        assert BlastRadiusClassifier.classify(3, 0) == Severity.MEDIUM
        assert BlastRadiusClassifier.classify(4, 0) == Severity.MEDIUM

    def test_high_from_cross_stage(self) -> None:
        """cross_stage >= 2 ->HIGH."""
        assert BlastRadiusClassifier.classify(1, 2) == Severity.HIGH

    def test_low_severity(self) -> None:
        """blast_radius 1, cross_stage 0 ->LOW."""
        assert BlastRadiusClassifier.classify(1, 0) == Severity.LOW

    def test_critical_from_cross_stage(self) -> None:
        """cross_stage >= 3 ->CRITICAL."""
        assert BlastRadiusClassifier.classify(1, 3) == Severity.CRITICAL
