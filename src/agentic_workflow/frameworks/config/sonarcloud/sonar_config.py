"""SonarCloud Main Configuration Model.

Implements ADR-SEC-005: Configuration Security Gateway.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .feedback_config import FeedbackConfig


class SonarCloudConfig(BaseModel):
    """Configuration for SonarCloud quality gate."""

    token: str | None = None
    project_key: str | None = None
    organization: str | None = None
    feedback: FeedbackConfig = Field(default_factory=FeedbackConfig)
    on_missing_config: str = "warn_and_disable"

    @property
    def is_valid(self) -> bool:
        """Check if essential parameters are present."""
        return bool(self.token and self.project_key and self.organization)

    @property
    def missing_vars(self) -> list[str]:
        """List names of missing essential parameters."""
        missing = []
        if not self.token:
            missing.append("SONAR_TOKEN")
        if not self.project_key:
            missing.append("SONAR_PROJECT_KEY")
        if not self.organization:
            missing.append("SONAR_ORGANIZATION")
        return missing
