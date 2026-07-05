"""Domain Service — OrchestratorService.

Coordinates between Pipeline aggregate and complex workflow transitions.
Ensures that phase and stage executions satisfy domain rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import deal

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import PipelineStatus


class IOrchestratorService(ABC):
    """Interface for Orchestrator Service to satisfy Dependency Inversion."""

    @abstractmethod
    def validate_phase_execution(self, pipeline: Pipeline, phase_id: int) -> bool:
        """Validate phase."""

    @abstractmethod
    def prepare_stage_context(self, pipeline: Pipeline) -> dict[str, Any]:
        """Prepare context."""


class OrchestratorService(IOrchestratorService):
    """Domain service for orchestrating complex pipeline transitions."""

    @deal.has()
    @deal.post(lambda result: isinstance(result, bool))
    def validate_phase_execution(self, pipeline: Pipeline, phase_id: int) -> bool:
        """Validates if a specific phase can be executed.

        Args:
            pipeline: The pipeline aggregate.
            phase_id: The phase number (0-10).

        Returns:
            True if valid, False otherwise.
        """
        # Example rule: Phase 1 (Understanding) needs Phase 0 to be complete
        # In our aggregate, this is tracked by stage indices or findings.
        return pipeline.status != PipelineStatus.FAILED

    @deal.ensure(
        lambda _: _.result["pipeline_id"] == _.pipeline.pipeline_id,
        message="Stage context must reference the source pipeline",
    )
    def prepare_stage_context(self, pipeline: Pipeline) -> dict[str, Any]:
        """Prepares domain-rich context for the current stage.

        Args:
            pipeline: The pipeline aggregate.

        Returns:
            A context dictionary derived from the aggregate.
        """
        stage = pipeline.current_stage
        return {
            "pipeline_id": pipeline.pipeline_id,
            "current_stage": stage.name if stage else None,
            "iteration": stage.iteration_count if stage else 0,
            "findings": list(stage.findings) if stage else [],
        }
