"""Tests for Orchestrator algorithm — 100% statement + branch coverage.

Consolidated from: test_algorithms_coverage.py
Traceable to: FR-002, FR-003, FR-017, FR-018.
"""

from agentic_workflow.domain.algorithms.orchestrator import Orchestrator, PhaseStatus


class TestPhaseStatus:
    """Test PhaseStatus enum accessibility."""

    def test_all_values_accessible(self) -> None:
        """Verify all PhaseStatus enum values are present."""
        values = {s.value for s in PhaseStatus}
        assert values == {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "FAILED"}


class TestExecutePhase:
    """Test Orchestrator.execute_phase logic."""

    def test_phase_0_returns_completed(self) -> None:
        """Verify phase 0 execution returns completed."""
        result = Orchestrator.execute_phase(0, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_phase_1_returns_completed(self) -> None:
        """Verify phase 1 execution returns completed."""
        result = Orchestrator.execute_phase(1, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_phase_output_mentions_phase_id(self) -> None:
        """Verify phase output contains the phase ID."""
        result = Orchestrator.execute_phase(5, {})
        assert "5" in result["output"]

    def test_context_passed_does_not_error(self) -> None:
        """Verify context passing works."""
        result = Orchestrator.execute_phase(0, {"key": "value"})
        assert isinstance(result, dict)

    def test_all_phases_0_to_10(self) -> None:
        """Verify all phases 0 to 10 execute successfully."""
        for phase in range(11):
            result = Orchestrator.execute_phase(phase, {})
            assert result["status"] == PhaseStatus.COMPLETED


class TestExecuteStage:
    """Test Orchestrator.execute_stage logic."""

    def test_stage_1_returns_completed(self) -> None:
        """Verify stage 1 execution returns completed."""
        result = Orchestrator.execute_stage(1, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_stage_output_mentions_stage_id(self) -> None:
        """Verify stage output contains the stage ID."""
        result = Orchestrator.execute_stage(3, {})
        assert "3" in result["output"]

    def test_all_stages_3_to_8(self) -> None:
        """Verify all stages 3 to 8 execute successfully."""
        for stage in range(3, 9):
            result = Orchestrator.execute_stage(stage, {})
            assert result["status"] == PhaseStatus.COMPLETED


class TestRunS2cGeneration:
    """Test Orchestrator.run_s2c_generation logic."""

    """Covers the run_s2c_generation method (previously missing — line 32)."""

    def test_returns_string(self) -> None:
        """Verify S2C generation returns a string."""
        result = Orchestrator.run_s2c_generation("domain_model", "requirements spec")
        assert isinstance(result, str)

    def test_output_contains_s2c_type(self) -> None:
        """Verify S2C output contains the requested type."""
        result = Orchestrator.run_s2c_generation("bdd_scenarios", "spec")
        assert "bdd_scenarios" in result

    def test_various_types(self) -> None:
        """Verify S2C generation for all supported types."""
        for s2c_type in [
            "charter",
            "stakeholder",
            "requirements",
            "domain_model",
            "bdd_scenarios",
        ]:
            result = Orchestrator.run_s2c_generation(s2c_type, "input")
            assert s2c_type in result

    def test_empty_type(self) -> None:
        """Verify S2C generation with empty type returns a string."""
        result = Orchestrator.run_s2c_generation("", "input")
        assert isinstance(result, str)
