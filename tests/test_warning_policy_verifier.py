"""Tests to fill coverage gaps for WarningPolicyVerifier and node_warning_policy_gate.

Traceable to: ADR-GOV-026, ALG-013.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

from agentic_workflow.adapters.langgraph.nodes import node_warning_policy_gate
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.domain.algorithms.warning_policy_verifier import (
    WarningPolicyVerifier,
)
from agentic_workflow.domain.models.enums import PipelineStatus


class TestWarningPolicyVerifierGaps:
    """Test gaps in WarningPolicyVerifier implementation."""

    def test_verify_config_file_not_found(self, tmp_path: Path) -> None:
        """Verify config when file does not exist (Line 30)."""
        non_existent = tmp_path / "pyproject.toml"
        result = WarningPolicyVerifier.verify_config(non_existent)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_config_no_filterwarnings(self, tmp_path: Path) -> None:
        """Verify config when filterwarnings is missing (Line 39)."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            "[tool.pytest.ini_options]\ntestpaths = ['tests']", encoding="utf-8"
        )
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_config_internal_exclusion(self, tmp_path: Path) -> None:
        """Verify internal code warning exclusion detection (Line 48)."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            "filterwarnings = ['ignore::DeprecationWarning:agentic_workflow.*']",
            encoding="utf-8",
        )
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is False
        assert any("Internal code warning exclusion" in v for v in result["violations"])

    def test_verify_config_unscoped_exclusion(self, tmp_path: Path) -> None:
        """Verify unscoped warning exclusion detection (Line 56)."""
        pyproject = tmp_path / "pyproject.toml"
        # Missing '.*' at the end of scope
        pyproject.write_text(
            "filterwarnings = ['ignore::DeprecationWarning:google']", encoding="utf-8"
        )
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is False
        assert any(
            "Broad or unscoped warning exclusion" in v for v in result["violations"]
        )

    def test_verify_config_ignore_no_colon(self, tmp_path: Path) -> None:
        """Verify ignore rule without colon handling (Line 52->45)."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("filterwarnings = ['ignore']", encoding="utf-8")
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_change_justification_failure(self) -> None:
        """Verify justification failure when missing keyword (Line 76)."""
        assert (
            WarningPolicyVerifier.verify_change_justification(
                "no evidence here", ["violation"]
            )
            is False
        )

    def test_verify_change_justification_success(self) -> None:
        """Verify justification success when keyword present (Line 76)."""
        assert (
            WarningPolicyVerifier.verify_change_justification(
                "FAILED_REFAC_EVIDENCE: test", ["violation"]
            )
            is True
        )


class TestNodeWarningPolicyGateGap:
    """Test gaps in node_warning_policy_gate implementation."""

    def test_node_warning_policy_gate_failure(self, tmp_path: Path) -> None:
        """Verify node returns FAILED status if policy check fails (Line 234)."""
        bad_config = tmp_path / "pyproject.toml"
        bad_config.write_text(
            "filterwarnings = ['ignore::DeprecationWarning:agentic_workflow.*']",
            encoding="utf-8",
        )

        state: dict[str, Any] = {
            "pipeline_id": "test",
            "metadata": {},
            "pipeline_status": PipelineStatus.RUNNING,
        }

        # Patch Path in node_warning_policy_gate to use our bad_config
        from typing import cast

        with patch(
            "agentic_workflow.adapters.langgraph.nodes.Path", return_value=bad_config
        ):
            result = node_warning_policy_gate(cast(WorkflowState, state))

        last_error = result.get("last_error")
        assert result["pipeline_status"] == PipelineStatus.FAILED
        assert last_error is not None
        assert "Warning Policy Violation" in last_error
