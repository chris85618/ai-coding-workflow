# SC-014: LLM Strategy Pattern Selection
# Traceable to: UC-003 (covers), INV-022 (verifies), CLS-017, ALG-008

Feature: LLM Strategy Pattern Selection
  As the workflow system
  I want to select different LLM models per task type
  So that reasoning tasks use strong models and editing uses fast models

  Scenario: Agent alpha uses reasoning model for critique
    Given strategy config has reasoning_model set to opus
    When task_type is CRITIQUE
    Then ModelConfig.model is opus
    And ModelConfig.provider is anthropic

  Scenario: Agent beta uses editing model for resolve
    Given strategy config has editing_model set to gpt-4o
    When task_type is RESOLVE
    Then ModelConfig.model is gpt-4o
    And ModelConfig.provider is openai

  Scenario: Simple formatting uses cheapest model
    Given strategy config has cheap_model set to gpt-4o-mini
    When task_type is FORMAT
    Then ModelConfig.model is gpt-4o-mini

  Scenario: Fallback when provider is disabled
    Given provider anthropic is disabled in config
    And reasoning_model uses anthropic
    When task_type is CRITIQUE
    Then fallback_model is selected instead
    And a warning is logged about provider unavailability

  Scenario: All configured providers are listed
    Given strategy config has 3 providers enabled
    When list_providers is called
    Then 3 provider names are returned
