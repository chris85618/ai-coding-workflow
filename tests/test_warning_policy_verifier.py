"""Tests to fill coverage gaps for WarningPolicyVerifier and node_warning_policy_gate.
Traceable to: ADR-GOV-026, ALG-013
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from agentic_workflow.domain.algorithms.warning_policy_verifier import WarningPolicyVerifier
from agentic_workflow.adapters.langgraph.nodes import node_warning_policy_gate
from agentic_workflow.domain.models.enums import PipelineStatus

class TestWarningPolicyVerifierGaps:
    def test_verify_config_file_not_found(self, tmp_path):
        """Line 30: pyproject.toml does not exist."""
        non_existent = tmp_path / "pyproject.toml"
        result = WarningPolicyVerifier.verify_config(non_existent)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_config_no_filterwarnings(self, tmp_path):
        """Line 39: filterwarnings section missing."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest.ini_options]\ntestpaths = ['tests']", encoding="utf-8")
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_config_internal_exclusion(self, tmp_path):
        """Line 48: Internal code warning exclusion detected."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("filterwarnings = ['ignore::DeprecationWarning:agentic_workflow.*']", encoding="utf-8")
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is False
        assert any("Internal code warning exclusion" in v for v in result["violations"])

    def test_verify_config_unscoped_exclusion(self, tmp_path):
        """Line 56: Broad or unscoped warning exclusion detected."""
        pyproject = tmp_path / "pyproject.toml"
        # Missing '.*' at the end of scope
        pyproject.write_text("filterwarnings = ['ignore::DeprecationWarning:google']", encoding="utf-8")
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is False
        assert any("Broad or unscoped warning exclusion" in v for v in result["violations"])

    def test_verify_config_ignore_no_colon(self, tmp_path):
        """Line 52->45: ignore rule without a colon (partially covered branch)."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("filterwarnings = ['ignore']", encoding="utf-8")
        result = WarningPolicyVerifier.verify_config(pyproject)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_verify_change_justification_failure(self):
        """Line 76: Justification missing."""
        assert WarningPolicyVerifier.verify_change_justification("no evidence here", ["violation"]) is False

    def test_verify_change_justification_success(self):
        """Line 76: Justification present."""
        assert WarningPolicyVerifier.verify_change_justification("FAILED_REFAC_EVIDENCE: test", ["violation"]) is True

class TestNodeWarningPolicyGateGap:
    def test_node_warning_policy_gate_failure(self, tmp_path):
        """nodes.py Line 234: node returns FAILED status if policy check fails."""
        bad_config = tmp_path / "pyproject.toml"
        bad_config.write_text("filterwarnings = ['ignore::DeprecationWarning:agentic_workflow.*']", encoding="utf-8")
        
        state = {
            "pipeline_id": "test",
            "metadata": {},
            "pipeline_status": PipelineStatus.RUNNING
        }
        
        # Patch Path in node_warning_policy_gate to use our bad_config
        with patch("agentic_workflow.adapters.langgraph.nodes.Path", return_value=bad_config):
            result = node_warning_policy_gate(state)
            
        assert result["pipeline_status"] == PipelineStatus.FAILED
        assert "last_error" in result
        assert "Warning Policy Violation" in result["last_error"]
