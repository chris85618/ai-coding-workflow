# SC-016: Context Budget Allocation
# Traceable to: UC-003 (covers), INV-021 (verifies), ALG-007

Feature: Context Budget Allocation
  As the workflow system
  I want to allocate token budgets across context sources
  So that LLM requests stay within cost limits

  Scenario: Budget splits across task, files, and repo map
    Given total budget is 4000 tokens
    When context is allocated
    Then task context gets up to 50 percent of budget
    And current files get up to 70 percent of remainder
    And repo map gets the rest

  Scenario: Total allocation never exceeds budget
    Given total budget is 2000 tokens
    When all context sources are assembled
    Then total allocated tokens do not exceed 2000

  Scenario: Large task context squeezes repo map
    Given total budget is 3000 tokens
    And task context alone is 2000 tokens
    When context is allocated
    Then repo map gets at most 300 tokens
