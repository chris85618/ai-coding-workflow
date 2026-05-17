"""Port Interface — Graph Builders and Verifier Abstractions.

Traceable to: ADR-STR-021
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class IIterationGraphBuilder(ABC):
    """Abstract interface for building iteration graph."""

    @classmethod
    @abstractmethod
    def build(cls) -> Any:
        """Build and compile the dual-agent iteration subgraph."""


class IMasterGraphBuilder(ABC):
    """Abstract interface for building master graph."""

    @classmethod
    @abstractmethod
    def build(cls, checkpointer: Any | None = None) -> Any:
        """Build and compile the master pipeline graph."""


class IMicroValidationGraphBuilder(ABC):
    """Abstract interface for building micro-validation graph."""

    @classmethod
    @abstractmethod
    def build(cls) -> Any:
        """Build and compile the micro-validation subgraph."""


class IGraphVerifier(Protocol):
    """Protocol interface for formal graph verification."""

    @classmethod
    def run_all_verifications(cls, graph: Any) -> dict[str, Any]:
        """Verify the graph configuration and return results."""
