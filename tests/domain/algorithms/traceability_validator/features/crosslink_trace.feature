# SC-011: Full-Chain Cross-Link Tracing
# Traceable to: UC-011 (covers), INV-009, INV-019 (verifies)

Feature: Full Chain Cross Link Tracing
  As the traceability engine
  I want to trace all link directions when an ID changes
  So that ADR validity and NFR satisfaction are continuously verified

  Scenario: Modified FR still satisfies all related ADRs
    Given FR-005 is modified
    And FR-005 is justified by ADR-GOV-003 and ADR-GOV-004 and ADR-GOV-006
    When CrossLinkTracer executes full direction tracing
    Then all 3 ADR files are read completely
    And all 3 ADRs are verified to still hold
    And all link types are semantically valid
    And the CrossLinkReport has no violations

  Scenario: Modification invalidates an ADR
    Given a FEA is significantly modified
    And ADR-STR-001 justifies that FEA architecture decision
    When CrossLinkTracer finds ADR-STR-001 premise no longer holds
    Then ADR-STR-001 is marked SUPERSEDED
    And CrossLinkViolationDetected event is emitted
    And HITL is notified that a new ADR is needed
    And severity is escalated to MAJOR

  Scenario: Modification violates an NFR
    Given CLS-006 is modified
    And NFR-002 constrains CLS-006 design
    When CrossLinkTracer finds NFR-002 is no longer satisfied
    Then a Violation is recorded with type NFR_VIOLATED
    And severity is escalated to MAJOR
    And HITL is notified

  Scenario: Lateral tracing includes RISK links
    Given RISK-004 mitigates FEA-006
    And FEA-006 related FR is modified
    When CrossLinkTracer executes full direction tracing
    Then RISK-004 mitigation action is re-verified
    And if the action is no longer effective it is reported
