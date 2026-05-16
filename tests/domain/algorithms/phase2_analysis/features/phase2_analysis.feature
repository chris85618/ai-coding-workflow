# SC-002: Phase 2 Project Analysis
# Traceable to: UC-002 (covers), INV-017 (verifies)

Feature: Phase 2 Project Analysis
  As a developer
  I want to execute Phase 2 four-step analysis
  So that BG, S, and FEA IDs are assigned with full traceability

  Scenario: Phase 2 produces complete IDs
    Given Phase 0 and Phase 1 are completed
    When Phase 2 four steps execute
    Then at least 1 BG ID is assigned
    And at least 1 S ID is assigned
    And at least 1 FEA ID is assigned
    And the traceability matrix is initialized
    And every BG has at least one FEA downstream link

  Scenario: Red Team challenge finds scope conflict
    Given FEA IDs are defined
    When Red Team challenge discovers mutually exclusive features
    Then the HITL gate triggers
    And the user decides on scope adjustment
    And adjusted FEA IDs update in the traceability matrix
