"""Tests for SonarCloudGate.extract_tech_debt logic."""

from typing import Any

from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate


class TestExtractTechDebt:
    """Test SonarCloudGate.extract_tech_debt logic."""

    def test_todo_issue_creates_debt(self) -> None:
        """Verify TODO issue extraction."""
        issues: list[dict[str, Any]] = [{"type": "TODO", "message": "Fix this", "severity": "MAJOR"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert "DEBT-SONAR-0" in debts[0]["id"]
        assert debts[0]["priority"] == "P2"

    def test_fixme_issue_creates_debt(self) -> None:
        """Verify FIXME issue extraction."""
        issues: list[dict[str, Any]] = [{"type": "FIXME", "message": "Refactor", "severity": "MINOR"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert debts[0]["priority"] == "P3"

    def test_code_smell_creates_debt(self) -> None:
        """Verify CODE_SMELL issue extraction."""
        issues: list[dict[str, Any]] = [{"type": "CODE_SMELL", "message": "Smell", "severity": "CRITICAL"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert debts[0]["priority"] == "P2"

    def test_non_matching_type_skipped(self) -> None:
        """Verify non-debt types are skipped."""
        issues: list[dict[str, Any]] = [{"type": "UNKNOWN", "message": "Not a debt type"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts == []

    def test_empty_issues(self) -> None:
        """Verify empty issue list returns empty debt list."""
        assert SonarCloudGate.extract_tech_debt([]) == []

    def test_multiple_issues_indexed(self) -> None:
        """Verify sequential ID generation."""
        issues: list[dict[str, Any]] = [
            {"type": "TODO", "message": "First", "severity": "MAJOR"},
            {"type": "FIXME", "message": "Second", "severity": "MINOR"},
        ]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 2
        assert debts[0]["id"] == "DEBT-SONAR-0"
        assert debts[1]["id"] == "DEBT-SONAR-1"

    def test_missing_severity_defaults_p3(self) -> None:
        """Verify default priority mapping."""
        issues: list[dict[str, Any]] = [{"type": "TODO", "message": "No severity"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts[0]["priority"] == "P3"

    def test_missing_message_defaults_sonarcloud_issue(self) -> None:
        """Verify default title mapping."""
        issues: list[dict[str, Any]] = [{"type": "TODO"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert "SonarCloud Issue" in debts[0]["title"]
