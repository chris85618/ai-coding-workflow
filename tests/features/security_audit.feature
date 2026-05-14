# SC-006: Three Layer Security Audit
# Traceable to: UC-006 (covers), INV-014 (verifies)

Feature: Three Layer Security Audit
  As the quality assurance system
  I want to run 3-layer security audits
  So that all security aspects are verified before release

  Scenario: All three layers pass
    Given the design or implementation is complete
    When the three layer security audit executes
    Then Layer 1 CSO passes
    And Layer 2 AgentShield passes
    And Layer 3 SkillFortify passes
    And the overall result is PASS

  Scenario: Layer 2 HIGH finding triggers redesign
    Given Layer 1 passes
    When Layer 2 discovers a HIGH severity issue
    Then the overall result is FAIL
    And AuditFailed event is emitted
    And the system returns to design stage for fixes
