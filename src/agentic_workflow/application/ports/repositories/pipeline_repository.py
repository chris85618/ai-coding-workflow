"""Port: Repository for Pipeline aggregates."""

from __future__ import annotations

from abc import ABC, abstractmethod

from agentic_workflow.domain.aggregates.pipeline import Pipeline


class IPipelineRepository(ABC):
    """Interface for pipeline persistence."""

    @abstractmethod
    def get_by_id(self, pipeline_id: str) -> Pipeline | None:
        """Retrieve a pipeline by ID."""
        pass

    @abstractmethod
    def save(self, pipeline: Pipeline) -> None:
        """Persist the pipeline state."""
        pass

    @abstractmethod
    def get_current(self) -> Pipeline | None:
        """Retrieve the current active pipeline (e.g., from workflow-state.md)."""
        pass
