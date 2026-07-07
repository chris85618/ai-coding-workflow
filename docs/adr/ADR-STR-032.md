# ADR-STR-032: Repository 範圍收斂 — 移除框架宿主殘留物

**狀態**: Accepted
**日期**: 2026-07-07
**決策者**: HITL (使用者指示) + Agent α/β 收斂
**追溯**: BG-001, FEA-001, NFR-002, NFR-003 (supersedes), ADR-STR-025, ADR-GOV-016 (Ockham's Razor)

---

## Context

本 repository 的歷史身分有兩個階段：

1. **框架宿主期**（v0.1.0 前後）：repo 同時承載工作流協議文件（`AGENTS.md`）、四個外部工具 submodule（`skills/everything-claude-code`、`skills/gstack`、`skills/understand-anything`、`skills/skillfortify`）與供應鏈產物（`skill-lock.json`、`agentic-workflow.cdx.json`）。
2. **可執行管線期**（v0.1.2 之後）：協議被完整具象化為 `src/agentic_workflow/` 的 LangGraph DAG 與 domain algorithms（各演算法 docstring 標註 `Replaces: skills/workflow-skills/*.md`）。框架協議的正本遷至 `$FRAMEWORK_ROOT`（`~/.setup/ai_coding`），repo 內的 `AGENTS.md` 自述「本文件所在位置 = ~/.setup/ai_coding」，證實其為過期副本。

窮舉掃描（exhaustive-search 協議）證據：

| 項目 | src/ 引用 | tests/ 引用 | CI 引用 | scripts/ 引用 | 唯一引用來源 |
|------|-----------|-------------|---------|---------------|----------------|
| `skills/` 4 submodules | 0 | 0 | 0 | 0 | 早期治理文件（歷史敘述） |
| `AGENTS.md`（repo 副本） | 0（僅 docstring 概念性提及） | 0 | 0 | 0 | README 連結、config.yaml 提示詞措辭 |
| `skill-lock.json` | 0 | 0 | 0 | 0 | tech-debt-register（DEBT-004 歷史） |
| `agentic-workflow.cdx.json` | 0 | 0 | 0 | 0 | tech-debt-register（DEBT-004 歷史） |
| `test_ruff_include*` ×3 | 0 | 0 | 0 | 0 | 無（孤兒 fixture） |
| `coverage_report.txt` | 0 | 0 | 0 | 0 | 已列 .gitignore 仍被追蹤 |
| `tasks/clean_architecture_scan.py` | 0 | 0 | 0 | 0 | ADR/WBS 歷史敘述（CAD-19） |
| `kanban.md` | 0（僅 tests docstring 提及） | — | 0 | 0 | 未追蹤工作清單，內容已全數落地 |

## Decision

1. **移除四個 `skills/` submodule 與 `.gitmodules`**：本 repo 的執行邏輯已完全內化為 Python 管線；外部工具由框架層（`$FRAMEWORK_ROOT`）統一路由，不屬於本專案的建置或測試依賴。
2. **移除 repo 副本 `AGENTS.md`**：協議正本位於 `$FRAMEWORK_ROOT`；過期副本會誤導 AI session 與貢獻者。`config.yaml` 提示詞與文件改指向「工作流協議（12-Step Protocol）」的實作文件 `docs/ARCHITECTURE.md`。
3. **移除 `skill-lock.json` 與 `agentic-workflow.cdx.json`**：前者鎖定已移除的 skills；後者為可再生的 CycloneDX SBOM，未接入 CI。需要 SBOM 時以 `cyclonedx-py` 於 release 流程再生（記入 backlog，見 Consequences）。
4. **移除 `test_ruff_include`、`test_ruff_include_dir`、`test_ruff_whitelist`**：零引用的歷史實驗 fixture。
5. **停止追蹤 `coverage_report.txt`**：屬產生式產物，`.gitignore` 已涵蓋。
6. **`tasks/clean_architecture_scan.py` 移至 `scripts/clean_architecture_scan.py`**：所有 CLI 工具集中於 `scripts/`（高內聚），並納入 ruff/mypy 掃描範圍（`[tool.ruff].src` 已含 `scripts`）。`tasks/` 目錄移除。
7. **刪除 `kanban.md`**：逐條驗證其 Done/Reference 內容已全數反映於 `docs/workflow-state.md` WBS、ADR-STR-008/020/021/025/027/028/029/030/031、`docs/formal/`、`tests/` 與 `scripts/`。

## Consequences

- **正面**：根目錄由 20+ 項縮減至純建置/治理必需項；clone 不再需要 `--recursive`；新貢獻者不會誤把過期協議副本當正本。
- **中性**：NFR-002（子模組唯讀）與 NFR-003（AGENTS.md 向下相容）隨載體移除而終止適用，於 `docs/requirements.md` 標註 superseded by 本 ADR。TC-001 的子模組存在性斷言同步改寫。
- **風險**：若未來需要 repo 內建供應鏈證明，需重新導入 SBOM 生成（建議接入 CI release job）— 已登錄 DEBT-010。
