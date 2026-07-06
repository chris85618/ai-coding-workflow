"""Tests for the DebtItem value object (FR-068, ADR-STR-029)."""

import pytest

from agentic_workflow.domain.enums import DebtSource, Severity
from agentic_workflow.domain.value_objects.debt_item import DebtItem


class TestDebtItem:
    """Covers DebtItem construction validation and serialization."""

    def test_valid_construction(self) -> None:
        """TC-V2-001: A well-formed debt item is immutable and complete."""
        item = DebtItem(
            debt_id="DEBT-001",
            title="Sonar gate failure",
            source=DebtSource.QUALITY_GATE,
            severity=Severity.HIGH,
            description="coverage below threshold",
        )
        assert item.debt_id == "DEBT-001"
        assert item.source is DebtSource.QUALITY_GATE

    def test_as_dict_serializes_all_fields(self) -> None:
        """TC-V2-002: as_dict yields a JSON-compatible mapping."""
        item = DebtItem(
            debt_id="DEBT-002",
            title="Security finding",
            source=DebtSource.SECURITY,
            severity=Severity.CRITICAL,
        )
        payload = item.as_dict()
        assert payload["debt_id"] == "DEBT-002"
        assert payload["source"] == "security"
        assert payload["severity"] == "critical"
        assert payload["description"] == ""

    def test_invalid_id_prefix_rejected(self) -> None:
        """TC-V2-003: Construction rejects ids without the DEBT- prefix."""
        with pytest.raises(ValueError, match="must start with"):
            DebtItem(debt_id="RISK-001", title="t", source=DebtSource.CODE, severity=Severity.LOW)

    def test_empty_title_rejected(self) -> None:
        """TC-V2-004: Construction rejects an empty title."""
        with pytest.raises(ValueError, match="non-empty"):
            DebtItem(debt_id="DEBT-003", title="", source=DebtSource.CODE, severity=Severity.LOW)
