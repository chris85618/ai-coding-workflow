# SC-015: Atomic Git Commits per Stage
# Traceable to: UC-003 (covers), INV-023 (verifies), FR-027

Feature: Atomic Git Commits per Stage
  As the workflow system
  I want to auto-commit all artifacts at each stage completion
  So that every AI change is traceable and reversible via git

  Scenario: Stage completion triggers atomic git commit
    Given Stage 3 has completed with updated artifacts in docs/
    When auto_commit executes via GitKraken MCP
    Then a git commit is created
    And commit message starts with "[Stage 3]"
    And all changed stage artifacts are included

  Scenario: No changes means no commit
    Given a stage produces no artifact changes
    When auto_commit checks for changes
    Then no git commit is created
    And no error is raised

  Scenario: Commit includes all stage files atomically
    Given Stage 5 updated ooad-design.md and domain-model.md
    When auto_commit executes
    Then both files are in the same single commit
