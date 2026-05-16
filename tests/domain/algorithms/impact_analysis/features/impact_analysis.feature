# SC-005: Impact Analysis Blast Radius
# Traceable to: UC-005 (covers), INV-012, INV-013 (verifies)

Feature: Impact Analysis Blast Radius
  As the traceability engine
  I want to calculate blast radius and classify severity
  So that high-impact changes trigger HITL intervention

  Scenario: COSMETIC level change with no downstream
    Given a change to an ID with no downstream links
    When impact analysis calculates
    Then blast radius equals 0
    And severity is COSMETIC
    And the change record is written to the corresponding ADR

  Scenario: MINOR level change within same stage
    Given a change to an ID with 3 or fewer downstream links in the same stage
    When impact analysis calculates
    Then severity is MINOR

  Scenario: MAJOR level change triggers HITL
    Given a change to an ID with more than 10 downstream links or crossing 2 plus stages
    When impact analysis calculates
    Then severity is MAJOR
    And the system automatically escalates to HITL
    And the change record is written to the corresponding ADR

  Scenario: Severity is monotonic with blast radius
    Given change A has blast radius 5 and change B has blast radius 15
    When severity is calculated for both
    Then severity of B is greater than or equal to severity of A
