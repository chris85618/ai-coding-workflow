# SC-010-v2: Checkpoint Resume (No workflow-state.md, No HITL)
# Traceable to: UC-010 (covers), INV-001, INV-018 (verifies)
# Changed by: design-change-autonomous.md

Feature: Autonomous Checkpoint Resume
  As an AI coding tool
  I want to resume from LangGraph checkpoint automatically
  So that interrupted executions continue without human decision

  Scenario: Resume from LangGraph checkpoint
    Given a previous execution was interrupted
    And a LangGraph checkpoint exists
    When the pipeline starts
    Then execution resumes from the checkpoint position automatically
    And previously completed stages are not re-executed
    And existing docs/ artifacts are preserved
    And no human confirmation is required

  Scenario: No checkpoint with existing docs starts from Phase 0
    Given no LangGraph checkpoint exists
    And docs/ contains requirements.md from a prior run
    When the pipeline starts
    Then execution begins from Phase 0
    And existing docs/ artifacts are read as input
    And new artifacts build upon existing IDs

  Scenario: No checkpoint and empty docs starts fresh
    Given no LangGraph checkpoint exists
    And docs/ directory is empty
    When the pipeline starts
    Then execution begins from Phase 0
    And all IDs are generated from scratch

  Scenario: Checkpoint preserves passed gates
    Given a checkpoint exists at Stage 5
    And Stage 3 and Stage 4 are marked PASSED in checkpoint
    When the pipeline resumes
    Then Stage 3 and Stage 4 are not re-executed
    And Stage 5 begins iteration immediately
