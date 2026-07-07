"""Frameworks Layer — DSPy implementation of the prompt optimizer gateway.

Traceable to: FR-075, ADR-STR-031
Thin DSPy wrapper: demonstrations are normalized through dspy.Example before
few-shot rendering. When dspy is not installed the optimizer degrades
gracefully to the pure few-shot adapter (ADR-GOV-017); a configured dspy LM
unlocks teleprompter compilation as the documented upgrade path.
"""

from __future__ import annotations

import importlib
from typing import Any

from agentic_workflow.adapters.prompting.few_shot_prompt_optimizer import FewShotPromptOptimizer
from agentic_workflow.application.ports.gateways.prompt_optimizer import IPromptOptimizer

_DSPY_MODULE_NAME = "dspy"


class DSPyModuleLoader:
    """Loads the optional dspy accelerator module (None when not installed)."""

    @staticmethod
    def load() -> Any:
        """Import dspy when installed; None otherwise (ADR-GOV-017)."""
        module_name = _DSPY_MODULE_NAME
        try:
            loaded: Any = importlib.import_module(module_name)
        except ImportError:
            loaded = None
        return loaded


class DSPyDemoMapper:
    """Normalizes example pairs through dspy.Example demonstrations."""

    @staticmethod
    def to_demos(module: Any, examples: list[tuple[str, str]]) -> list[Any]:
        """Build dspy.Example demonstrations from (input, expected-output) pairs."""
        return [module.Example(question=question, answer=answer) for question, answer in examples]

    @staticmethod
    def to_pairs(demos: list[Any]) -> list[tuple[str, str]]:
        """Extract the normalized (input, expected-output) pairs from demonstrations."""
        return [(demo.question, demo.answer) for demo in demos]


class DSPyPromptOptimizer(IPromptOptimizer):
    """DSPy-backed prompt optimizer with a pure few-shot degradation path."""

    def optimize(self, base_prompt: str, examples: list[tuple[str, str]]) -> str:
        """Optimize with dspy-normalized demonstrations when available; degrade otherwise."""
        module = DSPyModuleLoader.load()
        pairs = examples if module is None else DSPyDemoMapper.to_pairs(DSPyDemoMapper.to_demos(module, examples))
        return FewShotPromptOptimizer().optimize(base_prompt, pairs)
