"""BDD step definitions for the Archon workflow document scenarios.

ADR-STR-033: The exported Archon workflow document is the only
orchestration authority; LangGraph and internal graph runners are removed.

Traceable to: INV-001, INV-002, INV-003, SC-015, SC-016, FR-077, FR-078
"""

from typing import Any

from pytest_bdd import given, scenario, then, when

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
from agentic_workflow.frameworks.archon_orchestrator import ArchonOrchestrator


@scenario(
    "../features/archon_workflow.feature",
    "Workflow mapper exports a valid Archon workflow document",
)
def test_workflow_mapper_exports_valid_document() -> None:
    """BDD scenario: Workflow mapper exports a valid Archon workflow document."""


@scenario(
    "../features/archon_workflow.feature",
    "Invariants Verifier passes on the exported workflow document",
)
def test_invariants_verifier_passes_on_exported_document() -> None:
    """BDD scenario: Invariants Verifier passes on the exported workflow document."""


@given("the canonical pipeline positions")
def given_canonical_positions(context: dict[str, Any]) -> None:
    """BDD given: canonical position order from the Pipeline aggregate (SSOT)."""
    context["positions"] = list(Pipeline(pipeline_id="bdd").stages)


@when("the orchestrator gateway exports the Archon workflow")
def when_gateway_exports(context: dict[str, Any]) -> None:
    """BDD when: export the workflow document through the gateway."""
    context["workflow_doc"] = ArchonOrchestrator().export_workflow("bdd", context["positions"])


@then("the document should carry the workflow header")
def then_document_has_header(context: dict[str, Any]) -> None:
    """BDD then: verify the document header."""
    assert context["workflow_doc"].startswith("name: agentic-workflow-bdd\n")


@then('the document should contain a "start" step')
def then_document_contains_start(context: dict[str, Any]) -> None:
    """BDD then: verify start step presence."""
    assert "- id: start\n" in context["workflow_doc"]


@then("every command step should invoke the single-node runner")
def then_steps_invoke_single_node_runner(context: dict[str, Any]) -> None:
    """BDD then: every workflow-node command goes through scripts/run_node.py (FR-077)."""
    node_lines = [line for line in context["workflow_doc"].splitlines() if "--node" in line]
    assert node_lines
    assert all("scripts/run_node.py" in line for line in node_lines)


@given("an exported Archon workflow document")
def given_exported_document(context: dict[str, Any]) -> None:
    """BDD given: exported workflow document."""
    positions = list(Pipeline(pipeline_id="bdd").stages)
    context["workflow_doc"] = ArchonOrchestrator().export_workflow("bdd", positions)


@when("the DAG Invariant Verifier checks the document")
def when_verifier_checks_document(context: dict[str, Any]) -> None:
    """BDD when: run structural verification over the exported topology."""
    context["verification_result"] = DAGInvariantVerifier.run_all_verifications(context["workflow_doc"])


@then("all structural invariants should pass")
def then_invariants_should_pass(context: dict[str, Any]) -> None:
    """BDD then: verify structural pass."""
    result = context["verification_result"]
    assert result["passed"] is True


@then("there should be zero validation failures")
def then_zero_validation_failures(context: dict[str, Any]) -> None:
    """BDD then: verify zero failures."""
    result = context["verification_result"]
    assert len(result["failures"]) == 0
