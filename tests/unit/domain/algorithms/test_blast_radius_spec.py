"""Unit tests for BlastRadius Specifications."""

from agentic_workflow.domain.algorithms.blast_radius_spec import (
    BlastRadiusInput,
    CriticalImpactSpecification,
    HighImpactSpecification,
    ZeroImpactSpecification,
)


class TestBlastRadiusSpecifications:
    """Test suite for BlastRadius Specification Pattern classes."""

    def test_low_impact_spec(self) -> None:
        """Verify LowImpactSpecification logic."""
        spec = ZeroImpactSpecification()
        assert spec.is_satisfied_by(BlastRadiusInput(0, 0)) is True
        assert spec.is_satisfied_by(BlastRadiusInput(1, 0)) is False

    def test_critical_impact_spec(self) -> None:
        """Verify CriticalImpactSpecification logic."""
        spec = CriticalImpactSpecification()
        assert spec.is_satisfied_by(BlastRadiusInput(10, 0)) is True
        assert spec.is_satisfied_by(BlastRadiusInput(0, 3)) is True
        assert spec.is_satisfied_by(BlastRadiusInput(9, 2)) is False

    def test_high_impact_spec(self) -> None:
        """Verify HighImpactSpecification logic."""
        spec = HighImpactSpecification()
        assert spec.is_satisfied_by(BlastRadiusInput(5, 0)) is True
        assert spec.is_satisfied_by(BlastRadiusInput(0, 2)) is True
        assert spec.is_satisfied_by(BlastRadiusInput(4, 1)) is False

    def test_specification_composition(self) -> None:
        """Test AND/OR/NOT composition from the base class."""
        zero = ZeroImpactSpecification()
        critical = CriticalImpactSpecification()

        # NOT zero
        not_zero = ~zero
        assert not_zero.is_satisfied_by(BlastRadiusInput(1, 0)) is True
        assert not_zero.is_satisfied_by(BlastRadiusInput(0, 0)) is False

        # Critical OR Zero
        crit_or_zero = critical | zero
        assert crit_or_zero.is_satisfied_by(BlastRadiusInput(10, 0)) is True
        assert crit_or_zero.is_satisfied_by(BlastRadiusInput(0, 0)) is True
        assert crit_or_zero.is_satisfied_by(BlastRadiusInput(5, 0)) is False
