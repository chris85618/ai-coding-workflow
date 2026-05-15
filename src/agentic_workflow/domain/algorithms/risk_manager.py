"""Risk Management Algorithm.

Traceable to: FR-010, FR-011
Replaces: skills/workflow-skills/risk-management.md
"""

from typing import Any


class RiskManager:
    """Manages risk identification, evaluation, and treatment (ISO 31000)."""

    @classmethod
    def calculate_risk_score(cls, likelihood: int, impact: int) -> dict[str, Any]:
        """Calculates risk score and severity level."""
        score = likelihood * impact

        if score <= 4:
            severity = "LOW"
        elif score <= 9:
            severity = "MEDIUM"
        elif score <= 14:
            severity = "HIGH"
        else:
            severity = "CRITICAL"

        return {"score": score, "severity": severity}

    @classmethod
    def evaluate_treatment(cls, severity: str) -> dict[str, Any]:
        """Determines treatment priority and HITL requirement."""
        mapping = {
            "CRITICAL": {"priority": "Immediate (This Sprint)", "requires_hitl": True},
            "HIGH": {"priority": "Within Sprint", "requires_hitl": True},
            "MEDIUM": {
                "priority": "Next Sprint",
                "requires_hitl": False,
            },  # Recommended
            "LOW": {"priority": "Quarterly Review", "requires_hitl": False},
        }
        return mapping.get(severity, mapping["LOW"])

    @classmethod
    def format_risk_markdown(cls, risk_item: dict[str, Any]) -> str:
        """Formats a risk item into the required Markdown structure."""
        return f"""### {risk_item.get("id")}: {risk_item.get("title")}
- **狀態**: {risk_item.get("status", "open")}
- **類別**: {risk_item.get("category")}
- **機率**: {risk_item.get("likelihood")}
- **影響**: {risk_item.get("impact")}
- **風險強度**: {risk_item.get("score")} ({risk_item.get("severity")})
- **應對策略**: {risk_item.get("strategy")}
"""
