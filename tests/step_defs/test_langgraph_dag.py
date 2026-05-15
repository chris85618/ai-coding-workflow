import pytest
from pytest_bdd import scenario, given, when, then
from agentic_workflow.adapters.langgraph.graph_builder import build_graph_from_config
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier

@scenario('../features/langgraph_dag.feature', 'Graph Builder constructs a valid StateGraph from config.yaml')
def test_graph_builder_constructs_valid_stategraph():
    pass

@scenario('../features/langgraph_dag.feature', 'Invariants Verifier passes on a correctly structured DAG')
def test_invariants_verifier_passes_on_correct_dag():
    pass

@given('a valid config.yaml with workflow_graph configuration')
def given_valid_config(monkeypatch):
    # The config.yaml is present in the repository root, so we can just rely on the default.
    pass

@when('the graph builder compiles the LangGraph')
def when_graph_builder_compiles(pytestconfig):
    # Actually build the graph and store it in pytest context or just a local fixture 
    # But since BDD steps share state via fixture dict, let's yield it or return it.
    pass

@pytest.fixture
def context():
    return {}

@when('the graph builder compiles the LangGraph')
def when_compiles_langgraph(context):
    context['compiled_graph'] = build_graph_from_config()

@then('it should return a compiled graph')
def then_returns_compiled_graph(context):
    assert context.get('compiled_graph') is not None
    assert hasattr(context['compiled_graph'], 'nodes')

@then('the graph should contain "start_pipeline" node')
def then_contains_start_pipeline(context):
    graph = context['compiled_graph']
    assert "start_pipeline" in graph.nodes

@then('the graph should contain "orchestrator" node')
def then_contains_orchestrator(context):
    graph = context['compiled_graph']
    assert "orchestrator" in graph.nodes

@given('a compiled LangGraph built from config.yaml')
def given_compiled_langgraph(context):
    context['compiled_graph'] = build_graph_from_config()

@when('the DAG Invariant Verifier checks the graph')
def when_verifier_checks_graph(context):
    context['verification_result'] = DAGInvariantVerifier.run_all_verifications(context['compiled_graph'])

@then('all structural invariants should pass')
def then_invariants_should_pass(context):
    result = context['verification_result']
    assert result["passed"] is True

@then('there should be zero validation failures')
def then_zero_validation_failures(context):
    result = context['verification_result']
    assert len(result["failures"]) == 0
