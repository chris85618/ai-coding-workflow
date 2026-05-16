"""Cover success paths in traceable_id.py."""

import pytest

from agentic_workflow.domain.models.enums import IDPrefix, LinkType
from agentic_workflow.domain.models.traceable_id import TraceableID, TraceLink


class TestTraceableIDSuccessPaths:
    """Cover the append lines in traceable_id.py."""

    def test_add_upstream_non_bg(self) -> None:
        """Non-BG ID can add upstream links."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("BG-001", "FR-001", LinkType.DECOMPOSES)
        fr.add_upstream(link)
        assert len(fr.upstream_links) == 1
        assert fr.upstream_links[0].source_id == "BG-001"

    def test_add_downstream_non_tc(self) -> None:
        """Non-TC ID can add downstream links."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("FR-001", "UC-001", LinkType.REALIZES)
        fr.add_downstream(link)
        assert len(fr.downstream_links) == 1
        assert fr.downstream_links[0].target_id == "UC-001"

    def test_trace_link_self_link_raises(self) -> None:
        """Self-link raises ValueError (INV-008)."""
        with pytest.raises(ValueError, match="Self-link forbidden"):
            TraceLink("FR-001", "FR-001", LinkType.DERIVES)
