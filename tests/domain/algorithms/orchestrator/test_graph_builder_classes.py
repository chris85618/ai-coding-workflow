"""Frameworks OO graph builder class interface."""

from agentic_workflow.frameworks.graph import (
    IterationGraphBuilder,
    MasterGraphBuilder,
    MicroValidationGraphBuilder,
)


class TestGraphBuilderClasses:
    """Frameworks OO graph builder class interface."""

    def test_micro_validation_graph_builder_returns_compiled(self) -> None:
        """TC-215: MicroValidationGraphBuilder static method."""
        graph = MicroValidationGraphBuilder.build()
        assert graph is not None

    def test_iteration_graph_builder_returns_compiled(self) -> None:
        """TC-216: IterationGraphBuilder static method."""
        graph = IterationGraphBuilder.build()
        assert graph is not None

    def test_master_graph_builder_returns_compiled(self) -> None:
        """TC-217: MasterGraphBuilder static method."""
        graph = MasterGraphBuilder.build()
        assert graph is not None
