# Tech Debt Register — Unified Agentic Workflow System

> **Last Updated**: 2026-05-15T00:47+08:00
> **Total Active Items**: 1 (DEBT-005 deferred; DEBT-001~004 all resolved)
> **Sprint Allocation**: 20% capacity
> **維護 Skill**: `skills/workflow-skills/tech-debt-collect.md`, `skills/workflow-skills/tech-debt-framework.md`
> **追溯矩陣**: `docs/traceability-matrix.md` § DEBT → FR
> **RICE 排序**: 依 RICE 分數降序

---

## Active Debt

### DEBT-001: docs/ 下原始方法論檔案未標記為 Reference Only

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-001 |
| **狀態** | resolved |
| **來源** | 文件債 |
| **影響元件** | docs/phases/, docs/stages/, docs/governance/ |
| **優先等級** | P2 |
| **象限** | Fill In |
| **RICE Score** | 6.0 |
| **Reach** | 10 (框架文件範圍) |
| **Impact** | 1.0 (中 — 混淆但不阻塞) |
| **Confidence** | 0.6 |
| **Effort** | 1 person-day |
| **ADR 追溯** | ADR-GOV-022 |
| **FR 追溯** | FR-001, FR-002 |
| **對應 RISK** | RISK-003 (docs/ 與 skills/ 版本漂移) |
| **對應 LESSON** | LESSON-022 |
| **建立日期** | 2026-05-14T05:15+08:00 |
| **預計處理 Sprint** | Backlog |
| **解決日期** | 2026-05-14T08:36+08:00 |

**債務描述**：ADR-GOV-022 將 docs/ 中的執行方法論全數吸收至 skills/workflow-skills/ 後，docs/ 下的原始檔案（phases/、stages/、governance/ 目錄）未標記為「Reference Only — 執行邏輯已遷移至 skills/workflow-skills/」。這可能導致新 session 的 AI 誤讀過時的 docs/ 檔案而非 skills/ 中的最新版本，與 RISK-003 (版本漂移) 直接相關。

**解決措施**：2026-05-14 session 中，已為 16 個檔案（governance/5 + phases/5 + stages/6）全部加上 `⚠️ REFERENCE ONLY` 標記，指向對應 skill 檔案。

---

### DEBT-002: Adapter 層尚未實作

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-002 |
| **狀態** | resolved |
| **來源** | 架構債 (domain-first 策略性延後) |
| **影響元件** | `adapters/langgraph/`, `adapters/llm/`, `adapters/mcp/`, `adapters/persistence/` |
| **優先等級** | P1 |
| **象限** | Major Project |
| **RICE Score** | 6.75 (R=20, I=3.0, C=0.9, E=8) |
| **ADR 追溯** | ADR-STR-001 (Clean Architecture 分層) |
| **FR 追溯** | FR-001, FR-015, FR-018, FR-026~030 |
| **對應 RISK** | N/A |
| **對應 LESSON** | LESSON-035 |
| **建立日期** | 2026-05-14T19:45+08:00 |
| **預計處理 Sprint** | 下個 Session |
| **解決日期** | 2026-05-15T00:00+08:00 |

**債務描述**: LangGraph DAG 接線、OpenAI/Anthropic LLM adapters、GitKraken + SequentialThinking MCP gateway、LangGraph checkpoint persistence 均為空骨架。Domain 層 100% 完成，Adapter 層是下個開發周期的主要任務。

---

### DEBT-003: `repo_map_builder.py` 相對 import 邊界分支未覆蓋

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-003 |
| **狀態** | resolved |
| **來源** | 測試缺口 |
| **影響元件** | `ALG-006 repo_map_builder.py` (L98→96, L183-184) |
| **優先等級** | P3 |
| **象限** | Fill In |
| **RICE Score** | 0.9 (R=2, I=0.5, C=0.9, E=1) |
| **ADR 追溯** | ADR-STR-002 (確定型演算法) |
| **FR 追溯** | FR-018 (RepoMap build) |
| **對應 LESSON** | LESSON-037, LESSON-042, LESSON-043 |
| **建立日期** | 2026-05-14T19:45+08:00 |
| **預計處理 Sprint** | Resolved |
| **解決日期** | 2026-05-15T00:45+08:00 |

**債務描述**: Python stdlib `ast` 解析時的 OSError / 路徑邊界分支（`L98→96`, `L183-184`）已補足。覆蓋率達 99.04%，INV-024 精確性確認。

**解決措施**: 2026-05-15 — 在 `test_coverage_gap_fill.py::TestFinalCoverageGaps` 新增精確的 `patched_read` mock，透過 call-counter 控制第1次 read 觸發 OSError（symbol loop path），確認 `good.py` 符號仍正確提取。

---

### DEBT-004: Layer 2/3 安全審計尚未執行

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-004 |
| **狀態** | resolved |
| **來源** | 安全債 |
| **影響元件** | `hook_runner.py`, `markdown_writer.py`, `file_repository.py`, `sequential_adapter.py` |
| **優先等級** | P2 |
| **象限** | Major Project |
| **RICE Score** | 4.0 (R=5, I=3.0, C=0.8, E=3) |
| **ADR 追溯** | ADR-SEC-001 |
| **FR 追溯** | FR-030 (SkillFortify SBOM) |
| **對應 RISK** | N/A |
| **對應 LESSON** | LESSON-040 (SEC-001 test pattern) |
| **建立日期** | 2026-05-14T19:45+08:00 |
| **預計處理 Sprint** | Resolved |
| **解決日期** | 2026-05-15T00:00+08:00 |

**債務描述**: AgentShield (Layer 1-3) 和 SkillFortify 掃描已執行。發現並修正 SEC-001 (shell injection), SEC-002/003 (path traversal), SEC-004 (SSRF)。SBOM `agentic-workflow.cdx.json` 與 `skill-lock.json` 已產出。

---

### DEBT-005: SonarCloud CI 閘門尚未設定

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-005 |
| **狀態** | open |
| **來源** | 流程債 |
| **影響元件** | `.github/workflows/ci.yml` (尚不存在) |
| **優先等級** | P2 |
| **象限** | Quick Win |
| **RICE Score** | 9.0 (R=10, I=2.0, C=0.9, E=2) |
| **ADR 追溯** | N/A |
| **FR 追溯** | FR-004 (quality gate), FR-005 (SonarCloud) |
| **建立日期** | 2026-05-14T19:45+08:00 |
| **預計處理 Sprint** | Backlog |
| **解決日期** | N/A |

**債務描述**: `pytest --cov` 本地已通過 98.88%，但尚未設定 GitHub Actions 將結果送至 SonarCloud。需建立 `.github/workflows/ci.yml`。

---

### DEBT-001: docs/ 下原始方法論檔案未標記為 Reference Only — **RESOLVED**

> 解決於 2026-05-14。16 個檔案已標記 Reference Only。詳見 Active Debt 區段。

---

## 技術債登錄格式說明

每筆技術債使用以下格式：

```markdown
### DEBT-{NNN}: {標題}

| 欄位 | 值 |
|------|-----|
| **ID** | DEBT-{NNN} |
| **狀態** | open \| in-progress \| resolved \| cancelled |
| **來源** | 程式碼品質 \| 測試缺口 \| 架構債 \| 效能債 \| 安全債 \| 文件債 \| 流程債 |
| **影響元件** | {CLS-xxx \| 模組名} |
| **優先等級** | P0 \| P1 \| P2 \| P3 |
| **象限** | Quick Win \| Major Project \| Fill In \| Thankless Task |
| **RICE Score** | {score} |
| **Reach** | {1-100 — 受影響元件/使用者數} |
| **Impact** | {0.5 \| 1.0 \| 2.0 \| 3.0} |
| **Confidence** | {0.5-1.0} |
| **Effort** | {N} person-days |
| **ADR 追溯** | {ADR-xxx 或 N/A} |
| **FR 追溯** | {FR-xxx 列表} |
| **對應 RISK** | {RISK-xxx 或 N/A} |
| **對應 LESSON** | {LESSON-xxx 或 N/A} |
| **建立日期** | {ISO 8601} |
| **預計處理 Sprint** | {Sprint N \| Backlog \| 立即} |
| **解決日期** | {ISO 8601 或 N/A} |

**債務描述**：{詳細描述債務內容、形成原因、影響範圍、解決方向}
```

---

## 四象限分類說明

| 象限 | Impact | Effort | 策略 |
|------|--------|--------|------|
| Quick Win | HIGH (2.0+) | LOW (≤2天) | 立即處理（本 Sprint） |
| Major Project | HIGH (2.0+) | HIGH (>2天) | 排入 Sprint 計畫 |
| Fill In | LOW (<2.0) | LOW (≤2天) | 閒置時處理 |
| Thankless Task | LOW (<2.0) | HIGH (>2天) | 暫緩（每 3 Sprint 重評） |

## P0-P3 優先等級定義

| 等級 | 定義 | 處理時限 |
|------|------|---------|
| P0 | Critical — 阻斷功能/安全漏洞，不受容量限制 | 立即 |
| P1 | High — 顯著影響品質或效能 | 本 Sprint |
| P2 | Medium — 中等影響，有 workaround | 下個 Sprint |
| P3 | Low — 輕微，可延後 | Backlog |
