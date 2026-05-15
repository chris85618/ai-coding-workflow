"""Unit tests for node_sonarcloud_gate.

Ensures the LangGraph adapter node correctly interacts with the domain algorithm
and maps the results to the workflow state.
Traceable to: FR-015, FR-035, FR-036, ADR-OPS-001.
"""

from typing import Any
from unittest.mock import patch

import pytest

from agentic_workflow.adapters.langgraph.nodes import node_sonarcloud_gate
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.domain.models.enums import GateDecision


class TestSonarCloudNode:
    """Test suite for SonarCloud node logic."""

    @pytest.fixture
    def mock_gate(self) -> Any:
        """Mock the SonarCloudGate domain algorithm."""
        with patch("agentic_workflow.adapters.langgraph.nodes.SonarCloudGate") as mock:
            yield mock

    def test_node_passes_when_metrics_valid(self, mock_gate: Any) -> None:
        """TC-NODE-001: Node returns PASS if quality gate passes."""
        # 1. Setup Mock
        mock_gate.verify_configuration.return_value = {
            "valid": True,
            "missing_vars": [],
        }
        mock_gate.evaluate.return_value = {
            "passed": True,
            "failures": [],
            "tech_debts": [],
        }

        state: WorkflowState = {"metadata": {"sonar_metrics": {"coverage": 90.0}}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS
        assert result["metadata"]["sonar_status"] == "passed"

    def test_node_fails_and_extracts_debt(self, mock_gate: Any) -> None:
        """TC-NODE-002: Node returns FAIL and records tech debts if gate fails."""
        # 1. Setup Mock
        mock_gate.verify_configuration.return_value = {
            "valid": True,
            "missing_vars": [],
        }
        mock_gate.evaluate.return_value = {
            "passed": False,
            "failures": ["Coverage 70% < 80%"],
            "tech_debts": [{"id": "DEBT-SONAR-0", "priority": "P2"}],
        }

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.FAIL
        assert result["metadata"]["pending_sonar_debts"] == [
            {"id": "DEBT-SONAR-0", "priority": "P2"}
        ]
        assert "SonarCloud Quality Gate Failed" in str(result.get("last_error"))

    def test_node_warns_when_config_missing(self, mock_gate: Any) -> None:
        """TC-NODE-003: Node returns PASS_WITH_WARNINGS if config is missing."""
        # 1. Setup Mock
        mock_gate.verify_configuration.return_value = {
            "valid": False,
            "missing_vars": ["SONAR_TOKEN"],
        }

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS_WITH_WARNINGS
        assert result["metadata"]["sonar_status"] == "disabled"
        assert "Missing SonarCloud parameters" in result["metadata"]["sonar_warning"]
