"""Tests for node_absorb_debt (FR-068, ADR-STR-029)."""

from typing import Any

from agentic_workflow.adapters.orchestration.nodes import node_absorb_debt
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


class TestAbsorbDebtNode:
    """Covers dynamic debt absorption without hard stops."""

    def test_absorbs_sonar_and_security_failures(self) -> None:
        """TC-V2-040: Failures become DEBT items and the gate downgrades to warnings."""
        metadata: dict[str, Any] = {
            "sonar_failures": ["coverage < 100"],
            "security_audit_findings": ["open port"],
        }
        state = WorkflowState(pipeline_id="p", metadata=metadata, last_error="Sonar failed")
        result = node_absorb_debt(state)
        debt_ids = [item["debt_id"] for item in result["metadata"]["debt_items"]]
        assert debt_ids == ["DEBT-001", "DEBT-002"]
        assert result["last_gate_decision"] == "pass_with_warnings"
        assert result["last_error"] is None
        assert result["metadata"]["sonar_failures"] == []
        assert result["metadata"]["security_audit_findings"] == []

    def test_appends_after_existing_debt(self) -> None:
        """TC-V2-041: Numbering continues after previously absorbed items."""
        metadata: dict[str, Any] = {
            "sonar_failures": ["new failure"],
            "debt_items": [{"debt_id": "DEBT-001"}],
        }
        result = node_absorb_debt(WorkflowState(pipeline_id="p", metadata=metadata))
        debt_ids = [item["debt_id"] for item in result["metadata"]["debt_items"]]
        assert debt_ids == ["DEBT-001", "DEBT-002"]

    def test_no_failures_yields_clean_pass(self) -> None:
        """TC-V2-042: Nothing to absorb keeps a clean PASS decision."""
        result = node_absorb_debt(WorkflowState(pipeline_id="p"))
        assert result["metadata"]["debt_items"] == []
        assert result["last_gate_decision"] == "pass"
