"""ALG-004 OO class interface."""

import pytest


class TestRiceScorerOO:
    """ALG-004 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.rice_scoring import RiceScorer

        self.cls = RiceScorer

    def test_class_constants_exist(self) -> None:
        """TC-183: RICE constants check."""
        assert 0.5 in self.cls.VALID_IMPACT_VALUES
        assert self.cls.REACH_MIN == 1
        assert self.cls.REACH_MAX == 100

    def test_score_formula(self) -> None:
        """TC-184: RICE formula check."""
        result = self.cls.score(10, 2.0, 1.0, 5.0)
        assert abs(result - 4.0) < 1e-9

    def test_score_half_impact(self) -> None:
        """TC-185: Half impact RICE score."""
        result = self.cls.score(100, 0.5, 0.5, 1.0)
        assert abs(result - 25.0) < 1e-9

    def test_invalid_effort_raises(self) -> None:
        """TC-186: Invalid effort detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 2.0, 1.0, 0)

    def test_invalid_reach_raises(self) -> None:
        """TC-187: Invalid reach detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(0, 2.0, 1.0, 1.0)

    def test_invalid_impact_raises(self) -> None:
        """TC-188: Invalid impact detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 1.5, 1.0, 1.0)

    def test_invalid_confidence_raises(self) -> None:
        """TC-189: Invalid confidence detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 2.0, 0.1, 1.0)
