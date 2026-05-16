# SC-001-v2: Pipeline Start (Autonomous)
# Traceable to: UC-001 (covers), INV-001 (verifies), INV-002-v2 (verifies)
# Changed by: design-change-autonomous.md

Feature: Autonomous Pipeline Start
  As an AI coding tool
  I want to start and run the full pipeline autonomously
  So that all stages execute without human intervention

  Scenario: Full pipeline runs autonomously end to end
    Given the project docs directory exists
    And no LangGraph checkpoint exists
    When the pipeline executes
    Then all stages run sequentially without human intervention
    And each stage writes its artifacts to docs/
    And the pipeline completes with status COMPLETED

  Scenario: Pipeline reads existing docs on new project
    Given docs/ contains requirements.md and domain-model.md from a prior run
    When the pipeline starts
    Then it reads existing artifacts before processing
    And builds upon existing IDs and trace links
    And does not duplicate existing IDs

  Scenario: Pipeline position only advances forward
    Given the pipeline is at position P2
    When auto-gate passes
    Then the pipeline position is strictly greater than P2
    And the position does not go backward

  Scenario: Auto-gate passes after stage completion
    Given a stage has completed its iteration loop
    And auto-gate evaluates GateDecision PASS
    When advance is called
    Then the pipeline advances to the next stage
    And no human confirmation is required
