"""Adapter: Anthropic Reasoner Implementation."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.domain.value_objects.model_config import ModelConfig
from agentic_workflow.frameworks.llm.providers.anthropic import AnthropicProvider


def _coerce_structured(response: Any) -> dict[str, Any]:
    return response if isinstance(response, dict) else response.dict()


class AnthropicReasoner(IAgentReasoner):
    """Implementation of IAgentReasoner using Anthropic's Claude models."""

    def __init__(self, config: ModelConfig):
        """Initialize with model configuration."""
        provider = AnthropicProvider()
        self._model = provider.create_model(config)

    def reason(self, prompt: str, system_message: str | None = None) -> str:
        """Get a text response from Claude."""
        messages: list[BaseMessage] = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        response = self._model.invoke(messages)
        return str(response.content)

    def extract_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Extract structured data using tool-calling or specific prompt formatting."""
        try:
            res = _coerce_structured(self._model.with_structured_output(schema).invoke(prompt))
        except (AttributeError, NotImplementedError):
            res = {"error": "Structured output not implemented for this model/version"}
        return res
