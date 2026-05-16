"""Cover missing branches in CLS-004/CLS-005."""

import pytest

from agentic_workflow.domain.models.enums import IDPrefix, LinkType
from agentic_workflow.domain.models.traceable_id import TraceableID, TraceLink


class TestTraceableIDBranches:
    """Cover missing branches in CLS-004/CLS-005."""

    def test_bg_no_upstream_raises(self) -> None:
        """BG ID cannot have upstream links (INV-007)."""
        bg = TraceableID(prefix=IDPrefix.BG, sequence=1, title="BG")
        link = TraceLink("FR-001", "BG-001", LinkType.DERIVES)
        with pytest.raises(Exception, match="BG IDs have no upstream links"):
            bg.add_upstream(link)

    def test_tc_no_downstream_raises(self) -> None:
        """TC ID cannot have downstream links (INV-007)."""
        tc = TraceableID(prefix=IDPrefix.TC, sequence=1, title="TC")
        link = TraceLink("TC-001", "FR-002", LinkType.VALIDATES)
        with pytest.raises(Exception, match="TC IDs have no downstream links"):
            tc.add_downstream(link)

    def test_full_id_format(self) -> None:
        """full_id property formats correctly."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=5, title="FR-005")
        assert fr.full_id == "FR-005"
