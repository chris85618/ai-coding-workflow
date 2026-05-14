# SC-007: SonarCloud Quality Gate
# Traceable to: UC-007 (covers), INV-014 (verifies)

Feature: SonarCloud Quality Gate
  As the quality assurance system
  I want to enforce SonarCloud quality thresholds
  So that code quality meets minimum standards before release

  Scenario: All thresholds pass
    Given all tests pass
    When SonarCloud scan executes
    Then coverage is at least 80 percent
    And zero Critical vulnerabilities exist
    And tech debt ratio is at most 5 percent
    And the quality gate result is PASS

  Scenario: Coverage below threshold triggers auto-fix
    Given SonarCloud scan reports coverage at 72 percent
    When auto-fix attempts to add test cases
    Then additional tests are generated
    And the scan is re-executed

  Scenario: Auto-fix fails 3 times then escalates
    Given SonarCloud threshold is not met
    And auto-fix has been attempted 3 times
    When the 4th attempt would begin
    Then the system escalates to HITL
