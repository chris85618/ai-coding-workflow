"""Port Interface — SecurityGateway Contract.

Traceable to: FR-016, DEBT-004, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SecurityGateway(ABC):
    """Abstract gateway for security scanning tools.

    Traceable to: FR-016 (security audit), DEBT-004
    """

    @abstractmethod
    def scan(self, target_path: str) -> dict[str, Any]:
        """Run a security scan on the target path.

        Args:
            target_path: Directory or file path to scan.

        Returns:
            Scan results dictionary with findings.
        """

    @abstractmethod
    def generate_sbom(self, target_path: str) -> dict[str, Any]:
        """Generate a Software Bill of Materials (SBOM).

        Args:
            target_path: Directory to analyse.

        Returns:
            SBOM dictionary in CycloneDX format.
        """
