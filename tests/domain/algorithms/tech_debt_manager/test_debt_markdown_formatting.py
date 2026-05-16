"""Tests for TechDebtManager markdown formatting."""

from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager


class TestDebtMarkdownFormatting:
    """Tests for TechDebtManager markdown formatting."""

    def test_format_markdown_contains_id(self) -> None:
        """TC-250: Debt markdown formatting."""
        item = {
            "id": "DEBT-001",
            "title": "Fix thing",
            "source": "code",
            "affected_components": "api",
            "priority": "P1",
            "rice_score": 32.0,
            "quadrant": "Quick Win",
        }
        md = TechDebtManager.format_debt_markdown(item)
        assert "DEBT-001" in md
        assert "P1" in md
