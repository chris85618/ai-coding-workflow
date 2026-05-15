Feature: Configuration Interpolation
  As a developer
  I want to reference environment variables in my config.yaml
  So that sensitive information is kept out of version control

  @ADR-STR-011 @security
  Scenario: Successfully interpolate environment variables in configuration
    Given a configuration file with "${TEST_API_KEY}" as an api_key
    And the environment variable "TEST_API_KEY" is set to "sk-test-123"
    When I load the configuration
    Then the loaded api_key should be "sk-test-123"

  @ADR-STR-011
  Scenario: Use default value when environment variable is missing
    Given a configuration file with "${MISSING_VAR:default_val}" as a name
    And the environment variable "MISSING_VAR" is NOT set
    When I load the configuration
    Then the loaded name should be "default_val"
