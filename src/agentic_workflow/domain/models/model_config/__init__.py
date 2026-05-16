"""CLS-018: ModelConfig and ContextAllocation — Value Objects for LLM model parameters.

Traceable to: CLS-017 (LLMStrategySelector creates this)
INV-022 ensures provider is within enabled set.
"""

from agentic_workflow.domain.models.model_config.context_allocation import (
    ContextAllocation,
)
from agentic_workflow.domain.models.model_config.model_config import ModelConfig

__all__ = ["ModelConfig", "ContextAllocation"]
