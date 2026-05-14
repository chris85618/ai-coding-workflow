# SC-008: Tech Debt Management
# Traceable to: UC-008 (covers), INV-015 (verifies)

Feature: Tech Debt Management
  As the debt management system
  I want to track and prioritize technical debt with RICE scoring
  So that debt items are handled in optimal order

  Scenario: SonarCloud finding converts to tech debt
    Given SonarCloud scan finds a Major Code Smell
    When the finding is registered as tech debt
    Then a DEBT ID is created
    And RICE score is calculated
    And the four quadrant classification is completed
    And the item is written to tech-debt-register.md

  Scenario: RICE score is calculated correctly
    Given reach is 50 and impact is 2.0 and confidence is 0.8 and effort is 5
    When RICE score is calculated
    Then the score equals 16.0
    And the quadrant is STRATEGIC because impact is at least 2 and effort exceeds 2
