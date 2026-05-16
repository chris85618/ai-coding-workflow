"""Unit tests for MicroValidation Specifications."""

from agentic_workflow.domain.algorithms.micro_validation_spec import (
    MicroValidationResult,
    ZeroErrorSpecification,
    ZeroWarningSpecification,
)


class TestMicroValidationSpecifications:
    """Test suite for MicroValidation Specification Pattern classes."""

    def test_zero_error_spec(self) -> None:
        """Verify ZeroErrorSpecification logic."""
        spec = ZeroErrorSpecification()

        valid = MicroValidationResult(has_errors=False, error_count=0, warning_count=5, messages=[])
        assert spec.is_satisfied_by(valid) is True

        invalid = MicroValidationResult(has_errors=True, error_count=1, warning_count=0, messages=["Error"])
        assert spec.is_satisfied_by(invalid) is False

    def test_zero_warning_spec(self) -> None:
        """Verify ZeroWarningSpecification logic."""
        spec = ZeroWarningSpecification()

        valid = MicroValidationResult(has_errors=False, error_count=0, warning_count=0, messages=[])
        assert spec.is_satisfied_by(valid) is True

        invalid = MicroValidationResult(has_errors=False, error_count=0, warning_count=1, messages=["Warning"])
        assert spec.is_satisfied_by(invalid) is False

    def test_strict_validation_composition(self) -> None:
        """Test composite spec requiring both zero errors and zero warnings."""
        strict = ZeroErrorSpecification() & ZeroWarningSpecification()

        assert strict.is_satisfied_by(MicroValidationResult(False, 0, 0, [])) is True
        assert strict.is_satisfied_by(MicroValidationResult(False, 0, 1, [])) is False
        assert strict.is_satisfied_by(MicroValidationResult(True, 1, 0, [])) is False
