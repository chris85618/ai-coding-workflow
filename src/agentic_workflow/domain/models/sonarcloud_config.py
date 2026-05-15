"""SonarCloud Configuration Domain Model.

Traceable to: ADR-STR-010, FR-015
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SonarCloudConfig:
    """Configuration for SonarCloud quality gate.

    Attributes:
        token: API token for authentication.
        project_key: Unique key for the SonarCloud project.
        organization: SonarCloud organization key.
        auto_convert_to_debt: Whether to convert failures to technical debt.
        default_debt_priority: Default priority for extracted debt.
        on_missing_config: Action to take if config is missing.
    """

    token: str | None = None
    project_key: str | None = None
    organization: str | None = None
    auto_convert_to_debt: bool = True
    default_debt_priority: str = "P2"
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
