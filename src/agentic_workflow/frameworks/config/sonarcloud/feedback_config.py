"""SonarCloud Feedback Configuration Model.

Implements ADR-STR-006: External YAML Configuration.
"""

from __future__ import annotations

from pydantic import BaseModel


class FeedbackConfig(BaseModel):
    """Nested feedback configuration for SonarCloud."""

    auto_convert_to_debt: bool = True
    default_debt_priority: str = "P2"
