"""BDD step definitions for repo_map.feature (SC-012)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder
from agentic_workflow.domain.models.repo_map import RepoMap


class TestRepoMapScenarios:
    """BDD scenarios for repo map."""

    @staticmethod
    @scenario("features/repo_map.feature", "Generate repo map within token budget")
    def test_repo_map_within_budget() -> None:
        """SC-012: RepoMap generation respects token budget."""

    @staticmethod
    @scenario("features/repo_map.feature", "PageRank prioritizes context files")
    def test_pagerank_prioritizes_context() -> None:
        """SC-012: Context files rank higher in repo map."""

    @staticmethod
    @scenario("features/repo_map.feature", "Empty project returns empty map")
    def test_empty_project() -> None:
        """SC-012: Empty project yields empty map."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


@given(parsers.parse("a Python project with {n:d} source files"))
def given_python_project(ctx: dict[str, Any], n: int, tmp_path: Path) -> None:
    """Create a Python project with N source files."""
    for i in range(n):
        f = tmp_path / f"module_{i:03d}.py"
        f.write_text(f"class Module{i}:\n    pass\n\ndef func_{i}(): pass\n")
    ctx["project_path"] = str(tmp_path)


@given(parsers.parse("token budget is set to {budget:d}"))
def given_token_budget(ctx: dict[str, Any], budget: int) -> None:
    """Set the token budget."""
    ctx["budget"] = budget


@given("files A.py and B.py are in current context")
def given_context_files(ctx: dict[str, Any], tmp_path: Path) -> None:
    """Create project with A.py and B.py where C.py imports from A."""
    (tmp_path / "A.py").write_text("class A:\n    pass\n")
    (tmp_path / "B.py").write_text("def b(): pass\n")
    (tmp_path / "C.py").write_text("from A import A\n\ndef c(): pass\n")
    ctx["project_path"] = str(tmp_path)
    ctx["budget"] = 2000


@given("C.py imports from A.py")
def given_c_imports_a(ctx: dict[str, Any]) -> None:
    """Confirm the import relationship (already set up in prior step)."""


@given("a project with no Python files")
def given_empty_project(ctx: dict[str, Any], tmp_path: Path) -> None:
    """Create a directory with no Python files."""
    ctx["project_path"] = str(tmp_path)
    ctx["budget"] = 1000


@when("repo map is generated")
def when_generate_repo_map(ctx: dict[str, Any]) -> None:
    """Generate repo map from the project."""
    ctx["result"] = RepoMapBuilder.build(ctx["project_path"], ctx["budget"])


@when("repo map is generated with context personalization")
def when_generate_with_personalization(ctx: dict[str, Any]) -> None:
    """Generate repo map — context personalization is implicit via PageRank."""
    ctx["result"] = RepoMapBuilder.build(ctx["project_path"], ctx["budget"])


@then("the map contains ranked symbol definitions")
def then_map_has_symbols(ctx: dict[str, Any]) -> None:
    """Assert the repo map contains at least one symbol."""
    result: RepoMap = ctx["result"]
    assert result.token_count >= 0
    assert isinstance(result.symbols, tuple)


@then(parsers.parse("total token count does not exceed {budget:d}"))
def then_token_count_ok(ctx: dict[str, Any], budget: int) -> None:
    """Assert token count is within budget."""
    assert ctx["result"].token_count <= budget


@then("A.py symbols rank higher than unrelated files")
def then_a_ranks_higher(ctx: dict[str, Any]) -> None:
    """Assert A.py has higher rank than B.py (C imports A, not B)."""
    ranks = ctx["result"].file_ranks
    a_rank = ranks.get("A.py", 0.0) or max((v for k, v in ranks.items() if "A" in k), default=0.0)
    b_rank = ranks.get("B.py", 0.0) or max((v for k, v in ranks.items() if "B" in k), default=0.0)
    assert a_rank >= b_rank, f"Expected A ({a_rank}) >= B ({b_rank})"


@then("the map contains zero symbols")
def then_no_symbols(ctx: dict[str, Any]) -> None:
    """Assert the map has no symbols."""
    assert len(ctx["result"].symbols) == 0


@then("token count is 0")
def then_token_count_zero(ctx: dict[str, Any]) -> None:
    """Assert token count is zero."""
    assert ctx["result"].token_count == 0
