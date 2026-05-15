# ADR-GOV-026: Zero-Tolerance Warning Policy and Strict Scoping

## Status
Proposed

## Context
The project aims for maximum reliability and code quality. Pytest warnings often indicate underlying logic issues or future breaking changes. Previous attempts to use `filterwarnings` to ignore `stdlib` warnings (like `runpy`) were rejected in favor of fixing the root cause logic.

## Decision
1. **Zero-Tolerance**: All warnings encountered during test execution must result in a test failure (`filterwarnings = ["error"]`).
2. **Logic over Exclusion**: If a standard library or internal module emits a warning, the implementation or test logic must be refactored to eliminate the warning. Exclusions in `pyproject.toml` are strictly forbidden for internal code.
3. **Third-Party Strict Scoping**: Only third-party dependencies are allowed in the `filterwarnings` ignore list, and they MUST be scoped to their specific module names using regex to prevent accidental masking of internal warnings.
4. **Prohibition of Broad Ignores**: Any ignore rule without a specific module scope (e.g., `ignore::DeprecationWarning`) is prohibited.

## Consequences
- Increased CI sensitivity to dependency updates.
- Higher maintenance effort for test logic involving complex imports (e.g., `runpy`).
- Guaranteed visibility of all potential issues in the `agentic_workflow` codebase.
