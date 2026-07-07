"""Adapters Layer — Bootstrap few-shot prompt optimizer (degradation path).

Traceable to: FR-075, ADR-STR-031
Pure string logic mirroring the structure of DSPy's labeled few-shot
compilation: the base prompt is enriched with (input, expected-output)
demonstrations. Always available, so the DSPy accelerator stays optional
(ADR-GOV-017 graceful degradation; Voyager-style skill/lesson reuse).
"""

from __future__ import annotations

from agentic_workflow.application.ports.gateways.prompt_optimizer import IPromptOptimizer

_DEMO_TEMPLATE = "\n### Demonstration\nInput: {question}\nExpected: {answer}\n"


class FewShotPromptOptimizer(IPromptOptimizer):
    """Enriches prompts with labeled demonstrations using pure string logic."""

    def optimize(self, base_prompt: str, examples: list[tuple[str, str]]) -> str:
        """Append every (input, expected-output) demonstration to the base prompt."""
        demo_template = _DEMO_TEMPLATE
        demos = [demo_template.format(question=question, answer=answer) for question, answer in examples]
        return base_prompt + "".join(demos)
