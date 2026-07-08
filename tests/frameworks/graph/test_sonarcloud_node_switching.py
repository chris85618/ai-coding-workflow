"""Thorough verification of SonarCloud node switching logic.

Tests the following scenarios:
1. Data insufficient (missing config) -> WARNING + skip SonarCloud.
2. Data sufficient (config present) -> Fetch data from Adapter -> Evaluate.
3. Data sufficient but Adapter fails -> WARNING + skip with error msg.

Traceable to: RISK-001, FR-015, FR-035, ADR-OPS-001.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_workflow.adapters.orchestration.nodes import node_sonarcloud_gate
from agentic_workflow.adapters.orchestration.state_mapper.workflow_state import WorkflowState
from agentic_workflow.domain.enums import GateDecision
from agentic_workflow.domain.value_objects.sonarcloud_config import SonarCloudConfig


class TestSonarCloudNodeSwitching:
    """Detailed test suite for state switching in SonarCloud node."""

    @pytest.fixture(autouse=True)
    def setup_container(self) -> Any:
        """Set up a mock container for node tests."""
        from agentic_workflow.adapters.orchestration.nodes import set_container

        mock_container = MagicMock()
        set_container(mock_container)
        yield mock_container
        set_container(None)

    def test_switching_data_insufficient_warns_and_continues(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 1: Config missing (simulate removed .env).

        Expected: Returns PASS_WITH_WARNINGS, status='disabled', Adapter NOT called.
        """
        # 1. Setup: Missing token/key
        mock_sonar_config = SonarCloudConfig(
            token=None,
            project_key=None,
            organization=None,
            auto_convert_to_debt=True,
            default_debt_priority="P2",
            on_missing_config="warn_and_disable",
        )
        setup_container.sonar_config = mock_sonar_config

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS_WITH_WARNINGS
        assert result["metadata"]["sonar_status"] == "disabled"
        assert "Missing SonarCloud parameters" in result["metadata"]["sonar_warning"]
        assert "SONAR_TOKEN" in result["metadata"]["sonar_warning"]
        # container.sonar_adapter must NOT have been called
        setup_container.sonar_adapter.get_metrics.assert_not_called()

    def test_switching_data_sufficient_fetches_and_evaluates_pass(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 2: Config present -> Fetch data -> Pass.

        Expected: Returns PASS, status='passed', Adapter called.
        """
        # 1. Setup: Valid config
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        # Mock adapter instance (injected via container.sonar_adapter)
        adapter_inst = MagicMock()
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 90.0}}
        adapter_inst.get_issues.return_value = []
        setup_container.sonar_adapter = adapter_inst

        state: WorkflowState = {"metadata": {}}

        # 2. Execute
        result = node_sonarcloud_gate(state)

        # 3. Verify
        assert result["last_gate_decision"] == GateDecision.PASS
        assert result["metadata"]["sonar_status"] == "passed"
        assert result["metadata"]["sonar_metrics"] == {"coverage": {"global": 90.0}}
        adapter_inst.get_metrics.assert_called_once()

    def test_switching_data_sufficient_fetches_and_evaluates_fail(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 3: Config present -> Fetch data -> Fail.

        Expected: Returns FAIL, status='failed', tech debts recorded.
        """
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        # Mock adapter instance (Fail coverage)
        adapter_inst = MagicMock()
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 50.0}}
        adapter_inst.get_issues.return_value = []
        setup_container.sonar_adapter = adapter_inst

        state: WorkflowState = {"metadata": {}}

        result = node_sonarcloud_gate(state)

        assert result["last_gate_decision"] == GateDecision.FAIL
        assert result["metadata"]["sonar_status"] == "failed"
        assert len(result["metadata"]["sonar_failures"]) > 0
        assert "coverage" in result["metadata"]["sonar_failures"][0]

    def test_switching_data_sufficient_but_adapter_fails(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 4: Config present but API call fails.

        Expected: Returns PASS_WITH_WARNINGS, status='error', error msg in warning.
        """
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        # Mock adapter instance (API Error)
        adapter_inst = MagicMock()
        adapter_inst.get_metrics.side_effect = RuntimeError("API Connection Timeout")
        setup_container.sonar_adapter = adapter_inst

        state: WorkflowState = {"metadata": {}}

        result = node_sonarcloud_gate(state)

        assert result["last_gate_decision"] == GateDecision.PASS_WITH_WARNINGS
        assert result["metadata"]["sonar_status"] == "error"
        assert "API Connection Timeout" in result["metadata"]["sonar_warning"]

    def test_switching_skip_fetch_if_data_already_in_metadata(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 5: Data already present in metadata (e.g. from CI).

        Expected: Uses metadata data, Adapter NOT called.
        """
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        state: WorkflowState = {
            "metadata": {
                "sonar_metrics": {"coverage": {"global": 95.0}},
                "sonar_issues": [],
            },
        }

        result = node_sonarcloud_gate(state)

        assert result["last_gate_decision"] == GateDecision.PASS
        assert result["metadata"]["sonar_status"] == "passed"
        # container.sonar_adapter must NOT have been called (data pre-populated)
        setup_container.sonar_adapter.get_metrics.assert_not_called()

    def test_switching_partial_data_fetches_missing_metrics(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 6: sonar_issues present but sonar_metrics missing.

        Expected: Fetches metrics, reuses issues.
        """
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        adapter_inst = MagicMock()
        adapter_inst.get_metrics.return_value = {"coverage": {"global": 100.0}}
        setup_container.sonar_adapter = adapter_inst

        state: WorkflowState = {
            "metadata": {
                "sonar_issues": [],  # Present
                # sonar_metrics missing
            },
        }

        result = node_sonarcloud_gate(state)

        assert result["metadata"]["sonar_metrics"] == {"coverage": {"global": 100.0}}
        adapter_inst.get_metrics.assert_called_once()
        adapter_inst.get_issues.assert_not_called()

    def test_switching_partial_data_fetches_missing_issues(
        self,
        setup_container: MagicMock,
    ) -> None:
        """Scenario 7: sonar_metrics present but sonar_issues missing.

        Expected: Fetches issues, reuses metrics.
        """
        mock_sonar_config = SonarCloudConfig(
            token="valid_token",
            project_key="valid_key",
            organization="valid_org",
        )
        setup_container.sonar_config = mock_sonar_config

        adapter_inst = MagicMock()
        adapter_inst.get_issues.return_value = []
        setup_container.sonar_adapter = adapter_inst

        state: WorkflowState = {
            "metadata": {
                "sonar_metrics": {"coverage": {"global": 100.0}},  # Present
                # sonar_issues missing
            },
        }

        result = node_sonarcloud_gate(state)

        assert result["metadata"]["sonar_issues"] == []
        adapter_inst.get_issues.assert_called_once()
        adapter_inst.get_metrics.assert_not_called()
