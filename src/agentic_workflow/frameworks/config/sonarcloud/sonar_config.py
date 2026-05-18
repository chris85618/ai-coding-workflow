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
        return all((self.token, self.project_key, self.organization))

    @property
    def missing_vars(self) -> list[str]:
        """List names of missing essential parameters."""
        tk, pk, og = self.token, self.project_key, self.organization
        mapping = [("SONAR_TOKEN", tk), ("SONAR_PROJECT_KEY", pk), ("SONAR_ORGANIZATION", og)]
        return [n for n, v in mapping if not v]
