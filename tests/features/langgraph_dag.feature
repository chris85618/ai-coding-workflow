Feature: LangGraph DAG Builder and Invariants
  As a system architect
  I want to dynamically construct a LangGraph DAG from config.yaml and verify its structural invariants
  So that the autonomous workflow execution follows a strict and deterministic edge flow

  Scenario: Graph Builder constructs a valid StateGraph from config.yaml
    Given a valid config.yaml with workflow_graph configuration
    When the graph builder compiles the LangGraph
    Then it should return a compiled graph
    And the graph should contain "start_pipeline" node
    And the graph should contain "orchestrator" node

  Scenario: Invariants Verifier passes on a correctly structured DAG
    Given a compiled LangGraph built from config.yaml
    When the DAG Invariant Verifier checks the graph
    Then all structural invariants should pass
    And there should be zero validation failures
