"""Tests for blast_radius.classify_severity — 100% statement + branch coverage.
Consolidated from: test_coverage_gap_fill.py
Traceable to: FR-008, FR-009, INV-012, ALG-003
"""
import pytest
import icontract
from agentic_workflow.domain.algorithms.blast_radius import classify_severity
from agentic_workflow.domain.models.enums import Severity


class TestClassifySeverity:
    """Full branch coverage: COSMETIC/LOW/MEDIUM/HIGH/CRITICAL paths."""

    # ── COSMETIC: blast_radius == 0 ──────────────────────────────────────────
    def test_zero_blast_radius_is_cosmetic(self):
        assert classify_severity(0, 0) == Severity.COSMETIC

    def test_zero_blast_radius_any_cross_stage_is_cosmetic(self):
        # Even if cross_stage is large, blast_radius==0 → COSMETIC
        assert classify_severity(0, 5) == Severity.COSMETIC

    # ── LOW: blast_radius == 1, cross_stage < 2 ──────────────────────────────
    def test_blast_1_cross_0_is_low(self):
        assert classify_severity(1, 0) == Severity.LOW

    def test_blast_1_cross_1_is_low(self):
        assert classify_severity(1, 1) == Severity.LOW

    # ── MEDIUM: blast_radius >= 2, < 5, cross_stage < 2 ─────────────────────
    def test_blast_2_cross_0_is_medium(self):
        assert classify_severity(2, 0) == Severity.MEDIUM

    def test_blast_3_cross_0_is_medium(self):
        assert classify_severity(3, 0) == Severity.MEDIUM

    def test_blast_4_cross_1_is_medium(self):
        assert classify_severity(4, 1) == Severity.MEDIUM

    # ── HIGH: blast_radius >= 5 or cross_stage >= 2 (but not CRITICAL) ───────
    def test_blast_5_cross_0_is_high(self):
        assert classify_severity(5, 0) == Severity.HIGH

    def test_blast_1_cross_2_is_high(self):
        assert classify_severity(1, 2) == Severity.HIGH

    def test_blast_7_cross_1_is_high(self):
        assert classify_severity(7, 1) == Severity.HIGH

    # ── CRITICAL: blast_radius >= 10 or cross_stage >= 3 ─────────────────────
    def test_blast_10_cross_0_is_critical(self):
        assert classify_severity(10, 0) == Severity.CRITICAL

    def test_blast_1_cross_3_is_critical(self):
        assert classify_severity(1, 3) == Severity.CRITICAL

    def test_blast_15_cross_5_is_critical(self):
        assert classify_severity(15, 5) == Severity.CRITICAL

    # ── icontract invariant check ─────────────────────────────────────────────
    def test_icontract_enforces_zero_blast_cosmetic(self):
        """INV-012: Zero blast radius must classify as COSMETIC.
        icontract raises ViolationError if the contract fails.
        """
        result = classify_severity(0, 0)
        assert result == Severity.COSMETIC

    def test_nonzero_blast_does_not_violate_contract(self):
        """Contract allows any severity for blast_radius > 0."""
        result = classify_severity(5, 0)
        assert result != Severity.COSMETIC  # COSMETIC only for blast_radius==0
