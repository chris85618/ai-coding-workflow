"""Unit tests for the simplified PageRank implementation."""

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestPagerank:
    """Unit tests for the simplified PageRank implementation."""

    def test_empty_graph_returns_empty(self) -> None:
        """L119-120: empty graph → return {}."""
        result = RepoMapBuilder.pagerank({})
        assert result == {}

    def test_single_node_no_links(self) -> None:
        """Single node with no edges → rank converges to (1-damping)/n = 0.15."""
        result = RepoMapBuilder.pagerank({"a.py": []})
        assert "a.py" in result
        # With damping=0.85, n=1: stable rank = (1-0.85)/1 = 0.15
        assert abs(result["a.py"] - 0.15) < 0.01

    def test_two_nodes_one_imports(self) -> None:
        """a.py imports b.py → b.py gets higher rank."""
        result = RepoMapBuilder.pagerank({"a.py": ["b.py"], "b.py": []})
        # b.py is imported → it receives rank contribution
        assert result["b.py"] >= result["a.py"]

    def test_isolated_nodes_equal_rank(self) -> None:
        """Nodes with no edges share equal rank."""
        result = RepoMapBuilder.pagerank({"x.py": [], "y.py": [], "z.py": []})
        ranks = list(result.values())
        assert max(ranks) - min(ranks) < 0.01
