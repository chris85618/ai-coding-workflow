# ADR-STR-009: Ruff Line-Length = 120

## Status

Accepted — 2026-05-16

## Context

重構 `src` 目錄將多 class 的 `.py` 檔案拆分為資料夾結構後，所有子模組的
fully-qualified import 路徑長度可達 90–100 字元。

例如：
```python
from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_analysis_result import (
    RootCauseAnalysisResult,
)
```

在預設的 `line-length = 88` 設定下，這類 import 語句的 `from ... import (` 行本身即超長，
且無法透過 ruff formatter 自動換行（它只能縮短 import 清單，無法縮短模組路徑）。

## Decision

將 `ruff.toml` 和 `pyproject.toml` 中的 `line-length` 從 88 提升至 **120**。

**禁止使用 `# noqa: E501`**：

- `# noqa` 是主動的靜態分析繞行（suppression），會遮蔽未來真正的長行問題
- ADR-GOV-022 規範 CM-GATE 要求所有繞行必須進入 ADR，而非散落在 source code
- 120 字元是 Python 社群中廣泛接受的現代標準（Black 的 `--line-length=88` 是保守值）

## Consequences

| 面向 | 說明 |
|------|------|
| **正面** | 消除所有 `# noqa: E501`；import 路徑可完整表達模組層級 |
| **正面** | 120 字元仍在單一 4K 螢幕的可讀範圍內，不需水平滾動 |
| **正面** | `mypy` + `ruff check` + `ruff format` 三個 gate 全部通過 |
| **中性** | 需同步更新 `pyproject.toml` 中 `[tool.ruff]` 與 `ruff.toml` 兩處設定 |
| **限制** | 禁止新增任何 `# noqa: E501`；例外須重新提交 ADR |

## References

- Traceable to: FR-001 (架構純潔性), ADR-GOV-022 (CM-GATE inline 宣告規範)
- Triggered by: `src/` 重構（每個 class 獨立一個檔案，LESSON-034 範圍保護）
- Files changed: `ruff.toml`, `pyproject.toml`
