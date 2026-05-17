"""Three-Layer Security Audit — SecurityAuditResult Model.

Traceable to: FR-016
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SecurityAuditResult:
    """Result of a security audit layer."""

    layer: str
    passed: bool
    findings: list[dict[str, Any]]
