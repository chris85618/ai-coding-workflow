"""Tests for RiskManager markdown formatting."""

from agentic_workflow.domain.algorithms.risk_manager import RiskManager


class TestRiskMarkdownFormatting:
    """Tests for RiskManager markdown formatting."""

    def test_format_markdown_contains_id(self) -> None:
        """TC-238: Risk markdown formatting."""
        item = {
            "id": "RISK-001",
            "title": "Test Risk",
            "status": "open",
            "category": "SEC",
            "likelihood": 3,
            "impact": 4,
            "score": 12,
            "severity": "HIGH",
            "strategy": "MT",
        }
        md = RiskManager.format_risk_markdown(item)
        assert "RISK-001" in md
        assert "HIGH" in md
