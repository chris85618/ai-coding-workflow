"""Tests for entry point main.py."""

from unittest.mock import MagicMock, patch

from agentic_workflow.frameworks.main import main


@patch("agentic_workflow.frameworks.config.WorkflowConfigLoader.load")
@patch("agentic_workflow.frameworks.archon_orchestrator.ArchonOrchestrator.export_workflow")
def test_main_execution(mock_export: MagicMock, mock_load: MagicMock) -> None:
    """TC-070: Entry point main() initializes and exports the Archon workflow (ADR-STR-033)."""
    mock_config = MagicMock()
    mock_config.models = {"reasoning": MagicMock()}
    mock_load.return_value = mock_config

    main()

    mock_load.assert_called_once()
    mock_export.assert_called_once()
    pipeline_id, positions = mock_export.call_args[0]
    assert pipeline_id == "default"
    assert "stage3" in positions
