"""Tests for node_security_audit."""

from unittest.mock import MagicMock

from agentic_workflow.adapters.langgraph.nodes import node_security_audit, set_container
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.frameworks.dependency_container import DependencyContainer


class TestSecurityAuditNode:
    """Covers node_security_audit logic."""

    def setup_method(self) -> None:
        """Set up for TestSecurityAuditNode."""
        # Initialize container with mocks to satisfy nodes
        self.mock_repo = MagicMock()
        self.container = DependencyContainer(
            pipeline_repo=self.mock_repo,
            checkpoint_repo=MagicMock(),
            doc_io=MagicMock(),
            reasoner=MagicMock(),
        )
        set_container(self.container)

    def test_node_security_audit_executes(self) -> None:
        """TC-310: Security audit node execution."""
        state = WorkflowState(pipeline_id="test-p")
        result = node_security_audit(state)

        assert "security_audit_findings" in result["metadata"]
        assert result["last_gate_decision"] == "pass"
