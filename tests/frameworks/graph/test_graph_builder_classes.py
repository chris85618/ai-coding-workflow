"""Frameworks OO graph builder class interface."""


class TestGraphBuilderClasses:
    """Frameworks OO graph builder class interface."""

    def test_micro_validation_graph_builder_returns_compiled(self) -> None:
        """TC-215: MicroValidationGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import MicroValidationGraphBuilder

        graph = MicroValidationGraphBuilder.build()
        assert graph is not None

    def test_iteration_graph_builder_returns_compiled(self) -> None:
        """TC-216: IterationGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import IterationGraphBuilder

        graph = IterationGraphBuilder.build()
        assert graph is not None

    def test_master_graph_builder_returns_compiled(self) -> None:
        """TC-217: MasterGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import MasterGraphBuilder

        graph = MasterGraphBuilder.build()
        assert graph is not None
