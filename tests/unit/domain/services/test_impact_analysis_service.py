"""Unit tests for ImpactAnalysisService."""

from agentic_workflow.domain.services.impact_analysis_service import ImpactAnalysisService


class TestImpactAnalysisService:
    """Test suite for ImpactAnalysisService."""

    def test_analyze_change_cosmetic(self) -> None:
        """Verify severity is COSMETIC when blast radius is 0."""
        service = ImpactAnalysisService()
        result = service.analyze_change()
        assert result["blast_radius"] == 0
        assert result["severity"] == "COSMETIC"
        assert result["requires_manual_resolution"] is False

    def test_analyze_change_minor(self) -> None:
        """Verify severity is MINOR for small blast radius."""
        service = ImpactAnalysisService()
        result = service.analyze_change(_downstream=["FR-002", "FR-003"])
        assert result["blast_radius"] == 2
        assert result["severity"] == "MINOR"

    def test_analyze_change_moderate(self) -> None:
        """Verify severity is MODERATE for medium blast radius."""
        service = ImpactAnalysisService()
        result = service.analyze_change(_downstream=["FR-002", "FR-003", "FR-004", "FR-005"])
        assert result["blast_radius"] == 4
        assert result["severity"] == "MODERATE"

    def test_analyze_change_major(self) -> None:
        """Verify severity is MAJOR for large blast radius."""
        service = ImpactAnalysisService()
        result = service.analyze_change(_downstream=[f"FR-{i:03d}" for i in range(2, 13)])
        assert result["blast_radius"] == 11
        assert result["severity"] == "MAJOR"
        assert result["requires_manual_resolution"] is True
