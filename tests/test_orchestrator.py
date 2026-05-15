"""Tests for Orchestrator algorithm — 100% statement + branch coverage.
Consolidated from: test_algorithms_coverage.py
Traceable to: FR-002, FR-003, FR-017, FR-018
"""
import pytest
from agentic_workflow.domain.algorithms.orchestrator import Orchestrator, PhaseStatus


class TestPhaseStatus:
    def test_all_values_accessible(self):
        values = {s.value for s in PhaseStatus}
        assert values == {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "FAILED"}


class TestExecutePhase:
    def test_phase_0_returns_completed(self):
        result = Orchestrator.execute_phase(0, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_phase_1_returns_completed(self):
        result = Orchestrator.execute_phase(1, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_phase_output_mentions_phase_id(self):
        result = Orchestrator.execute_phase(5, {})
        assert "5" in result["output"]

    def test_context_passed_does_not_error(self):
        result = Orchestrator.execute_phase(0, {"key": "value"})
        assert isinstance(result, dict)

    def test_all_phases_0_to_10(self):
        for phase in range(11):
            result = Orchestrator.execute_phase(phase, {})
            assert result["status"] == PhaseStatus.COMPLETED


class TestExecuteStage:
    def test_stage_1_returns_completed(self):
        result = Orchestrator.execute_stage(1, {})
        assert result["status"] == PhaseStatus.COMPLETED

    def test_stage_output_mentions_stage_id(self):
        result = Orchestrator.execute_stage(3, {})
        assert "3" in result["output"]

    def test_all_stages_3_to_8(self):
        for stage in range(3, 9):
            result = Orchestrator.execute_stage(stage, {})
            assert result["status"] == PhaseStatus.COMPLETED


class TestRunS2cGeneration:
    """Covers the run_s2c_generation method (previously missing — line 32)."""

    def test_returns_string(self):
        result = Orchestrator.run_s2c_generation("domain_model", "requirements spec")
        assert isinstance(result, str)

    def test_output_contains_s2c_type(self):
        result = Orchestrator.run_s2c_generation("bdd_scenarios", "spec")
        assert "bdd_scenarios" in result

    def test_various_types(self):
        for s2c_type in ["charter", "stakeholder", "requirements", "domain_model", "bdd_scenarios"]:
            result = Orchestrator.run_s2c_generation(s2c_type, "input")
            assert s2c_type in result

    def test_empty_type(self):
        result = Orchestrator.run_s2c_generation("", "input")
        assert isinstance(result, str)
