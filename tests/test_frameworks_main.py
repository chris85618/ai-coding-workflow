"""Tests for entry point main.py."""
import sys
from unittest.mock import patch, MagicMock
from agentic_workflow.frameworks.main import main
from agentic_workflow.frameworks.config import WorkflowConfig, ModelConfig

@patch("agentic_workflow.frameworks.main.load_config")
@patch("agentic_workflow.frameworks.main.build_graph")
def test_main_execution(mock_build, mock_load):
    mock_config = MagicMock()
    mock_config.models = {"reasoning": MagicMock()}
    mock_load.return_value = mock_config
    
    main()
    
    mock_load.assert_called_once()
    mock_build.assert_called_once()
