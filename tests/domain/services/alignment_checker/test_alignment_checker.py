"""Tests for the AlignmentChecker domain service (FR-072, ADR-STR-029, ALG-020)."""

from agentic_workflow.domain.services.alignment_checker import AlignmentChecker


class TestAlignmentChecker:
    """Covers the diverge → converge → align closure evidence merge."""

    def test_misalignments_are_tagged_and_merged(self) -> None:
        """TC-V2-030: Traceability and consistency issues are ALIGN-tagged."""
        result = AlignmentChecker.find_misalignments(["FR-001 missing UC"], ["doc contradicts CLS-002"])
        assert result == ["ALIGN: FR-001 missing UC", "ALIGN: doc contradicts CLS-002"]

    def test_empty_issues_are_dropped(self) -> None:
        """TC-V2-031: Blank issue strings never become findings."""
        assert AlignmentChecker.find_misalignments(["", ""], [""]) == []

    def test_is_aligned_true_when_clean(self) -> None:
        """TC-V2-032: No misalignments certifies the full solution."""
        assert AlignmentChecker.is_aligned([]) is True

    def test_is_aligned_false_when_issues_remain(self) -> None:
        """TC-V2-033: Any misalignment feeds back to Agent alpha."""
        assert AlignmentChecker.is_aligned(["ALIGN: gap"]) is False
