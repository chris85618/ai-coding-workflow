"""Tech Debt Management Algorithm.

Traceable to: FR-010, FR-011
Replaces: ``skills/workflow-skills/tech-debt-collect.md`` and ``skills/workflow-skills/tech-debt-framework.md``
"""

from typing import Any

import deal

from agentic_workflow.domain.algorithms.rice_scoring import RiceScorer


class TechDebtManager:
    """Manages collection, scoring, and framework for technical debt."""

    @classmethod
    @deal.post(lambda result: result >= 0.0, message="RICE scores are non-negative")
    def calculate_rice_score(cls, reach: int, impact: float, confidence: float, effort: float) -> float:
        """Calculates RICE score: (Reach x Impact x Confidence) / Effort."""
        if effort <= 0:
            return 0.0
        return RiceScorer.score(reach, impact, confidence, effort)

    @classmethod
    @deal.has()
    @deal.post(
        lambda result: result in ("Quick Win", "Major Project", "Fill In", "Thankless Task"),
        message="Quadrant is a closed classification set",
    )
    def classify_quadrant(cls, impact: float, effort: float) -> str:
        """Classifies the debt into action quadrants."""
        if impact >= 2.0 and effort <= 2.0:
            return "Quick Win"
        if impact >= 2.0 and effort > 2.0:
            return "Major Project"
        if impact < 2.0 and effort <= 2.0:
            return "Fill In"
        return "Thankless Task"

    @classmethod
    @deal.has()
    @deal.post(lambda result: result in ("P1", "P2", "P3"), message="Priority is a closed set")
    def assign_priority(cls, quadrant: str) -> str:
        """Assigns priority based on quadrant."""
        mapping = {
            "Quick Win": "P1",
            "Major Project": "P2",
            "Fill In": "P3",
            "Thankless Task": "P3",
        }
        return mapping.get(quadrant, "P3")

    @classmethod
    @deal.post(lambda result: result.startswith("### "), message="Debt entries render as level-3 headings")
    def format_debt_markdown(cls, debt_item: dict[str, Any]) -> str:
        """Formats a debt item into the required Markdown structure."""
        return f"""### {debt_item.get("id")}: {debt_item.get("title")}
- **來源**: {debt_item.get("source")}
- **影響元件**: {debt_item.get("affected_components")}
- **優先等級**: {debt_item.get("priority")}
- **RICE Score**: {debt_item.get("rice_score")}
- **象限**: {debt_item.get("quadrant")}
"""
