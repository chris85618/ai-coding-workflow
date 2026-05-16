"""Three-Layer Security Audit — SecurityAuditResult Model.

Traceable to: FR-016
"""

from typing import Any

from pydantic import BaseModel


class SecurityAuditResult(BaseModel):
    """Result of a security audit layer."""

    layer: str
    passed: bool
    findings: list[dict[str, Any]]
