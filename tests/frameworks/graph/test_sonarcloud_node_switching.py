"""Thorough verification of SonarCloud node switching logic.

Tests the following scenarios:
1. Data insufficient (missing config) -> WARNING + skip SonarCloud.
2. Data sufficient (config present) -> Fetch data from Adapter -> Evaluate.
3. Data sufficient but Adapter fails -> WARNING + skip with error msg.

Traceable to: RISK-001, FR-015, FR-035, ADR-OPS-001.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_workflow.adapters.langgraph.nodes import node_sonarcloud_gate
from agentic_workflow.adapters.langgraph.state_mapper.workflow_state import WorkflowState
from agentic_workflow.domain.enums import GateDecision


class TestSonarCloudNodeSwitching:
    """Detailed test suite for state switching in SonarCloud node."""

    @pytest.fixture
    def mock_config_loader(self) -> Any:
        """Mock WorkflowConfigLoader.load."""
        with patch("agentic_workflow.adapters.langgraph.nodes.WorkflowConfigLoader.load") as mock:
            yield mock

    @pytest.fixture
    def mock_adapter(self) -> Any:
        """Mock SonarCloudAdapter."""
        with patch("agentic_workflow.adapters.langgraph.nodes.SonarCloudAdapter") as mock:
            yield mock

    def test_switching_data_insufficient_warns_and_continues(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 1: Config missing (simulate removed .env).

        Expected: Returns PASS_WITH_WARNINGS, status='disabled', Adapter NOT called.
        """
        # 1. Setup: Missing token/key
        mock_config = MagicMock()
        mock_config.sonarcloud.token = None
        mock_config.sonarcloud.project_key = None
        mock_config.sonarcloud.organization = None
        mock_config.sonarcloud.feedback.auto_convert_to_debt = True
        mock_config.sonarcloud.feedback.default_debt_priority = "P2"
        mock_config.sonarcloud.on_missing_config = "warn_and_disable"
        mock_config_loader.return_value = mock_config

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS_WITH_WARNINGS
        assert result["metadata"]["sonar_status"] == "disabled"
        assert "Missing SonarCloud parameters" in result["metadata"]["sonar_warning"]
        assert "SONAR_TOKEN" in result["metadata"]["sonar_warning"]
        mock_adapter.assert_not_called()

    def test_switching_data_sufficient_fetches_and_evaluates_pass(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 2: Config present -> Fetch data -> Pass.

        Expected: Returns PASS, status='passed', Adapter called.
        """
        # 1. Setup: Valid config
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config.sonarcloud.project_key = "valid_key"
        mock_config.sonarcloud.organization = "valid_org"
        mock_config_loader.return_value = mock_config

        # Mock adapter instance
        adapter_inst = mock_adapter.return_value
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 90.0}}
        adapter_inst.get_issues.return_value = []

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS
        assert result["metadata"]["sonar_status"] == "passed"
        assert result["metadata"]["sonar_metrics"] == {"coverage": {"global": 90.0}}
        mock_adapter.assert_called_once()
        adapter_inst.get_metrics.assert_called_once()

    def test_switching_data_sufficient_fetches_and_evaluates_fail(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 3: Config present -> Fetch data -> Fail.

        Expected: Returns FAIL, status='failed', tech debts recorded.
        """
        # 1. Setup: Valid config
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config_loader.return_value = mock_config

        # Mock adapter instance (Fail coverage)
        adapter_inst = mock_adapter.return_value
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 50.0}}
        adapter_inst.get_issues.return_value = []

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.FAIL
        assert result["metadata"]["sonar_status"] == "failed"
        assert len(result["metadata"]["sonar_failures"]) > 0
        assert "coverage" in result["metadata"]["sonar_failures"][0]

    def test_switching_data_sufficient_but_adapter_fails(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 4: Config present but API call fails.

        Expected: Returns PASS_WITH_WARNINGS, status='error', error msg in warning.
        """
        # 1. Setup: Valid config
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config_loader.return_value = mock_config

        # Mock adapter instance (API Error)
        adapter_inst = mock_adapter.return_value
        adapter_inst.get_metrics.side_effect = RuntimeError("API Connection Timeout")

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS_WITH_WARNINGS
        assert result["metadata"]["sonar_status"] == "error"
        assert "API Connection Timeout" in result["metadata"]["sonar_warning"]

    def test_switching_skip_fetch_if_data_already_in_metadata(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 5: Data already present in metadata (e.g. from CI).

        Expected: Uses metadata data, Adapter NOT called.
        """
        # 1. Setup: Valid config
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config_loader.return_value = mock_config

        state: WorkflowState = {
            "metadata": {
                "sonar_metrics": {"coverage": {"global": 95.0}},
                "sonar_issues": [],
            },
        }

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS
        assert result["metadata"]["sonar_status"] == "passed"
        mock_adapter.assert_not_called()

    def test_switching_partial_data_fetches_missing_metrics(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 6: sonar_issues present but sonar_metrics missing.

        Expected: Fetches metrics, reuses issues.
        """
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config_loader.return_value = mock_config

        adapter_inst = mock_adapter.return_value
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 100.0}}

        state: WorkflowState = {
            "metadata": {
                "sonar_issues": [],  # Present
                # sonar_metrics missing
            },
        }

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["metadata"]["sonar_metrics"] == {"coverage": {"global": 100.0}}
        adapter_inst.get_metrics.assert_called_once()
        adapter_inst.get_issues.assert_not_called()

    def test_switching_partial_data_fetches_missing_issues(
        self,
        mock_config_loader: MagicMock,
        mock_adapter: MagicMock,
    ) -> None:
        """Scenario 7: sonar_metrics present but sonar_issues missing.

        Expected: Fetches issues, reuses metrics.
        """
        mock_config = MagicMock()
        mock_config.sonarcloud.token = "valid_token"
        mock_config_loader.return_value = mock_config

        adapter_inst = mock_adapter.return_value
        adapter_inst.get_issues.return_value = []

        state: WorkflowState = {
            "metadata": {
                "sonar_metrics": {"coverage": {"global": 100.0}},  # Present
                # sonar_issues missing
            },
        }

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["metadata"]["sonar_issues"] == []
        adapter_inst.get_issues.assert_called_once()
        adapter_inst.get_metrics.assert_not_called()
