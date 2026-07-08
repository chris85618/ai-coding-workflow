Feature: Archon Workflow Document and Invariants
  As a system architect
  I want to export the master pipeline as an Archon workflow document and verify its structural invariants
  So that the sole orchestration engine executes a strict and deterministic flow (ADR-STR-033)

  Scenario: Workflow mapper exports a valid Archon workflow document
    Given the canonical pipeline positions
    When the orchestrator gateway exports the Archon workflow
    Then the document should carry the workflow header
    And the document should contain a "start" step
    And every command step should invoke the single-node runner

  Scenario: Invariants Verifier passes on the exported workflow document
    Given an exported Archon workflow document
    When the DAG Invariant Verifier checks the document
    Then all structural invariants should pass
    And there should be zero validation failures
