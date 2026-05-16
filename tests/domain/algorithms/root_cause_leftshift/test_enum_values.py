"""Test Enum values and accessibility for RootCauseLeftShift."""

from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    InterventionType,
    RootCauseCategory,
)


class TestEnumValues:
    """Test Enum values and accessibility."""

    def test_root_cause_categories(self) -> None:
        """Verify enum values for categories."""
        cats = {c.value for c in RootCauseCategory}
        assert "FORMAT_ERROR" in cats
        assert "COVERAGE_GAP" in cats
        assert "GOVERNANCE_BYPASS" in cats
        assert "DECLARATION_IMPLEMENTATION_GAP" in cats

    def test_intervention_types(self) -> None:
        """Verify enum values for interventions."""
        types = {t.value for t in InterventionType}
        assert "GUARD_STRENGTHENING" in types
        assert "NEW_GUARD" in types
        assert "STEP_ADDITION" in types
