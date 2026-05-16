# SC-013: Hook Execution
# Traceable to: UC-013 (covers), INV-020 (verifies), CLS-016

Feature: Lifecycle Hook Execution
  As the workflow system
  I want deterministic hooks at lifecycle events
  So that quality gates are enforced without relying on LLM memory

  Scenario: PreStageStart hook runs before stage logic
    Given a hook is registered for PRE_STAGE_START event
    When the stage begins execution
    Then the hook command executes before any stage logic
    And hook exit code 0 allows the stage to proceed

  Scenario: Hook exit code 2 blocks stage execution
    Given a blocking hook is registered for PRE_STAGE_START
    And the hook command returns exit code 2
    When the hook executes
    Then the stage execution is blocked
    And stderr content is logged as a warning

  Scenario: PostDocWrite hook auto-formats Python files
    Given a PostDocWrite hook runs ruff format on the file
    When a Python file is written to docs/
    Then the file is automatically formatted by ruff
    And no manual formatting is needed

  Scenario: Multiple hooks execute in registration order
    Given hooks A and B are registered for POST_STAGE_COMPLETE
    When POST_STAGE_COMPLETE fires
    Then hook A executes before hook B
