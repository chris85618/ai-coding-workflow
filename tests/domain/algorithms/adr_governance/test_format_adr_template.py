"""Tests for ADRGovernance.format_adr_template."""

from typing import Any

from agentic_workflow.domain.algorithms.adr_governance import ADRGovernance


class TestFormatAdrTemplate:
    """Covers format_adr_template — known + unknown category branches."""

    def _details(self, **kwargs: Any) -> dict[str, Any]:
        base = {
            "status": "Proposed",
            "date": "2026-01-01",
            "decision_maker": "AI",
            "upstream_ids": ["FR-001"],
            "context": "Some context",
            "decision": "We do X",
            "rationale": "Because Y",
        }
        base.update(kwargs)
        return base

    def test_known_category_structural(self) -> None:
        """TC-301: format_adr_template STRUCTURAL."""
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Test ADR", self._details())
        assert "ADR-STR-001" in md
        assert "Test ADR" in md

    def test_known_category_governance(self) -> None:
        """TC-302: format_adr_template GOVERNANCE."""
        md = ADRGovernance.format_adr_template("GOVERNANCE", "002", "Gov ADR", self._details())
        assert "ADR-GOV-002" in md

    def test_known_category_security(self) -> None:
        """TC-303: format_adr_template SECURITY."""
        md = ADRGovernance.format_adr_template("SECURITY", "003", "Sec ADR", self._details())
        assert "ADR-SEC-003" in md

    def test_known_category_scope(self) -> None:
        """TC-304: format_adr_template SCOPE."""
        md = ADRGovernance.format_adr_template("SCOPE", "004", "Scope ADR", self._details())
        assert "ADR-SCP-004" in md

    def test_known_category_gate(self) -> None:
        """TC-305: format_adr_template GATE."""
        md = ADRGovernance.format_adr_template("GATE", "005", "Gate ADR", self._details())
        assert "ADR-GATE-005" in md

    def test_known_category_operational(self) -> None:
        """TC-306: format_adr_template OPERATIONAL."""
        md = ADRGovernance.format_adr_template("OPERATIONAL", "006", "Ops ADR", self._details())
        assert "ADR-OPS-006" in md

    def test_unknown_category_uses_misc(self) -> None:
        """TC-307: format_adr_template MISC fallback."""
        md = ADRGovernance.format_adr_template("UNKNOWN_TYPE", "007", "Misc ADR", self._details())
        assert "ADR-MISC-007" in md

    def test_template_contains_all_sections(self) -> None:
        """TC-308: Template section verification."""
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", self._details())
        assert "背景" in md
        assert "決策" in md
        assert "理由" in md
        assert "替代方案" in md

    def test_details_defaults_when_missing(self) -> None:
        """Covers the .get() defaults in the template."""
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", {})
        assert "Proposed" in md  # status default
        assert "AI-Autonomous" in md  # decision_maker default

    def test_upstream_ids_joined(self) -> None:
        """TC-309: Upstream IDs joined string."""
        details = self._details(upstream_ids=["FR-001", "FR-002"])
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", details)
        assert "FR-001" in md
        assert "FR-002" in md

    def test_empty_upstream_ids(self) -> None:
        """TC-310: Empty upstream IDs handling."""
        details = self._details(upstream_ids=[])
        md = ADRGovernance.format_adr_template("STRUCTURAL", "001", "Title", details)
        assert "ADR-STR-001" in md  # still generates correctly

    def test_categories_dict_has_all_keys(self) -> None:
        """TC-311: CATEGORIES key verification."""
        expected = {
            "STRUCTURAL",
            "GOVERNANCE",
            "SECURITY",
            "SCOPE",
            "GATE",
            "OPERATIONAL",
        }
        assert set(ADRGovernance.CATEGORIES.keys()) == expected
