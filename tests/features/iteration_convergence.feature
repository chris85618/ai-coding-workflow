# SC-003-v2: Iteration Stage Convergence (Autonomous)
# Traceable to: UC-003 (covers), INV-003, INV-004, INV-005-v2 (verifies)
# Changed by: design-change-autonomous.md

Feature: Autonomous Iteration Stage Convergence
  As the workflow system
  I want Agent alpha and beta to iterate until convergence
  So that each stage auto-passes at fixed point without human gates

  Scenario: Auto-convergence at fixed point (REACHED)
    Given Stage N is ready for iteration
    When Agent alpha critiques and all findings are YAGNI severity
    Then fixed point is REACHED
    And the stage auto-passes without human confirmation
    And stage artifacts are written to docs/

  Scenario: Max iterations reached auto-advances
    Given Stage N is iterating
    And iteration count has reached 10
    When the 11th iteration would begin
    Then a warning is logged with message MAX_ITERATIONS reached
    And the stage auto-advances
    And no human intervention is requested
    And artifacts produced so far are written to docs/

  Scenario: NOT_REACHED continues autonomously
    Given Step M micro-validation has passed
    And there are still CRITICAL or HIGH unresolved findings
    When fixed point check executes
    Then the result is NOT_REACHED
    And Agent alpha automatically re-critiques
    And iteration count increments by 1
    And no human gate triggers

  Scenario: MAJOR impact logged but execution continues
    Given impact analysis classifies severity as MAJOR
    When the result is processed
    Then a warning is logged with full blast radius details
    And execution continues autonomously
    And the warning is recorded in the stage artifacts

  Scenario: Stage status transitions are unidirectional
    Given a stage with status PENDING
    When the stage transitions to ITERATING
    Then the status cannot return to PENDING
    And later transitions to PASSED are final

  Scenario: Micro-validation failure auto-retries then skips
    Given a micro-validation step fails
    When auto-fix is attempted 3 times and all fail
    Then the failure is logged as a warning
    And execution continues to the next step
    And no escalation to human occurs
