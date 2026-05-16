# Phase 10 Retrospective — Unified Agentic Workflow System

> **版本**: v0.1.0 Post-Release Retro
> **日期**: 2026-05-15T00:45+08:00
> **Pipeline ID**: pipe-langgraph-migration-v1
> **執行依據**: `skills/workflow-skills/phase-10-orchestration.md`
> **追溯**: BG-001~003 → FEA-001~012 → FR-001~033 → TC-001~012

---

## 1. 成果快照

| 指標 | 值 |
|------|----|
| 測試數量 | 221 tests (17 test files) |
| 覆蓋率 | 99.04% (line + branch) |
| 安全修正 | SEC-001~004 (OWASP Layer 1-3) |
| DEBT 解決 | DEBT-001~004 resolved, DEBT-005 deferred |
| 交付方式 | Branch push: `langgraph-coding` @ fc8b945 |
| 交付日期 | 2026-05-15T00:44+08:00 |

---

## 2. 成功模式 (What Went Well)

### 2.1 Hexagonal Architecture 讓測試與基礎設施完全解耦
Domain 層 (algorithms, models, services) 無任何外部依賴，221 個測試在純 unit 環境下全部通過，無需啟動 LangGraph、OpenAI API 或 Git 服務。

### 2.2 Design-by-Contract (icontract) 作為邊界守衛
`@icontract.require` / `@icontract.ensure` 在 CI 即時捕捉前提條件違規（如 token_budget=0, 非法 project_path），避免錯誤資料傳遞到 boundary 以外。

### 2.3 BDD-first 讓需求到測試路徑清晰
SC-001~012 的 Gherkin scenario 直接對應 `tests/test_*.feature` 步驟，使需求變更到測試失敗的路徑一目了然，無模糊地帶。

### 2.4 BATCH-CM 宣告讓多檔 session 可窮舉審計
每次多檔案修改前宣告 `BATCH-CM`，確保 Step 12.1 的窮舉列舉有依據，無遺漏。

### 2.5 安全左移 (Security Left-Shift) 實際有效
DEBT-004 觸發的 SEC-001~004 修正均在程式碼層而非配置層實施，且每個修正都有對應的迴歸測試，確保不迴歸。

---

## 3. 改善機會 (What Could Be Better)

### 3.1 覆蓋率測試設計需先確認 call 順序 (→ LESSON-042)
補 `repo_map_builder.py` L183-184 的 OSError 分支時，花了 3 次 iteration 才正確。根因：未先 debug 確認 symbol extraction 和 import graph 哪個先執行，憑程式碼閱讀做錯誤假設。

### 3.2 安全測試應驗證機制而非副作用字串 (→ LESSON-040)
`test_metachar_stripped_from_context` 第一版驗證 `"rm -rf" not in full_cmd`，但 `shell=False` 模式下 `rm -rf` 是 echo 的合法輸出（只是字串，不執行）。應改為驗證 `shell=False` + `isinstance(cmd, list)`。

### 3.3 路徑過濾條件需用 basename (→ LESSON-043)
`test_test_files_excluded` 使用 `"test_" in s.file_path`，但 `file_path` 是絕對路徑，中間目錄名稱可能意外包含 `test_`。應明確使用 `Path(s.file_path).name.startswith("test_")`。

### 3.4 PageRank 穩態需先計算理論值 (→ LESSON-041)
假設單節點 PageRank = 1.0，實際穩態為 `(1-d)/n = 0.15`。測試數值斷言前應先推算理論值。

---

## 4. 新教訓歸檔 (LESSON-040~044)

### LESSON-040: 安全機制測試驗證機制而非副作用字串
**根因**: shell=True 防護的本質是命令不被 shell 解釋，而非命令字串不含危險詞彙。
**守衛**: 安全相關測試的斷言對象應是執行機制（`shell=False`, `isinstance(args, list)`），而非輸出字串內容。
**觸發**: SEC-001 test_metachar_stripped_from_context 第一版失敗。
**SSOT**: `tests/test_security_fixes.py`

- **LESSON-074**: 在 CI 腳本中處理 Node.js 版本切換時，應優先檢查 `node` 指令是否可用，而非僅依賴 `nvm`。
- **LESSON-075**: Git Hook 模板應考慮指令參數化。目前 `install_hooks.py` 採硬編碼字串，若未來勾子邏輯變複雜，應考慮將指令清單化或從 `pyproject.toml` 讀取，以維持基礎設施程式碼的整潔與彈性。

### LESSON-041: PageRank 單節點穩態 = (1-damping)/n = 0.15，非 1.0
**根因**: 誤將初始值 1/n 當作穩態值。
**守衛**: 測試 PageRank 等數值演算法前先推算理論穩態，再寫斷言。
**觸發**: `TestPagerank.test_single_node_no_links` 第一版斷言 abs(result-1.0) < 0.01 失敗。
**SSOT**: `tests/test_repo_map_coverage.py`

### LESSON-042: 補 coverage branch 前先用 debug print 確認 call 順序
**根因**: `_build_import_graph` 在 L188 (symbol loop L180 之後執行)，憑程式碼閱讀誤判讀取順序。
**守衛**: 補 branch coverage 測試前，先用 `print` 或 call counter 驗證實際執行路徑，避免錯誤的 mock 設計。
**觸發**: `test_repo_map_build_oserror_on_second_read` 花費 3 次 iteration。
**SSOT**: `tests/test_coverage_gap_fill.py`

### LESSON-043: 路徑字串過濾必須用 basename，不得在全路徑做 substring 判斷
**根因**: `"test_" in s.file_path` 在 Windows 絕對路徑中匹配到目錄層級中的非目標部分。
**守衛**: 路徑過濾一律使用 `os.path.basename(path)` 或 `Path(path).name`，再做 `startswith`/`endswith`/`in` 判斷。
**觸發**: `test_test_files_excluded` 第一版誤判非 test_ 檔案為 test_ 檔案。
**SSOT**: `tests/test_repo_map_coverage.py`

### LESSON-044: 快速迭代專案使用 branch push 作為交付模型，tag 保留給 formal release
**根因**: 使用者確認 branch push 即交付，tag 僅於 formal GitHub Release 時使用。
**守衛**: 在專案初始 session 中確認交付模型（branch push vs tag vs GitHub Release），記錄至 workflow-state.md。
**觸發**: v0.1.0 交付時創建了不必要的 local tag。
**SSOT**: `docs/workflow-state.md`

---

## 5. 技術債狀態更新

| DEBT | 標題 | 舊狀態 | 新狀態 | 解決日期 |
|------|------|--------|--------|----------|
| DEBT-001 | docs/ Reference Only 標記 | resolved | resolved ✅ | 2026-05-14 |
| DEBT-002 | Adapter 層實作 | resolved | resolved ✅ | 2026-05-15 |
| DEBT-003 | repo_map_builder 邊界分支 | open | **resolved ✅** | 2026-05-15 |
| DEBT-004 | Layer 1-3 安全審計 | open | **resolved ✅** | 2026-05-15 |
| DEBT-005 | SonarCloud CI 閘門 | open | deferred (post v0.1.0) | — |

---

## 6. 風險審查結果

| RISK | 舊強度 | 新強度 | 狀態變更 | 理由 |
|------|--------|--------|----------|------|
| RISK-001 SonarCloud 外部帳號 | MEDIUM (6) | MEDIUM (6) | open | DEBT-005 deferred，風險仍存在 |
| RISK-002 ADR 膨脹 | MEDIUM (6) | LOW (4) | **→ closed** | ADR 數量穩定，traceability-matrix 統一管理有效 |
| RISK-003 docs/skills 漂移 | MEDIUM (9) | LOW (3) | **→ closed** | skills/ 已為唯一執行來源，Phase 10 完成，緩解確認 |
| RISK-004 CM bypass | HIGH (12) | MEDIUM (8) | open | Step 12 3 sessions 無 bypass，機率降為 2 |
| RISK-005 ADR 欄位省略 | MEDIUM (9) | MEDIUM (6) | open | micro-validation 已加入檢查，機率降為 2 |

---

## 7. 知識圖譜增量更新項目

本次開發週期新增/變更的主要元件：

```
agentic_workflow/
├── adapters/ [NEW]
│   ├── events/in_memory_bus.py     — InMemoryEventBus (CLS-018)
│   ├── langgraph/                  — WorkflowGraph + StateMapper (FEA-010)
│   ├── llm/llm_adapter.py          — LLMAdapter (CLS-019)
│   ├── mcp/                        — SeqThinking + GitKraken adapters
│   └── persistence/                — File* repositories + MarkdownDocumentIO
├── application/ports/ [NEW]        — 7 Port interfaces
└── domain/services/hook_runner.py  [PATCHED: SEC-001]

tests/
├── test_security_fixes.py [NEW]    — 18 SEC-001~004 regression tests
├── test_repo_map_coverage.py [NEW] — 26 ALG-006 branch tests
└── test_coverage_gap_fill.py [MOD] — +4 final gap tests
```

---

## 8. 追溯矩陣最終快照

> 完整矩陣見 `docs/traceability-matrix.md`

| 層級 | ID 範圍 | 數量 | 覆蓋率 |
|------|---------|------|--------|
| BG | BG-001~003 | 3 | 100% |
| FEA | FEA-001~012 | 12 | 100% |
| FR | FR-001~033 | 33 | 100% |
| NFR | NFR-001~012 | 12 | 100% |
| UC | UC-001~012 | 12 | 100% |
| SC | SC-001~012 | 12 | 100% |
| TC | TC-001~012 | 12 + 221 unit tests | 100% |
| ALG | ALG-001~008 | 8 | 100% |
| INV | INV-001~025 | 25 | 100% |
| ADR | ADR-STR/SEC/GOV | ~30 | 100% |

---

## 9. 工作流改善建議 (/evolve)

1. **CI 自動化** (DEBT-005): 建立 `.github/workflows/ci.yml` 在 PR 時自動執行 `pytest --cov` 並送 SonarCloud，消除 RISK-001
2. **Coverage badge**: 在 README.md 加入 coverage badge，可視化品質門
3. **Pre-commit hook**: 加入 `ruff` + `mypy` 作為本地左移守衛，在 commit 前捕捉型別和 lint 問題
4. **Integration test suite**: 建立 `tests/integration/` 目錄，覆蓋 LLM adapter 的真實 API call（需 mock server 或 vcr）

---

```

---

## [v0.1.1+] Phase 10 Retrospective — 零容忍警告治理週期

> **版本**: v0.1.1+ (ADR-GOV-026)
> **日期**: 2026-05-15T17:42+08:00
> **Pipeline ID**: pipe-langgraph-migration-v1 (continued)
> **主要工作**: OO 重構 + 100% coverage + 零容忍警告政策

### 1. 成果快照

| 指標 | 值 |
|------|-----|
| 測試數量 | 646 tests (100% coverage) |
| 覆蓋率 | 100.00% (statement + branch) |
| 警告 | 0 (ADR-GOV-026 enforced) |
| DEBT 解決 | DEBT-006 closed (.coverage tracking 移除) |
| 交付方式 | Branch push: `langgraph-coding` @ 70d5007 |
| 交付日期 | 2026-05-15T17:38+08:00 |

### 2. 成功模式

- **ALG-010 OO Mandate**: 全部演算法轉 class-based，stateful encapsulation 實現
- **Logic-Fix First (ADR-GOV-026)**: runpy 警告透過邏輯修正而非 filter 解決，根本治理
- **LangGraph gate 節點**: `node_warning_policy_gate` 將政策制度化在執行路徑上

### 3. 新教訓歸檔 (LESSON-045~049)

| LESSON | 根因 | 守衛 |
|--------|------|------|
| LESSON-045 | FILTERING_LOGIC_FLAW | `warning_policy_verifier.py` — 警告判定需用 message/category 雙重條件 |
| LESSON-046 | PROCESS_GAP | `.gitignore` 範本不完整 → 二進位進 git tracking |
| LESSON-047 | ARCHITECTURE_EROSION | `$FRAMEWORK_ROOT` 與 `{target_repo}` 在多層 submodule 結構中可能不同 |
| LESSON-048 | PROCESS_GAP | Phase 0 checklist 必須強制驗證 `.gitignore` 包含 `.coverage`/`.pytest_cache`/`.env` |
| LESSON-049 | ARCHITECTURE_EROSION | Step 0 讀取 skill 前需探測路徑，fallback 至 `$FRAMEWORK_ROOT` |

### 4. 風險重評

| RISK | 前強度 | 新強度 | 狀態 |
|------|--------|--------|------|
| RISK-004 Session CM bypass | MEDIUM (8) | **MEDIUM (6)** | open — 機率降 2×4→2×3 |

### 5. 工作流改善

1. **Phase 0 checklist 強化**: 加入 `.gitignore` 完整範本驗證（含 `.coverage`, `.pytest_cache`, `.env`）
2. **Skill 路徑雙重探測**: Step 0 先嘗試 `{target_repo}/skills/workflow-skills/`，空時 fallback 至 `$FRAMEWORK_ROOT`
3. **ALG-010 推廣**: 所有新演算法一律 class-based

### 6. Phase 10 完成宣告

```
Phase 10 Retro [v0.1.1+]: COMPLETE
LESSON: LESSON-045~049 歸檔
DEBT: 無新增；DEBT-005 仍 deferred
RISK: RISK-004 降評 MEDIUM(8)→MEDIUM(6)
Archive: 追溯矩陣已更新 (302 條，零孤兒)
Next Pipeline: 等待人類發起新功能需求 (Phase 2)
```
