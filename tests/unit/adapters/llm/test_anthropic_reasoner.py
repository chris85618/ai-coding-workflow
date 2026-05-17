"""Unit tests for AnthropicReasoner adapter."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_workflow.domain.value_objects.model_config import ModelConfig
from agentic_workflow.frameworks.llm.anthropic_reasoner import AnthropicReasoner


class TestAnthropicReasoner:
    """Test suite for AnthropicReasoner."""

    @pytest.fixture
    def mock_config(self) -> ModelConfig:
        """Create a mock model configuration."""
        return ModelConfig(
            provider="anthropic", model="claude-3-opus", temperature=0.7, max_tokens=1000, api_key="test-key"
        )

    @patch("agentic_workflow.frameworks.llm.providers.anthropic.AnthropicProvider.create_model")
    def test_reason(self, mock_create: MagicMock, mock_config: ModelConfig) -> None:
        """Verify the reason method calls the underlying model."""
        mock_model = MagicMock()
        mock_create.return_value = mock_model

        mock_response = MagicMock()
        mock_response.content = "Hello from Claude"
        mock_model.invoke.return_value = mock_response

        reasoner = AnthropicReasoner(mock_config)
        result = reasoner.reason("Hello")

        assert result == "Hello from Claude"
        mock_model.invoke.assert_called_once()

    @patch("agentic_workflow.frameworks.llm.providers.anthropic.AnthropicProvider.create_model")
    def test_extract_structured_success(self, mock_create: MagicMock, mock_config: ModelConfig) -> None:
        """Verify structured extraction using with_structured_output."""
        mock_model = MagicMock()
        mock_create.return_value = mock_model

        structured_model = MagicMock()
        mock_model.with_structured_output.return_value = structured_model
        structured_model.invoke.return_value = {"key": "value"}

        reasoner = AnthropicReasoner(mock_config)
        result = reasoner.extract_structured("Extract", {"type": "object"})

        assert result == {"key": "value"}
        mock_model.with_structured_output.assert_called_once()

    @patch("agentic_workflow.frameworks.llm.providers.anthropic.AnthropicProvider.create_model")
    def test_extract_structured_fallback(self, mock_create: MagicMock, mock_config: ModelConfig) -> None:
        """Verify fallback when with_structured_output is missing."""
        mock_model = MagicMock()
        mock_create.return_value = mock_model
        # Simulate older LangChain version without the method
        del mock_model.with_structured_output

        reasoner = AnthropicReasoner(mock_config)
        result = reasoner.extract_structured("Extract", {"type": "object"})

        assert "error" in result
        assert "not implemented" in result["error"]

    @patch("agentic_workflow.frameworks.llm.providers.anthropic.AnthropicProvider.create_model")
    def test_reason_with_system_message(self, mock_create: MagicMock, mock_config: ModelConfig) -> None:
        """Verify the reason method with system message."""
        mock_model = MagicMock()
        mock_create.return_value = mock_model

        mock_response = MagicMock()
        mock_response.content = "Response"
        mock_model.invoke.return_value = mock_response

        reasoner = AnthropicReasoner(mock_config)
        result = reasoner.reason("Hello", system_message="Be helpful")

        assert result == "Response"
        mock_model.invoke.assert_called_once()
        messages = mock_model.invoke.call_args[0][0]
        assert len(messages) == 2
        assert messages[0].content == "Be helpful"
