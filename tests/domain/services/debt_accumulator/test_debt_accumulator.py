"""Tests for the DebtAccumulator domain service (FR-068, ADR-STR-029, ALG-016)."""

import deal
import pytest

from agentic_workflow.domain.enums import DebtSource, GateDecision, Severity
from agentic_workflow.domain.services.debt_accumulator import DebtAccumulator


class TestDebtAccumulator:
    """Covers dynamic debt absorption and continuous-flow gate decisions."""

    def test_absorb_numbers_sequentially_from_start_index(self) -> None:
        """TC-V2-010: Absorbed items are numbered from start_index."""
        items = DebtAccumulator.absorb(
            DebtSource.QUALITY_GATE, Severity.HIGH, ["coverage < 100", "bugs > 0"], start_index=3
        )
        assert [item.debt_id for item in items] == ["DEBT-003", "DEBT-004"]
        assert all(item.source is DebtSource.QUALITY_GATE for item in items)

    def test_absorb_skips_empty_descriptions(self) -> None:
        """TC-V2-011: Empty descriptions produce no debt items."""
        items = DebtAccumulator.absorb(DebtSource.SECURITY, Severity.CRITICAL, ["", "injection risk"], start_index=1)
        assert len(items) == 1
        assert items[0].description == "injection risk"

    def test_absorb_truncates_long_titles(self) -> None:
        """TC-V2-012: Titles are capped at 80 characters while description keeps all."""
        long_text = "x" * 200
        items = DebtAccumulator.absorb(DebtSource.VALIDATION, Severity.MEDIUM, [long_text], start_index=1)
        assert len(items[0].title) == 80
        assert items[0].description == long_text

    def test_absorb_rejects_zero_start_index(self) -> None:
        """TC-V2-013: Debt numbering is 1-based (INV-026)."""
        with pytest.raises(deal.PreContractError):
            DebtAccumulator.absorb(DebtSource.CODE, Severity.LOW, ["x"], start_index=0)

    def test_gate_decision_pass_when_no_debt(self) -> None:
        """TC-V2-014: Zero debt yields a clean PASS."""
        assert DebtAccumulator.gate_decision_for(0) is GateDecision.PASS

    def test_gate_decision_never_hard_fails(self) -> None:
        """TC-V2-015: Any debt count yields PASS_WITH_WARNINGS, never FAIL."""
        assert DebtAccumulator.gate_decision_for(7) is GateDecision.PASS_WITH_WARNINGS
