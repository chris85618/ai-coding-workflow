# SC-004: Micro-Validation 6-Step Sequence
# Traceable to: UC-004 (covers), INV-006..011 (verifies)

Feature: Micro-Validation Six Step Sequence
  As the traceability engine
  I want to validate every change through 6 sequential steps
  So that all IDs maintain structural integrity and traceability

  Scenario: All six steps pass successfully
    Given a new ID is assigned
    When micro-validation triggers
    Then six steps execute in strict order
    And structure check passes with correct ID format
    And forward trace passes with downstream links or terminal status
    And backward trace passes with upstream links or source status
    And semantic consistency passes with valid link types
    And orphan detection passes
    And impact analysis triggers

  Scenario: Step 3 fails and auto-fix succeeds
    Given backward trace check fails due to missing upstream link
    When auto-fix attempt 1 executes
    Then the missing upstream link is added automatically
    And re-validation passes

  Scenario: Auto-fix fails 3 times then escalates
    Given a step check fails
    And auto-fix has been attempted 3 times
    When the 4th fix attempt would begin
    Then the system escalates to HITL
    And the step is marked as ESCALATED

  Scenario: Self-link is rejected
    Given an attempt to create a TraceLink
    When source and target are the same ID
    Then the link creation is rejected
    And the error message says self-link is forbidden

  Scenario: ID uniqueness violation is rejected
    Given FR-001 already exists in the registry
    When an attempt to create a second FR-001 occurs
    Then the creation is rejected
    And the error message says ID is duplicated

  Scenario: Invalid link type is rejected
    Given a BG ID and a TC ID
    When an attempt to create a link with type realizes
    Then the link is rejected because BG cannot realize TC
