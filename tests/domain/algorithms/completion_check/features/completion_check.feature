# SC-009: Pre-Release Completion Check
# Traceable to: UC-009 (covers), INV-016 (verifies)

Feature: Pre-Release Completion Check
  As the release control system
  I want to verify all quality gates before shipping
  So that no incomplete work reaches production

  Scenario: All checks pass and ship is allowed
    Given Stage 8 HITL has confirmed PASS
    When the pre-release completion check executes
    Then traceability integrity is PASS
    And quality gate is PASS
    And security audit is PASS
    And tech debt check is PASS
    And the ship command is allowed

  Scenario: Traceability integrity fails and blocks ship
    Given orphan IDs exist in the registry
    When the pre-release completion check executes
    Then traceability integrity is FAIL
    And the ship command is blocked
    And the missing trace links are listed
