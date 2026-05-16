"""Coverage for ABC port interfaces — hitting the 'pass' statements."""

from typing import Any

from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.algorithms.base_specification import Specification


def test_agent_reasoner_abc_coverage() -> None:
    """Cover IAgentReasoner abstract method bodies."""

    class DummyReasoner(IAgentReasoner):
        def reason(self, prompt: str, system_message: str | None = None) -> str:
            return super().reason(prompt, system_message)  # type: ignore

        def extract_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
            return super().extract_structured(prompt, schema)  # type: ignore

    d = DummyReasoner()
    assert d.reason("p") is None
    assert d.extract_structured("p", {}) is None


def test_pipeline_repository_abc_coverage() -> None:
    """Cover IPipelineRepository abstract method bodies."""

    class DummyRepo(IPipelineRepository):
        def save(self, pipeline: Any) -> None:
            super().save(pipeline)  # type: ignore

        def get_by_id(self, pipeline_id: str) -> Any:
            return super().get_by_id(pipeline_id)  # type: ignore

        def get_current(self) -> Any:
            return super().get_current()  # type: ignore

    d = DummyRepo()
    d.save(None)
    assert d.get_by_id("id") is None
    assert d.get_current() is None


def test_base_specification_abc_coverage() -> None:
    """Cover Specification abstract method bodies."""

    class DummySpec(Specification[Any]):
        def is_satisfied_by(self, candidate: Any) -> bool:
            return super().is_satisfied_by(candidate)  # type: ignore

    d = DummySpec()
    assert d.is_satisfied_by(None) is None
