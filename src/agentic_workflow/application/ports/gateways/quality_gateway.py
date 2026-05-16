"""Port Interface — QualityGateway Contract.

Traceable to: FR-015, DEBT-005, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QualityGateway(ABC):
    """Abstract gateway for external quality tools (SonarCloud, etc.).

    Traceable to: FR-015 (SonarCloud gate), DEBT-005
    """

    @abstractmethod
    def get_quality_metrics(self, project_key: str) -> dict[str, Any]:
        """Fetch quality metrics for a project.

        Args:
            project_key: Project identifier in the quality tool.

        Returns:
            Dictionary of metric names to values.
        """

    @abstractmethod
    def passes_gate(self, project_key: str) -> bool:
        """Check if the project passes the quality gate.

        Args:
            project_key: Project identifier.

        Returns:
            True if all quality thresholds are met.
        """
