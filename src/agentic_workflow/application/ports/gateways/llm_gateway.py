"""Port Interface — LLMGateway Contract.

Traceable to: FR-026, FR-027, FR-029, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_workflow.domain.enums import TaskType
    from agentic_workflow.domain.value_objects import ModelConfig


class LLMGateway(ABC):
    """Abstract gateway for LLM provider calls.

    Traceable to: FR-026 (LLM inference), FR-027 (model selection),
    FR-029 (strategy pattern), UC-003 (iteration convergence)
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        task_type: TaskType,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the LLM and return the completion.

        Args:
            prompt: The prompt string to send.
            task_type: Task type used for model selection (ALG-008).
            max_tokens: Maximum tokens for the completion.

        Returns:
            LLM completion string.
        """

    @abstractmethod
    def get_model_config(self, task_type: TaskType) -> ModelConfig:
        """Return the ModelConfig that will be used for this task type.

        Args:
            task_type: The task type to look up.

        Returns:
            ModelConfig for the selected model.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is currently reachable.

        Returns:
            True if the provider API is accessible.
        """
