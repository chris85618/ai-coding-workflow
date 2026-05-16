# SC-012: RepoMap Generation
# Traceable to: UC-012 (covers), INV-024 (verifies), ALG-006
# Created by: feature-absorption-design.md

Feature: Repository Map Generation
  As the workflow system
  I want to generate a condensed repo map via tree-sitter
  So that LLM context is focused and token-efficient

  Scenario: Generate repo map within token budget
    Given a Python project with 50 source files
    And token budget is set to 1000
    When repo map is generated
    Then the map contains ranked symbol definitions
    And total token count does not exceed 1000

  Scenario: PageRank prioritizes context files
    Given files A.py and B.py are in current context
    And C.py imports from A.py
    When repo map is generated with context personalization
    Then A.py symbols rank higher than unrelated files

  Scenario: Empty project returns empty map
    Given a project with no Python files
    When repo map is generated
    Then the map contains zero symbols
    And token count is 0
