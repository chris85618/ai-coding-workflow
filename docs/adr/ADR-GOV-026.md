# ADR-GOV-026: Zero-Tolerance Warning Policy and Strict Scoping

## Status

Accepted — Updated 2026-05-16

## Context

The project aims for maximum reliability and code quality. Pytest warnings often indicate underlying logic issues or future breaking changes. Previous attempts to use `filterwarnings` to ignore warnings were rejected in favour of fixing the root cause.

Two categories of violations were identified as AI-driven abuse patterns:

1. **E402 suppression**: AI added `per-file-ignores = ["tests/*.py" = ["E402"]]` to `ruff.toml` to bypass import-order violations caused by its own ill-structured code, instead of restructuring the imports correctly.
2. **DeprecationWarning suppression**: AI added `filterwarnings = ['ignore::DeprecationWarning:gherkin.*']` to suppress a Python 3.14 warning caused by `@tags` in `.feature` files, instead of removing the tags.

Both patterns are **GOVERNANCE_BYPASS** — they hide defects instead of fixing them.

## Decision

1. **Zero-Tolerance**: All warnings during test execution cause test failure (`filterwarnings = ["error"]`).
2. **Logic over Exclusion (Universal)**: If any module emits a warning, refactor the implementation or test to eliminate it. No exclusions in `pyproject.toml` or `ruff.toml`.
3. **E402 is always fixable**: Restructure imports. Never suppress with `per-file-ignores` or `# noqa: E402`.
4. **DeprecationWarning is always fixable**: Fix the root cause (e.g., remove `@tags` from `.feature` files that trigger gherkin TagLine parsing, upgrade the library). Never suppress.
5. **Automated Enforcement** (`WarningPolicyVerifier` / ALG-013): Four rules enforced:
   - Rule 1: No `agentic_workflow` module exclusions
   - Rule 2: All third-party ignores must use `.*` scope regex
   - Rule 3: `E402` never appears in any ignore list or `per-file-ignores`
   - Rule 4: `DeprecationWarning` never appears in any ignore list
6. **Evidence Gate**: Any exception requires `FAILED_REFAC_EVIDENCE` keyword in the commit message and a new ADR entry.

## Consequences

| 面向 | 說明 |
|------|------|
| **正面** | AI 無法用 suppression 掩蓋結構性缺陷 |
| **正面** | `.feature` 文件保持乾淨（無 `@tag` 造成的 TagLine parsing overhead）|
| **正面** | `ruff.toml` 保持零豁免 |
| **中性** | 需要更深入理解第三方函式庫行為 |
| **限制** | `WarningPolicyVerifier` 四條規則強制執行，任何繞行須 ADR |

## References

- Triggered by: AI 濫用 suppression 取代正確修正（LESSON-034 範圍保護）
- Enforced by: `WarningPolicyVerifier.verify_config()` (ALG-013, Rule 3+4 新增)
- Traceable to: NFR-001 (事實優先), ADR-GOV-014 (事實優先失敗報告)
