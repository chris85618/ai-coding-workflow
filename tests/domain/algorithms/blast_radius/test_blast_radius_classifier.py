"""ALG-003 OO class interface."""

from agentic_workflow.domain.models.enums import Severity


class TestBlastRadiusClassifier:
    """ALG-003 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.blast_radius import (
            BlastRadiusClassifier,
        )

        self.cls = BlastRadiusClassifier

    def test_class_constants_exist(self) -> None:
        """TC-175: Blast constants check."""
        assert self.cls.CRITICAL_RADIUS == 10
        assert self.cls.HIGH_RADIUS == 5
        assert self.cls.MEDIUM_RADIUS == 2

    def test_zero_blast_radius_is_cosmetic(self) -> None:
        """TC-176: Zero blast is COSMETIC."""
        assert self.cls.classify(0, 0) == Severity.COSMETIC

    def test_critical_by_radius(self) -> None:
        """TC-177: Critical by radius."""
        assert self.cls.classify(10, 0) == Severity.CRITICAL

    def test_critical_by_stages(self) -> None:
        """TC-178: Critical by stages."""
        assert self.cls.classify(1, 3) == Severity.CRITICAL

    def test_high_by_radius(self) -> None:
        """TC-179: High by radius."""
        assert self.cls.classify(5, 0) == Severity.HIGH

    def test_high_by_stages(self) -> None:
        """TC-180: High by stages."""
        assert self.cls.classify(1, 2) == Severity.HIGH

    def test_medium(self) -> None:
        """TC-181: Medium severity."""
        assert self.cls.classify(2, 0) == Severity.MEDIUM

    def test_low(self) -> None:
        """TC-182: Low severity."""
        assert self.cls.classify(1, 0) == Severity.LOW
