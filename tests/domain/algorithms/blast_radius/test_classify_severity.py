"""Tests for BlastRadiusClassifier.classify — 100% statement + branch coverage."""

from agentic_workflow.domain.algorithms.blast_radius import BlastRadiusClassifier
from agentic_workflow.domain.enums import Severity


class TestClassifySeverity:
    """Full branch coverage: COSMETIC/LOW/MEDIUM/HIGH/CRITICAL paths."""

    def test_zero_blast_radius_is_cosmetic(self) -> None:
        """TC-151: Zero blast is COSMETIC."""
        assert BlastRadiusClassifier.classify(0, 0) == Severity.COSMETIC

    def test_zero_blast_radius_any_cross_stage_is_cosmetic(self) -> None:
        """TC-152: Zero blast with cross-stage is COSMETIC."""
        # Even if cross_stage is large, blast_radius==0 → COSMETIC
        assert BlastRadiusClassifier.classify(0, 5) == Severity.COSMETIC

    # ── LOW: blast_radius == 1, cross_stage < 2 ──────────────────────────────
    def test_blast_1_cross_0_is_low(self) -> None:
        """TC-153: Blast 1 cross 0 is LOW."""
        assert BlastRadiusClassifier.classify(1, 0) == Severity.LOW

    def test_blast_1_cross_1_is_low(self) -> None:
        """TC-154: Blast 1 cross 1 is LOW."""
        assert BlastRadiusClassifier.classify(1, 1) == Severity.LOW

    # ── MEDIUM: blast_radius >= 2, < 5, cross_stage < 2 ─────────────────────
    def test_blast_2_cross_0_is_medium(self) -> None:
        """TC-155: Blast 2 cross 0 is MEDIUM."""
        assert BlastRadiusClassifier.classify(2, 0) == Severity.MEDIUM

    def test_blast_3_cross_0_is_medium(self) -> None:
        """TC-156: Blast 3 cross 0 is MEDIUM."""
        assert BlastRadiusClassifier.classify(3, 0) == Severity.MEDIUM

    def test_blast_4_cross_1_is_medium(self) -> None:
        """TC-157: Blast 4 cross 1 is MEDIUM."""
        assert BlastRadiusClassifier.classify(4, 1) == Severity.MEDIUM

    # ── HIGH: blast_radius >= 5 or cross_stage >= 2 (but not CRITICAL) ───────
    def test_blast_5_cross_0_is_high(self) -> None:
        """TC-158: Blast 5 cross 0 is HIGH."""
        assert BlastRadiusClassifier.classify(5, 0) == Severity.HIGH

    def test_blast_1_cross_2_is_high(self) -> None:
        """TC-159: Blast 1 cross 2 is HIGH."""
        assert BlastRadiusClassifier.classify(1, 2) == Severity.HIGH

    def test_blast_7_cross_1_is_high(self) -> None:
        """TC-160: Blast 7 cross 1 is HIGH."""
        assert BlastRadiusClassifier.classify(7, 1) == Severity.HIGH

    # ── CRITICAL: blast_radius >= 10 or cross_stage >= 3 ─────────────────────
    def test_blast_10_cross_0_is_critical(self) -> None:
        """TC-161: Blast 10 cross 0 is CRITICAL."""
        assert BlastRadiusClassifier.classify(10, 0) == Severity.CRITICAL

    def test_blast_1_cross_3_is_critical(self) -> None:
        """TC-162: Blast 1 cross 3 is CRITICAL."""
        assert BlastRadiusClassifier.classify(1, 3) == Severity.CRITICAL

    def test_blast_15_cross_5_is_critical(self) -> None:
        """TC-163: Blast 15 cross 5 is CRITICAL."""
        assert BlastRadiusClassifier.classify(15, 5) == Severity.CRITICAL

    # ── deal contract check ─────────────────────────────────────────────
    def test_contract_enforces_zero_blast_cosmetic(self) -> None:
        """TC-164: Contract enforces zero blast COSMETIC."""
        result = BlastRadiusClassifier.classify(0, 0)
        assert result == Severity.COSMETIC

    def test_nonzero_blast_does_not_violate_contract(self) -> None:
        """TC-165: Non-zero blast allows any severity."""
        result = BlastRadiusClassifier.classify(5, 0)
        assert result != Severity.COSMETIC  # COSMETIC only for blast_radius==0
