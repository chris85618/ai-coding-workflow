"""Tests for ADRGovernance algorithm — 100% statement + branch coverage.
Consolidated from: test_algorithms_coverage.py, test_governance_algorithms.py
Traceable to: FR-009, ALG (governance)
"""
import pytest
from agentic_workflow.domain.algorithms.adr_governance import ADRGovernance


class TestEvaluateDecisionUnit:
    """Covers evaluate_decision_unit — 2 branches (True/False return)."""

    def test_all_conditions_met_returns_true(self):
        assert ADRGovernance.evaluate_decision_unit("We decided X", 0.9, True, True) is True

    def test_low_cohesiveness_returns_false(self):
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.5, True, True) is False

    def test_not_consequences_coupled_returns_false(self):
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.9, False, True) is False

    def test_not_atomic_returns_false(self):
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.9, True, False) is False

    def test_all_false_returns_false(self):
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.0, False, False) is False

    def test_boundary_cohesiveness_exactly_08(self):
        # 0.8 >= 0.8 → True (if others also True)
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.8, True, True) is True

    def test_boundary_cohesiveness_just_below_08(self):
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.799, True, True) is False


class TestFormatAdrTemplate:
    """Covers format_adr_template — known + unknown category branches."""

    def _details(self, **kwargs):
        base = {
            "status": "Proposed", "date": "2026-01-01",
            "decision_maker": "AI", "upstream_ids": ["FR-001"],
            "context": "Some context", "decision": "We do X",
            "rationale": "Because Y",
        }
        base.update(kwargs)
        return base

    def test_known_category_structural(self):
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Test ADR", self._details())
        assert "ADR-STR-001" in md
        assert "Test ADR" in md

    def test_known_category_governance(self):
        md = ADRGovernance.format_adr_template("GOVERNANCE", "002", "Gov ADR", self._details())
        assert "ADR-GOV-002" in md

    def test_known_category_security(self):
        md = ADRGovernance.format_adr_template("SECURITY", "003", "Sec ADR", self._details())
        assert "ADR-SEC-003" in md

    def test_known_category_scope(self):
        md = ADRGovernance.format_adr_template("SCOPE", "004", "Scope ADR", self._details())
        assert "ADR-SCP-004" in md

    def test_known_category_gate(self):
        md = ADRGovernance.format_adr_template("GATE", "005", "Gate ADR", self._details())
        assert "ADR-GATE-005" in md

    def test_known_category_operational(self):
        md = ADRGovernance.format_adr_template("OPERATIONAL", "006", "Ops ADR", self._details())
        assert "ADR-OPS-006" in md

    def test_unknown_category_uses_misc(self):
        md = ADRGovernance.format_adr_template("UNKNOWN_TYPE", "007", "Misc ADR", self._details())
        assert "ADR-MISC-007" in md

    def test_template_contains_all_sections(self):
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", self._details())
        assert "背景" in md
        assert "決策" in md
        assert "理由" in md
        assert "替代方案" in md

    def test_details_defaults_when_missing(self):
        """Covers the .get() defaults in the template."""
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", {})
        assert "Proposed" in md        # status default
        assert "AI-Autonomous" in md   # decision_maker default

    def test_upstream_ids_joined(self):
        details = self._details(upstream_ids=["FR-001", "FR-002"])
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", details)
        assert "FR-001" in md
        assert "FR-002" in md

    def test_empty_upstream_ids(self):
        details = self._details(upstream_ids=[])
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", details)
        assert "ADR-STR-001" in md  # still generates correctly

    def test_categories_dict_has_all_keys(self):
        expected = {"STRUCTURAL", "GOVERNANCE", "SECURITY", "SCOPE", "GATE", "OPERATIONAL"}
        assert set(ADRGovernance.CATEGORIES.keys()) == expected
