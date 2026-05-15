# ADR-GOV-026: Zero-Tolerance Warning Policy and Strict Scoping

## Status
Proposed

## Context
The project aims for maximum reliability and code quality. Pytest warnings often indicate underlying logic issues or future breaking changes. Previous attempts to use `filterwarnings` to ignore `stdlib` warnings (like `runpy`) were rejected in favor of fixing the root cause logic.

## Decision
1. **Zero-Tolerance**: All warnings encountered during test execution must result in a test failure (`filterwarnings = ["error"]`).
2. **Logic over Exclusion (Universal)**: If a standard library, internal module, or **third-party package** emits a warning, the implementation or test logic must be refactored to eliminate the warning. Exclusions in `pyproject.toml` are strictly forbidden for internal code and strongly discouraged for third-party code.
3. **Third-Party Strict Scoping & Justification**: Only third-party dependencies are allowed in the `filterwarnings` ignore list, and ONLY IF refactoring is technically impossible. They MUST be:
   - Scoped to specific module names using regex.
   - Accompanied by documentation in the commit/ADR explaining the failed refactoring attempts.
4. **Autonomous Enforcement**: This policy is enforced by the LangGraph orchestration flow. A mandatory `warning_policy_gate` node in the micro-validation subgraph scans `pyproject.toml` changes and rejects any new exclusion that lacks justification or covers fixable logic.

## Consequences
- Guaranteed zero-regression of warning-related technical debt.
- Higher requirement for deep understanding of third-party dependency behaviors.
- The LangGraph workflow will now autonomously reject "easy" exclusion-based fixes.
