"""Unit tests for TraceableIdVO."""

import pytest

from agentic_workflow.domain.enums.id_prefix import IDPrefix
from agentic_workflow.domain.value_objects.traceable_id_vo import TraceableIdVO


class TestTraceableIdVO:
    """Test suite for TraceableIdVO validation and behavior."""

    def test_valid_id(self) -> None:
        """Verify that valid IDs are accepted."""
        vo = TraceableIdVO("FR-001")
        assert vo.value == "FR-001"
        assert str(vo) == "FR-001"

    def test_invalid_format(self) -> None:
        """Verify that invalid formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid Traceable ID format"):
            TraceableIdVO("FR-1")
        with pytest.raises(ValueError, match="Invalid Traceable ID format"):
            TraceableIdVO("FR-0001")

    def test_unknown_prefix(self) -> None:
        """Verify that unknown prefixes raise ValueError."""
        with pytest.raises(ValueError, match="Unknown ID prefix"):
            TraceableIdVO("XYZ-001")

    def test_factory_method(self) -> None:
        """Verify the create factory method."""
        vo = TraceableIdVO.create(IDPrefix.FR, 5)
        assert vo.value == "FR-005"

    def test_immutability(self) -> None:
        """Verify the VO is immutable (frozen dataclass)."""
        vo = TraceableIdVO("FR-001")
        with pytest.raises(AttributeError):
            vo.value = "FR-002"  # type: ignore
