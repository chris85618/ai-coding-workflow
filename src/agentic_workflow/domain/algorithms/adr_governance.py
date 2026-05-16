"""ADR Governance Algorithm.

Traceable to: FR-009
Replaces: skills/workflow-skills/adr-governance.md
"""

from typing import Any


class ADRGovernance:
    """Manages ADR classification, lifecycle, and formatting."""

    CATEGORIES = {
        "STRUCTURAL": "ADR-STR",
        "GOVERNANCE": "ADR-GOV",
        "SECURITY": "ADR-SEC",
        "SCOPE": "ADR-SCP",
        "GATE": "ADR-GATE",
        "OPERATIONAL": "ADR-OPS",
    }

    @classmethod
    def evaluate_decision_unit(
        cls,
        statement: str,
        cohesiveness: float,
        consequences_coupled: bool,
        atomic: bool,
    ) -> bool:
        """Evaluates if a decision is a valid Decision Unit."""
        return cohesiveness >= 0.8 and consequences_coupled and atomic

    @classmethod
    def format_adr_template(cls, category: str, adr_id: str, title: str, details: dict[str, Any]) -> str:
        """Generates the Markdown template for a new ADR."""
        prefix = cls.CATEGORIES.get(category, "ADR-MISC")
        full_id = f"{prefix}-{adr_id}"

        # Build standard sections
        md = f"""# {full_id}: {title}

> **狀態**: {details.get("status", "Proposed")}
> **日期**: {details.get("date")}
> **類別**: {category}
> **決策者**: {details.get("decision_maker", "AI-Autonomous")}
> **追溯**: {", ".join(details.get("upstream_ids", []))}

## 背景
{details.get("context", "- N/A")}

## 決策
{details.get("decision", "- 我們決定...")}

## 理由
{details.get("rationale", "- N/A")}

## 替代方案
| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
"""
        return md
