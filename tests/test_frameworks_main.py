"""Tests for entry point main.py."""

from unittest.mock import MagicMock, patch

from agentic_workflow.frameworks.main import main


@patch("agentic_workflow.frameworks.main.load_config")
@patch("agentic_workflow.frameworks.main.build_graph")
def test_main_execution(mock_build: MagicMock, mock_load: MagicMock) -> None:
    """TC-070: Entry point main() initializes and builds graph."""
    mock_config = MagicMock()
    mock_config.models = {"reasoning": MagicMock()}
    mock_load.return_value = mock_config

    main()

    mock_load.assert_called_once()
    mock_build.assert_called_once()
