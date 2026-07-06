"""Tests for node_rollback (FR-069, FR-071, ADR-STR-029)."""

from typing import Any
from unittest.mock import MagicMock

from agentic_workflow.adapters.langgraph.nodes import node_rollback, set_container
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


class TestRollbackNode:
    """Covers the universal-base degradation path and delayed HITL flag."""

    def teardown_method(self) -> None:
        """Reset the injected container after each test."""
        set_container(None)

    def test_rollback_via_container_gateway(self) -> None:
        """TC-V2-045: The version-control gateway performs the rollback."""
        container = MagicMock()
        container.version_control.rollback_to.return_value = True
        set_container(container)
        result = node_rollback(WorkflowState(pipeline_id="p"))
        container.version_control.rollback_to.assert_called_once_with("universal-base")
        assert result["metadata"]["rollback_performed"] is True
        assert result["metadata"]["hitl_required"] is True

    def test_custom_universal_base_ref(self) -> None:
        """TC-V2-046: An explicit universal_base_ref in metadata wins."""
        container = MagicMock()
        container.version_control.rollback_to.return_value = True
        set_container(container)
        metadata: dict[str, Any] = {"universal_base_ref": "abc123"}
        node_rollback(WorkflowState(pipeline_id="p", metadata=metadata))
        container.version_control.rollback_to.assert_called_once_with("abc123")

    def test_missing_container_records_error_and_still_flags_hitl(self) -> None:
        """TC-V2-047: Rollback failure still raises the delayed-HITL flag."""
        set_container(None)
        result = node_rollback(WorkflowState(pipeline_id="p"))
        assert result["metadata"]["rollback_performed"] is False
        assert result["metadata"]["hitl_required"] is True
        assert result["last_error"] is not None
