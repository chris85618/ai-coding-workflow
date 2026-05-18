# Traceability Matrix — Unified Agentic Workflow System

**Generated**: 2026-05-13T21:31:00+08:00
**Last Validated**: Phase 11 Complete (Release v0.1.5 Finalized)
**Validation Status**: ✅ ALG-010 (OO Mandate), ADR-STR-020 (DDD), 100% Coverage reached; 343 條追溯紀錄，零孤兒

---

## 正向追溯矩陣

### BG → FEA

| BG | FEA | 連結 | 語意 |
|----|-----|------|------|
| BG-001 | FEA-001, FEA-009, FEA-010, FEA-011, FEA-029 | derives | ✅ |
| BG-002 | FEA-002, FEA-003 | derives | ✅ |
| BG-003 | FEA-005, FEA-010 | derives | ✅ |
| BG-004 | FEA-004, FEA-006, FEA-007, FEA-008 | derives | ✅ |
| BG-005 | FEA-025 | derives | ✅ (DDD Transition) |
| BG-006 | FEA-027, FEA-028 | derives | ✅ (Automation & Monitoring) |

### FEA → FR/NFR

| FEA | FR/NFR | 連結 | 語意 |
|-----|--------|------|------|
| FEA-001 | FR-001, FR-002, FR-003 | decomposes | ✅ |
| FEA-001 | NFR-002, NFR-003 | constrains | ✅ |
| FEA-002 | FR-004, FR-005, FR-006, FR-007 | decomposes | ✅ |
| FEA-002 | NFR-004 | constrains | ✅ |
| FEA-003 | FR-008, FR-009 | decomposes | ✅ |
| FEA-004 | FR-010, FR-011 | decomposes | ✅ |
| FEA-005 | FR-012, FR-013, FR-014-v2 | decomposes | ✅ (FR-014 superseded → v2: 自主收斂) |
| FEA-006 | FR-015, FR-035, FR-036 | decomposes | ✅ |
| FEA-007 | FR-016 | decomposes | ✅ |
| FEA-008 | FR-003, FR-017 | decomposes | ✅ |
| FEA-009 | FR-002, FR-018 | decomposes | ✅ |
| FEA-009 | NFR-001 | constrains | ✅ |
| FEA-010 | FR-019-v2, FR-020, FR-021-v2, FR-023 | decomposes | ✅ (FR-019/021 superseded → v2: DAG checkpoint) |
| FEA-010 | NFR-005, NFR-006 | constrains | ✅ |
| FEA-002, FEA-003 | FR-022 | decomposes | ✅ |
| FEA-002, FEA-003 | FR-024, FR-025 | decomposes | ✅ |
| FEA-011 | FR-001, FR-002, FR-003, FR-012, FR-013 | decomposes | ✅ |
| FEA-011 | NFR-002, NFR-003, NFR-007, NFR-008 | constrains | ✅ |
| FEA-011 | FR-026, FR-027, FR-028, FR-029, FR-030 | decomposes | ✅ |
| FEA-012 | NFR-009, NFR-010 | constrains | ✅ |
| FEA-013 | FR-033 | decomposes | ✅ |
| FEA-013 | NFR-011 | constrains | ✅ |
| FEA-011 | FR-034 | decomposes | ✅ (NEW: Token Limit Mechanism) |
| FEA-015 | FR-035, FR-036 | decomposes | ✅ (SonarCloud Adapter) |
| FEA-016 | FR-043 | decomposes | ✅ (MkDocs-Pyproject Sync) |
| FEA-019 | FR-043, FR-044 | decomposes | ✅ (Centralized Config SSOT) |
| FEA-020 | FR-043 | decomposes | ✅ (Project Documentation Restructuring) |
| FEA-021 | FR-045 | decomposes | ✅ (Mypy Config Hardening) |
| FEA-022 | FR-046 | decomposes | ✅ (Git Hook Ruff Format) |
| FEA-023 | FR-047, FR-048, FR-049 | decomposes | ✅ (Test Refactor & Quality Hardening) |
| FEA-024 | FR-050 | decomposes | ✅ (Granular Test Architecture) |
| FEA-025 | FR-051, FR-052, FR-053 | decomposes | ✅ (DDD Core Models) |
| FEA-026 | FR-054, FR-055, FR-056, FR-057, FR-058, FR-059, FR-060, FR-061, FR-062 | decomposes | ✅ (Clean Architecture Deep Alignment) |
| FEA-027 | FR-063 | decomposes | ✅ (Dependabot Integration) |
| FEA-028 | FR-064 | decomposes | ✅ (Visual Monitoring Badges) |
| FEA-029 | FR-065, FR-066, FR-067 | decomposes | ✅ (OpenAI-compatible Provider) |
| FEA-029 | NFR-012 | constrains | ✅ |

### FR → UC

| FR | UC | 連結 | 語意 |
|----|-----|------|------|
| FR-001 | UC-001 | StartPipelineUseCase | ✅ |
| FR-050 | UC-003 | One-Class-Per-File Test Architecture | ✅ |
| FR-002 | UC-001, UC-002 | StartPipelineUseCase | ✅ |
| FR-003 | UC-003 | RunIterationUseCase | ✅ |
| FR-004 | UC-002, UC-004 | realizes | ✅ |
| FR-005 | UC-004, UC-009 | realizes | ✅ |
| FR-006 | UC-004 | realizes | ✅ |
| FR-007 | UC-004 | realizes | ✅ |
| FR-008 | UC-005 | realizes | ✅ |
| FR-009 | UC-005 | realizes | ✅ |
| FR-010 | UC-008 | realizes | ✅ |
| FR-011 | UC-008 | realizes | ✅ |
| FR-012 | UC-003 | realizes | ✅ |
| FR-013 | UC-003 | realizes | ✅ |
| FR-016 | UC-006, UC-009 | realizes | ✅ |
| FR-017 | UC-002, UC-003 | realizes | ✅ |
| FR-018 | UC-001, UC-002 | realizes | ✅ |
| FR-019 | UC-001, UC-003, UC-010 | realizes | ✅ |
| FR-020 | UC-003 | realizes | ✅ |
| FR-021 | UC-010 | realizes | ✅ |
| FR-022 | UC-005, UC-011 | realizes | ✅ |
| FR-023 | UC-005 | realizes | ✅ |
| FR-024 | UC-004, UC-005 | realizes | ✅ |
| FR-025 | UC-004 | realizes | ✅ |
| FR-026 | UC-012 | realizes | ✅ |
| FR-027 | UC-003 | realizes | ✅ |
| FR-028 | UC-013 | realizes | ✅ |
| FR-029 | UC-003 | realizes | ✅ |
| FR-030 | UC-003 | realizes | ✅ |
| FR-031 | UC-014 | realizes | ✅ |
| FR-032 | UC-015 | realizes | ✅ |
| FR-033 | UC-004 | realizes | ✅ |
| FR-034 | UC-003 | realizes | ✅ |
| FR-040 | UC-001 | realizes | ✅ |
| FR-041 | UC-004 | realizes | ✅ |
| FR-042 | UC-003 | realizes | ✅ |
| FR-043 | UC-016 | realizes | ✅ |
| FR-045 | UC-003 | realizes | ✅ (Mypy CLI Flag Internalization) |
| FR-046 | UC-018 | realizes | ✅ (Pre-commit Ruff Format) |
| FR-065, FR-066, FR-067 | UC-019 | realizes | ✅ |

### Stakeholder → BG

| S | BG | 連結 | 語意 |
|---|-----|------|------|
| S-001 | BG-001, BG-002, BG-003, BG-004 | stakeholder-of | ✅ |
| S-002 | BG-001, BG-003 | stakeholder-of | ✅ |
| S-003 | BG-001 | stakeholder-of | ✅ |

### ADR 登記簿 & FR 追溯

> 原 `docs/adr/ADR-INDEX.md` 已合併至此。導航、分類、追溯統一管理。

| ADR | 標題 | 類別 | 狀態 | FR/NFR | 連結 |
|-----|------|------|------|--------|------|
| [ADR-SEC-005](adr/ADR-SEC-005.md) | 配置網關安全性與 Clean Architecture 存取限制 | SEC | Accepted | FR-032, NFR-004, NFR-011 | justifies |
| [ADR-STR-020](adr/ADR-STR-020.md) | 領域驅動設計 (DDD) 實施準則 | STR | Accepted | FR-051, FR-052, FR-053 | justifies |
| [ADR-STR-021](adr/ADR-STR-021.md) | Clean Architecture & DDD 深度對齊實施 | STR | Proposed | FR-054~060 | justifies |
| [ADR-STR-022](adr/ADR-STR-022.md) | Dependabot 依賴治理策略 | STR | Accepted | FR-063 | justifies |
| [ADR-STR-023](adr/ADR-STR-023.md) | 支援 OpenAI 相容 Provider 之配置策略 | STR | Proposed | FR-065, FR-066, FR-067 | justifies |
| [ADR-STR-024](adr/ADR-STR-024.md) | 消除 Stage 6 Invariants Verifier 內部對 frameworks 之外層動態導入以遵循依賴反轉原則 | STR | Proposed | FR-054~060 | justifies |

> 類別統計：STR=9, GOV=26, SEC=1, SCP=0, GATE=0, OPS=0, **合計=36**
| [ADR-GOV-001](adr/ADR-GOV-001.md) | Decision Unit 理論 + 資訊新穎性門檻 | GOV | Accepted | FR-001, NFR-001 | justifies |
| [ADR-GOV-002](adr/ADR-GOV-002.md) | ADR 治理框架 — 全決策記錄制度 | GOV | Accepted | FR-001, FR-002, FR-003, NFR-001, FR-022, FR-023 | justifies |
| [ADR-GOV-003](adr/ADR-GOV-003.md) | 格式驗證閘門 (Step 0) + 外來殘留掃描 | GOV | Accepted | FR-005, FR-007 | justifies |
| [ADR-GOV-004](adr/ADR-GOV-004.md) | UC↔CLS 覆蓋斷言強制化 | GOV | Accepted | FR-005, FR-017 | justifies |
| [ADR-GOV-005](adr/ADR-GOV-005.md) | TC 斷言設計指引 | GOV | Accepted | FR-016 | justifies |
| [ADR-GOV-006](adr/ADR-GOV-006.md) | 自動化計數驗證強制化 | GOV | Accepted | FR-005, FR-007 | justifies |
| [ADR-GOV-007](adr/ADR-GOV-007.md) | 跨檔案增量演化同步治理 | GOV | Accepted | FR-024 | justifies |
| [ADR-GOV-008](adr/ADR-GOV-008.md) | 全鏈影響追溯制度化 (FR-022/023/024/025) | GOV | Accepted | FR-022, FR-023, FR-024, FR-025 | justifies |
| [ADR-GOV-009](adr/ADR-GOV-009.md) | Skill 版本升級級聯協議 | GOV | Accepted | FR-024 | justifies |
| [ADR-GOV-010](adr/ADR-GOV-010.md) | Session-End Hook Precondition Gate | GOV | Accepted | FR-007 | justifies |
| [ADR-GOV-011](adr/ADR-GOV-011.md) | 全變更類型 RCA — 消除逃生門 | GOV | Accepted | FR-005, FR-006, FR-007 | justifies |
| [ADR-GOV-012](adr/ADR-GOV-012.md) | Session-Start Hard Gate | GOV | Accepted | FR-019 | justifies |
| [ADR-GOV-013](adr/ADR-GOV-013.md) | 全域搜尋協議 | GOV | Accepted | FR-005 | justifies |
| [ADR-GOV-014](adr/ADR-GOV-014.md) | 事實優先失敗報告 | GOV | Accepted | NFR-001 | justifies |
| [ADR-GOV-015](adr/ADR-GOV-015.md) | 顧問式風險緩解 | GOV | Accepted | NFR-001 | justifies |
| [ADR-GOV-016](adr/ADR-GOV-016.md) | 務實簡潔性 (Ockham's Razor) | GOV | Accepted | NFR-001, FR-014 | justifies |
| [ADR-GOV-017](adr/ADR-GOV-017.md) | LLM 原生與優雅降級 | GOV | Accepted | NFR-001, NFR-003 | justifies |
| [ADR-GOV-018](adr/ADR-GOV-018.md) | 雙軸意圖框架 (DAIF) | GOV | Accepted | FR-019 | justifies |
| [ADR-GOV-019](adr/ADR-GOV-019.md) | ADG + PAG 驗證增強 | GOV | Accepted | FR-005, FR-007 | justifies |
| [ADR-GOV-020](adr/ADR-GOV-020.md) | AGENTS.md 結構化步驟協議重塑 | GOV | Accepted | FR-001, FR-002, FR-003, FR-005, FR-019, NFR-001 | justifies |
| [ADR-GOV-021](adr/ADR-GOV-021.md) | 雙 Agent 迭代協議 — 設計決策記錄 | GOV | Accepted | FR-001, FR-005, FR-007, NFR-001 | justifies |
| [ADR-GOV-022](adr/ADR-GOV-022.md) | docs/ 執行邏輯吸收至 skills/ 實現 Skill 自足性 | GOV | Accepted | FR-001, FR-002, FR-003, FR-005, FR-019, FR-022, FR-023 | justifies |
| [ADR-GOV-023](adr/ADR-GOV-023.md) | Skill 追溯性擴充 + RCA 推論平準化 | GOV | Accepted | FR-004, FR-005, FR-007, FR-022, FR-023 | justifies |
| [ADR-GOV-024](adr/ADR-GOV-024.md) | 強制循序輸出協議 | GOV | Accepted | FR-001, FR-005, FR-019 | justifies |
| [ADR-GOV-027](adr/ADR-GOV-027.md) | 以 pyproject.toml 為全域配置唯一事實來源 | GOV | Accepted | FR-043, FR-044 | justifies |
| [ADR-GOV-025](adr/ADR-GOV-025.md) | ISO 31000 風險管理框架 + DEBT/RISK 完整追溯制度 | GOV | Accepted | FR-010, FR-011, FR-022, FR-023 | justifies |
| [ADR-GOV-026](adr/ADR-GOV-026.md) | 零容忍警告政策與嚴格 Scope 制度 (Logic-Fix First) | GOV | Accepted | NFR-001, FR-004, FR-005, FR-033 | justifies |
| [ADR-STR-001](adr/ADR-STR-001.md) | 模組化架構 — 每個 Class 獨立檔案原則 | STR | Accepted | NFR-002, NFR-003 | justifies |
| [ADR-STR-002](adr/ADR-STR-002.md) | Clean Architecture for LangGraph Migration | STR | Accepted | FR-001, FR-002, FR-003 | justifies |
| [ADR-STR-003](adr/ADR-STR-003.md) | 自主執行模型 (No HITL Gates) | STR | Accepted | FR-012, FR-013, FR-014-v2, FR-019-v2, FR-021-v2 | justifies |
| [ADR-STR-004](adr/ADR-STR-004.md) | AI Tool Feature Absorption — Strategy Pattern + Hooks + RepoMap | STR | Accepted | FR-026, FR-027, FR-028, FR-029, FR-030, NFR-008 | justifies |
| [ADR-STR-005](adr/ADR-STR-005.md) | Markdown ↔ JSON 雙向轉換策略 | STR | Accepted | FR-031, NFR-009 | justifies |
| [ADR-STR-006](adr/ADR-STR-006.md) | 外部化 YAML 配置 (Models & Prompts Only) | STR | Amended | FR-032, NFR-010 | justifies |
| [ADR-STR-007](adr/ADR-STR-007.md) | 單一建圖路徑 — OO Builder 為唯一合法建圖機制 | STR | Accepted | NFR-003, RISK-004 | justifies |
| [ADR-STR-008](adr/ADR-STR-008.md) | Token Budget & Long Response Continuation Mechanism | STR | Accepted | FR-034 | justifies |
| [ADR-STR-009](adr/ADR-STR-009.md) | Ruff Line-Length = 120 (禁止 noqa 抑制) | STR | Accepted | NFR-002, NFR-003 | justifies |
| [ADR-OPS-001](adr/ADR-OPS-001.md) | SonarCloud 閉環回饋與降級機制 | OPS | Accepted | FR-015, FR-035, FR-036 | justifies |
| [ADR-STR-015](adr/ADR-STR-015.md) | 導入 pyproject-mkdocs-plugin 實施單一事實來源 | STR | Accepted | FR-043 | justifies |
| [ADR-STR-016](adr/ADR-STR-016.md) | 巨集驅動的配置與元資料同步 | STR | Accepted | FEA-017, FR-044 | justifies |
| [ADR-STR-017](adr/ADR-STR-017.md) | 配置與文件巨集的生命週期隔離 | STR | Accepted | FEA-018, FR-044 | justifies |
| [ADR-STR-019](adr/ADR-STR-019.md) | Mypy 常用執行參數固化 | STR | Accepted | FEA-021, FR-045 | justifies |
| [ADR-STR-027](adr/ADR-STR-027.md) | 架構邊界防護與註解封鎖硬化 | STR | Accepted | FR-054~060 | justifies |
| [ADR-GOV-028](adr/ADR-GOV-028.md) | 專案文件入口規範與 README 重構 | GOV | Accepted | FEA-020, FR-043 | justifies |
| [ADR-GOV-029](adr/ADR-GOV-029.md) | Git Pre-commit Hook 整合 Ruff 格式化 | GOV | Accepted | FEA-022, FR-046 | justifies |

> 類別統計：STR=13, GOV=27, SEC=1, SCP=0, GATE=0, OPS=1, **合計=42**

### ALG → FR

| ALG | FR | 連結 | 語意 |
|-----|-----|------|------|
| ALG-001 | FR-012, FR-013 | implements | ✅ (v2: auto-gate, no HITL) |
| ALG-002 | FR-005, FR-006, FR-007 | implements | ✅ |
| ALG-003 | FR-008, FR-009 | implements | ✅ |
| ALG-004 | FR-010, FR-011 | implements | ✅ |
| ALG-005 | FR-005 | implements | ✅ |
| ALG-006 | FR-001, FR-026, FEA-011 | implements | ✅ (RepoMap tree-sitter + PageRank) |
| ALG-007 | FR-030, FEA-011 | implements | ✅ (ContextBudgetAllocator) |
| ALG-008 | FR-029, FEA-011 | implements | ✅ (NEW: ModelSelector Strategy Pattern) |
| ALG-009 | FR-031, FEA-012 | implements | ✅ (NEW: Markdown Parser) |
| ALG-010 | FR-002, NFR-002 | implements | ✅ (NEW: Stage 8 TDD骨架優先協議; test coverage 95.66%) |
| ALG-013 | FR-033, FEA-013 | implements | ✅ (NEW: WarningPolicyVerifier) |

### RISK → FEA (ISO 31000 完整屬性)

| RISK | 標題 | 狀態 | 機率 | 影響 | 強度 | 策略 | FEA | 對應LESSON | 對應ADR | 連結 |
|------|------|------|------|------|------|------|-----|-----------|---------|------|
| RISK-001 | SonarCloud依賴外部服務帳號 | resolved | 2 | 3 | 6(MEDIUM) | MT | FEA-006 | LESSON-073,074 | ADR-OPS-001 | mitigates |
| RISK-002 | ADR數量膨脹導致管理困難 | closed | 3 | 2 | 6(MEDIUM) | MT | FEA-009 | N/A | ADR-GOV-002 | mitigates |
| RISK-003 | docs/與skills/版本漂移 | closed | 3 | 3 | 9(MEDIUM) | MT | FEA-001,009 | LESSON-022 | ADR-GOV-022 | mitigates |
| RISK-004 | Session結束前未執行完整CM協議 | open | 2 | 4 | 8(MEDIUM) | MT | FEA-006 | LESSON-009,011,030 | ADR-GOV-010,011 | mitigates |
| RISK-005 | ADR-TEMPLATE欄位過長導致LLM省略 | open | 2 | 3 | 6(MEDIUM) | MT | FEA-006,007 | LESSON-029 | ADR-GOV-025 | mitigates |

> **未應對風險計數公式**：status=`open` AND 強度>=MEDIUM 的 RISK-xxx 數量。當前值 = **3**

### DEBT → FR

| DEBT | 標題 | 狀態 | 來源 | 優先 | RICE | 象限 | FR 追溯 | 對應RISK | 對應LESSON | 連結 |
|------|------|------|------|------|------|------|---------|---------|-----------|------|
| DEBT-001 | docs/下原始方法論檔案未標記為Reference Only | resolved | 文件債 | P2 | 6.0 | Fill In | FR-001,002 | RISK-003 | LESSON-022 | derives |
| DEBT-002 | Adapter 層尚未實作 | resolved | 架構債 | P1 | 6.75 | Major Project | FR-001,015,018,026~030 | N/A | LESSON-035 | derives |
| DEBT-003 | repo_map_builder.py 相對 import 邊界分支未覆蓋 | resolved | 測試缺口 | P3 | 0.9 | Fill In | FR-018 | N/A | LESSON-037 | derives |
| DEBT-004 | Layer 2/3 安全審計尚未執行 | resolved | 安全債 | P2 | 4.0 | Major Project | FR-030 | N/A | N/A | derives |
| DEBT-005 | SonarCloud CI 閘門尚未設定 | in-progress | 流程債 | P2 | 9.0 | Quick Win | FR-004,005 | N/A | N/A | derives |
| DEBT-006 | SonarCloudGate.evaluate 認知複雜度過高 | resolved | 程式碼品質 | P2 | 9.0 | Quick Win | ADR-STR-017 | 設定中心化 SSOT 策略 | FR-042 | [LESSON-023](docs/lessons.md) |
| ADR-STR-018 | 強制 Git Hook 整合 Ruff Format | FR-044 | - |
| DEBT-007 | `os.environ` 依賴清理 | resolved | 安全債 | P1 | 12.0 | Quick Win | FR-032 | RISK-005 | LESSON-071,072 | derives |
| DEBT-008 | SonarCloud 切換邏輯異步化 | open | 效能債 | P3 | 2.0 | Fill In | FR-015 | N/A | LESSON-073 | derives |

### CLS → UC / ALG

| CLS | 追溯至 | 連結 | 語意 |
|-----|--------|------|------|
| CLS-001 | Pipeline | domain/aggregates/pipeline.py | ✅ (Aggregate Root) |
| CLS-002 | Stage | domain/entities/stage.py | ✅ (Entity) |
| CLS-003 | RunIterationUseCase | application/use_cases/run_iteration.py | ✅ |
| CLS-004 | TraceableID | domain/entities/traceable_id.py | ✅ (Entity) |
| CLS-005 | TraceLink | domain/value_objects/trace_link.py | ✅ (Value Object) |
| CLS-006 | ALG-002, UC-004 | implements, models | ✅ |
| CLS-007 | ALG-003, UC-005 | implements, models | ✅ |
| CLS-008 | UC-007 | models | ✅ |
| CLS-009 | UC-008 | models | ✅ |
| CLS-010 | UC-006 | models | ✅ |
| CLS-011 | UC-009 | models | ✅ |
| CLS-012 | UC-002 | models | ✅ |
| CLS-013 | UC-010 | models | ✅ (v2: checkpoint-based) |
| CLS-014 | UC-011 | models | ✅ |
| CLS-015 | RepoMap | domain/value_objects/repo_map.py | ✅ (Value Object) |
| CLS-016 | FEA-011, UC-013 | models | ✅ (HookRunner, from Claude Code) |
| CLS-017 | FEA-011, UC-003, FR-029 | models | ✅ (NEW: LLMStrategySelector) |
| CLS-018 | CLS-017 | models | ✅ (NEW: ModelConfig VO) |
| CLS-019 | UC-014, FR-031 | models | ✅ (NEW: Markdown Parser) |
| CLS-020 | UC-015, FR-032 | models | ✅ (NEW: YAML Configurator) |
| CLS-021 | FR-034 | models | ✅ (NEW: TokenLimitExceededError) |
| CLS-022 | SymbolDef | domain/value_objects/symbol_def.py | ✅ (Value Object) |
| CLS-023 | Findings | domain/value_objects/findings.py | ✅ (Value Object) |
| CLS-024 | DependencyContainer | frameworks/dependency_container.py | ✅ (DI Container) |
| CLS-025 | TraceableIdVO | domain/value_objects/traceable_id_vo.py | ✅ (Value Object) |
| CLS-026 | IPipelineRepository | application/ports/repositories/pipeline_repository.py | ✅ (Port) |
| CLS-027 | IAgentReasoner | application/ports/gateways/agent_reasoner.py | ✅ (Port) |

### EVT → CLS

| EVT | 追溯至 | 連結 | 語意 |
|-----|--------|------|------|
| EVT-001 | CLS-001, CLS-002 | emitted-by | ✅ |
| EVT-002 | CLS-006 | emitted-by | ✅ |
| EVT-003 | CLS-007 | emitted-by | ✅ |
| EVT-004 | CLS-009 | emitted-by | ✅ |
| EVT-005 | CLS-010 | emitted-by | ✅ |
| EVT-006 | CLS-013 | emitted-by | ✅ (v2: CheckpointResumed) |
| EVT-007 | CLS-014 | emitted-by | ✅ |
| EVT-008 | CLS-016 | emitted-by | ✅ (HookExecuted) |
| EVT-009 | MCPGateway | emitted-by | ✅ (NEW: GitCommitCreated) |
| EVT-010 | CLS-017 | emitted-by | ✅ (NEW: ModelSelected) |

### INV → CLS / ALG

| INV | 追溯至 | 連結 | 語意 |
|-----|--------|------|------|
| INV-001 | CLS-001 | formalizes | ✅ |
| INV-002-v2 | CLS-001 | formalizes | ✅ (supersedes INV-002: auto-gate required) |
| INV-003 | CLS-002 | formalizes | ✅ |
| INV-004 | CLS-003, ALG-001 | formalizes | ✅ |
| INV-005-v2 | CLS-003 | formalizes | ✅ (supersedes INV-005: step M before auto-gate) |
| INV-006 | CLS-004 | formalizes | ✅ |
| INV-007 | CLS-004 | formalizes | ✅ |
| INV-008 | CLS-005 | formalizes | ✅ |
| INV-009 | CLS-005 | formalizes | ✅ |
| INV-010 | CLS-006, ALG-002 | formalizes | ✅ |
| INV-011 | CLS-006, ALG-002 | formalizes | ✅ |
| INV-012 | CLS-007, ALG-003 | formalizes | ✅ |
| INV-013 | CLS-007 | formalizes | ✅ |
| INV-014 | CLS-008, CLS-010 | formalizes | ✅ |
| INV-015 | CLS-009, ALG-004 | formalizes | ✅ |
| INV-016 | CLS-011 | formalizes | ✅ |
| INV-017 | CLS-012 | formalizes | ✅ |
| INV-018 | CLS-013 | formalizes | ✅ |
| INV-019 | CLS-014 | formalizes | ✅ |
| INV-020 | CLS-016 | formalizes | ✅ (NEW: Hook exit code contract) |
| INV-021 | ALG-007 | formalizes | ✅ (Token budget never exceeded) |
| INV-022 | CLS-017 | formalizes | ✅ (NEW: Strategy provider constraint) |
| INV-023 | MCPGateway | formalizes | ✅ (NEW: Atomic commit completeness) |
| INV-024 | ALG-006 | formalizes | ✅ (NEW: RepoMap budget constraint) |
| INV-025 | CLS-021 | formalizes | ✅ (NEW: Token Bound Continuation Safety) |

### SC → UC / INV

| SC | 追溯至 UC | 驗證 INV | 連結 | 語意 |
|----|----------|---------|------|------|
| SC-001 | UC-001 | INV-001, INV-002-v2 | covers, verifies | ✅ (v2: autonomous) |
| SC-002 | UC-002 | INV-017 | covers, verifies | ✅ |
| SC-003 | UC-003 | INV-003, INV-004, INV-005-v2 | covers, verifies | ✅ (v2: autonomous convergence) |
| SC-004 | UC-004 | INV-006..INV-011 | covers, verifies | ✅ |
| SC-005 | UC-005 | INV-012, INV-013 | covers, verifies | ✅ |
| SC-006 | UC-006 | INV-014 | covers, verifies | ✅ |
| SC-007 | UC-007 | INV-014 | covers, verifies | ✅ |
| SC-008 | UC-008 | INV-015 | covers, verifies | ✅ |
| SC-009 | UC-009 | INV-016 | covers, verifies | ✅ |
| SC-010 | UC-010 | INV-001, INV-018 | covers, verifies | ✅ |
| SC-011 | UC-011 | INV-009, INV-019 | covers, verifies | ✅ |
| SC-021 | UC-019 | INV-022 | covers, verifies | ✅ (NEW: FEA-029) |
| SC-012 | UC-012 | INV-024 | covers, verifies | ✅ (NEW: RepoMap) |
| SC-013 | UC-013 | INV-020 | covers, verifies | ✅ (NEW: Hook execution) |
| SC-014 | UC-003 | INV-022 | covers, verifies | ✅ (NEW: Strategy LLM) |
| SC-015 | UC-003 | INV-023 | covers, verifies | ✅ (NEW: Atomic git) |
| SC-016 | UC-003 | INV-021 | covers, verifies | ✅ (NEW: Context budget) |
| SC-017 | UC-014 | INV-001 | covers, verifies | ✅ (NEW: MD-JSON Parser) |
| SC-018 | UC-015 | INV-001 | covers, verifies | ✅ (NEW: YAML Config) |
| SC-019 | UC-001 | INV-001, INV-002-v2, INV-003 | covers, verifies | ✅ (NEW: LangGraph DAG & Invariants) |
| SC-020 | UC-003 | INV-025 | covers, verifies | ✅ (NEW: Auto-continuation bounding) |

### TC → SC

| TC | 追溯至 SC | 連結 | 語意 |
|----|----------|------|------|
| TC-SONAR-001 | 驗證 SonarCloud 閘門邏輯 | FR-015 | SonarCloudGate | ✅ |
| TC-SONAR-002 | 驗證 SonarCloudConfig 缺失參數報告 | FR-032 | SonarCloudConfig | ✅ |
| TC-SONAR-003 | 驗證 SonarCloudConfig 完整參數檢核 | FR-032 | SonarCloudConfig | ✅ |
| TC-SONAR-004 | 驗證 SonarCloud 節點切換邏輯 (Mocked) | FR-015, FR-035, ADR-OPS-001 | node_sonarcloud_gate | ✅ |
| TC-001 | SC-001 | validates | ✅ |
| TC-016 | SC-021 | validates | ✅ (Granular Test Set Verification) |
| TC-017 | SC-019 | validates | ✅ (Step 0 & 1 validation failure and node branch coverage) |
| TC-002 | SC-002 | validates | ✅ |
| TC-003 | SC-003 | validates | ✅ |
| TC-004 | SC-004 | validates | ✅ |
| TC-005 | SC-005 | validates | ✅ |
| TC-006 | SC-006 | validates | ✅ |
| TC-007 | SC-007 | validates | ✅ |
| TC-008 | SC-008 | validates | ✅ |
| TC-009 | SC-009 | validates | ✅ |
| TC-010 | SC-010 | validates | ✅ |
| TC-011 | SC-011 | validates | ✅ |
| TC-012 | SC-017 | validates | ✅ |
| TC-013 | SC-018 | validates | ✅ |
| TC-014 | SC-019 | validates | ✅ |
| TC-015 | SC-020 | validates | ✅ |
| TC-LLM-021 | SC-021 | validates | ✅ (FEA-029: Custom OpenAI Endpoint) |
| TC-UC-001 | UC-001 | validates | ✅ (NEW: StartPipelineUseCase) |
| TC-UC-002 | UC-001, UC-003 | validates | ✅ (NEW: AdvancePipelineUseCase) |
| TC-UC-003 | UC-003 | validates | ✅ (NEW: RunIterationUseCase) |
| TC-CAD-001 | DependencyContainer wiring validation | validates | ✅ |
| TC-CAD-002 | AdvancePipelineUseCase execution validation | validates | ✅ |
| TC-COV-001 | FR-019-v2 | validates | ✅ (NEW: StateMapper edge cases) |
| TC-COV-002 | FR-051 | validates | ✅ (NEW: Pipeline error paths) |
| TC-QUALITY-001 | 驗證 Ruff 靜態語法檢查 0 警告不退化 | FR-QUALITY-001 | validates | ✅ (NEW: Pytest Ruff Check) |
| TC-QUALITY-002 | 驗證 Mypy 類型安全檢查 0 錯誤不退化 | FR-QUALITY-002 | validates | ✅ (NEW: Pytest Mypy Check) |
| TC-QUALITY-003 | 驗證 DEBT-009 自動化 AST 檢查 100% 阻斷 concrete ellipsis | FR-QUALITY-002 | validates | ✅ (NEW: AST Ellipsis Check) |
| TC-QUALITY-004 | 驗證任一 framework code 的 Cyclomatic Complexity 必須 <= 2 | FR-QUALITY-003 | validates | ✅ (NEW: AST Complexity Check) |
| TC-QUALITY-005 | 驗證任一 framework code 的函式 NLOC 排除空行/註解/docstring 後必須 <= 6 | FR-QUALITY-004 | validates | ✅ (NEW: AST NLOC Check) |
| TC-QUALITY-006 | 驗證任一 framework code 的巢狀深度必須 <= 1 | FR-QUALITY-005 | validates | ✅ (NEW: AST Nesting Depth Check) |
| TC-QUALITY-007 | 驗證任一 framework code 的 branch 數必須 <= 1 | FR-QUALITY-006 | validates | ✅ (NEW: AST Branch Count Check) |
| TC-QUALITY-008 | 驗證任一 framework code 的 ast.Return 節點數須 <= 1 | FR-QUALITY-007 | validates | ✅ (NEW: AST Return Count Check) |
| TC-QUALITY-009 | 驗證任一 framework code 中的類別都必須繼承自內層的抽象 | FR-QUALITY-008 | validates | ✅ (NEW: AST Inheritance Check) |
| TC-QUALITY-010 | 驗證任一 framework code 的方法都必須覆寫內層抽象的方法 | FR-QUALITY-009 | validates | ✅ (NEW: AST Override Check) |
| TC-QUALITY-011 | 驗證任一 framework code 中禁止存在任何模組層級的 function 或 async function 定義 | FR-QUALITY-010 | validates | ✅ (NEW: AST Module Level Check) |


### FR → Skill 實作映射

| FR | 實作 Skill | 連結 |
|----|-----------|------|
| FR-001 | `pipeline_completeness.py`, `AGENTS.md` (Step 0-12) | implemented-by |
| FR-002 | `orchestrator.py` | implemented-by |
| FR-003 | `iter_loop.py`, `orchestrator.py` | implemented-by |
| FR-004 | `traceability_validator.py` | implemented-by |
| FR-005 | `micro_validation.py`, `traceability_validator.py` | implemented-by |
| FR-006 | `micro_validation.py` (Step 4) | implemented-by |
| FR-007 | `micro_validation.py`, `root_cause_leftshift.py` | implemented-by |
| FR-008 | `impact_analysis.py` | implemented-by |
| FR-009 | `impact_analysis.py`, `adr_governance.py` | implemented-by |
| FR-010 | `tech_debt_manager.py`, `risk_manager.py` | implemented-by |
| FR-011 | `tech_debt_manager.py`, `risk_manager.py` | implemented-by |
| FR-012 | `iter_loop.py` | implemented-by |
| FR-013 | `iter_loop.py` (determine_convergence) | implemented-by |
| FR-014 | `iter_loop.py` (HITL section) | implemented-by |
| FR-015 | `sonarcloud_gate.py`, `nodes.py` (node_sonarcloud_gate) | implemented-by |
| FR-035 | `sonarcloud_gate.py`, `nodes.py` (node_sonarcloud_gate) | implemented-by |
| FR-036 | `sonarcloud_gate.py`, `nodes.py` (node_sonarcloud_gate) | implemented-by |
| FR-016 | `security_audit.py` | implemented-by |
| FR-017 | `orchestrator.py` | implemented-by |
| FR-018 | `orchestrator.py` | implemented-by |
| FR-019 | `workflow_resume.py`, `AGENTS.md` (Step 0) | implemented-by |
| FR-020 | `iter_loop.py` | implemented-by |
| FR-021 | `workflow_resume.py` | implemented-by |
| FR-022 | `impact_analysis.py`, `micro_validation.py` (Step 5.5) | implemented-by |
| FR-023 | `root_cause_leftshift.py` (Step 1.5/3c), `micro_validation.py` (Step 5.7) | implemented-by |
| FR-024 | `change_management.py`, `micro_validation.py` | implemented-by |
| FR-025 | `change_management.py` (PGVG) | implemented-by |
| FR-033 | `warning_policy_verifier.py`, `nodes.py` (node_warning_policy_gate) | implemented-by |
| FR-034 | `llm_adapter.py` (LangChainLLMAdapter.complete) | implemented-by |

### LESSON → Skill 守衛映射

| LESSON | 根因分類 | 守衛所在 Skill | ADR 來源 | 連結 |
|--------|---------|---------------|----------|------|
| LESSON-001 | FORMAT_ERROR | `micro_validation.py` (Step 0) | ADR-GOV-003 | guards |
| LESSON-002 | COVERAGE_GAP | `micro_validation.py` (Step 4), `orchestrator.py`, `completion_check.py` | ADR-GOV-004 | guards |
| LESSON-003 | LLM_HALLUCINATION | `orchestrator.py` | ADR-GOV-005 | guards |
| LESSON-004 | PROCESS_GAP | `micro_validation.py` (Step 0) | ADR-GOV-003 | guards |
| LESSON-005 | LLM_HALLUCINATION | `micro_validation.py` (Step 1), `completion_check.py` | ADR-GOV-006 | guards |
| LESSON-006 | PROCESS_GAP | `micro_validation.py` (Step 5.5), `change_management.py` (Step 5) | ADR-GOV-007 | guards |
| LESSON-007 | DECLARATION_IMPLEMENTATION_GAP | `change_management.py` (Step 2f/5), `micro_validation.py` (Step 5.5/5.7) | ADR-GOV-008 | guards |
| LESSON-008 | PROCESS_GAP | `orchestrator.py` | ADR-GOV-009 | guards |
| LESSON-009 | PROCESS_GAP | `change_management.py` (Precondition Gate) | ADR-GOV-010 | guards |
| LESSON-010 | GOVERNANCE_BYPASS | `root_cause_leftshift.py` (觸發條件) | ADR-GOV-011 | guards |
| LESSON-011 | GOVERNANCE_BYPASS | `AGENTS.md` (Step 0 Hard Gate) | ADR-GOV-012 | guards |
| LESSON-012 | SCAN_INCOMPLETENESS | `exhaustive_search.py` | ADR-GOV-013 | guards |
| LESSON-013 | DECLARATION_IMPLEMENTATION_GAP | `change_management.py` (ADR 變更紀錄區段) | ADR-GOV-008 | guards |
| LESSON-014 | IMPROVEMENT | 16 個 `workflow-skills/*.md` (Step N 格式) | ADR-GOV-016 | guards |
| LESSON-020 | ARCHITECTURE_EROSION | `AGENTS.md` (Principle #13) | ADR-GOV-020 | guards |
| LESSON-022 | ARCHITECTURE_EROSION | `AGENTS.md` (Scope Rules) | ADR-GOV-022 | guards |
| LESSON-023 | GOVERNANCE_BYPASS | `change_management.py` (Inline CM-GATE), `AGENTS.md` (#14) | ADR-GOV-022 | guards |
| LESSON-024 | PROCESS_GAP | `change_management.py` (CM-GATE 宣告) | ADR-GOV-022 | guards |
| LESSON-025 | DECLARATION_IMPLEMENTATION_GAP | `root_cause_leftshift.py` (Meta-RCA) | ADR-GOV-022 | guards |
| LESSON-026 | DECLARATION_IMPLEMENTATION_GAP | `micro_validation.py` (Step 7.6) | ADR-GOV-022 | guards |
| LESSON-027 | ARCHITECTURE_EROSION | `impact_analysis.py` | — (ADR-INDEX 合併) | guards |
| LESSON-028 | GOVERNANCE_BYPASS | `AGENTS.md` (#15 + Step 輸出協議) | ADR-GOV-024 | guards |
| LESSON-029 | PROCESS_GAP | `risk_manager.py` (Step 5), `tech_debt_manager.py` (Step 5), `ADR-TEMPLATE.md` (關聯產出物) | ADR-GOV-025 | guards |
| LESSON-030 | SCAN_INCOMPLETENESS | `risk_manager.py` (Step 1 SSOT), `tech_debt_manager.py` (Step 1 SSOT), `exhaustive_search.py` | ADR-GOV-025 (追加) | guards |
| LESSON-031 | ARCHITECTURE_EROSION | `traceability_validator.py` (Step 0 通用 ID 指派協議), `root_cause_leftshift.py` (Step 7 LESSON ID 守衞) | ADR-GOV-025 (追加) | guards |
| LESSON-032 | GOVERNANCE_BYPASS | `AGENTS.md` (Step 12.2 Pipeline Position 客觀判定守衛) | ADR-GOV-025 (追加) | guards |
| LESSON-033 | GOVERNANCE_BYPASS | `AGENTS.md` (Step 輸出協議 — 每個 prompt = 完整協議觸發) | ADR-GOV-025 (追加) | guards |
| LESSON-034 | ASSUMPTION_OVERRIDE | `AGENTS.md` (Factual Reporting — 範圍限定詞保護) | ADR-GOV-025 (追加) | guards |
| LESSON-040 | SECURITY_TESTING_FLAW | `orchestrator.py` (Step 4) | - | guards |
| LESSON-041 | ALGORITHM_TESTING_FLAW | `orchestrator.py` (Step 4) | - | guards |
| LESSON-042 | COVERAGE_GAP | `orchestrator.py` (Step 4) | - | guards |
| LESSON-043 | FILTERING_LOGIC_FLAW | `orchestrator.py` (Step 4) | - | guards |
| LESSON-044 | DELIVERY_MODEL_DRIFT | `orchestrator.py` (Step 2) | - | guards |
| LESSON-045 | FILTERING_LOGIC_FLAW | `warning_policy_verifier.py`, `graph.py` (s8_warning) | ADR-GOV-026 | guards |
| LESSON-046 | PROCESS_GAP | `.gitignore`, `mcp_GitKraken_git_push` | - | guards |
| LESSON-047 | ARCHITECTURE_EROSION | `AGENTS.md` (Scope Rules - Parent Repo Awareness) | - | guards |
| LESSON-048 | PROCESS_GAP | `phase-0-orchestration.md` (gitignore checklist) | - | guards |
| LESSON-049 | ARCHITECTURE_EROSION | `AGENTS.md` (Step 0 skill path fallback) | - | guards |
| LESSON-050 | ARCHITECTURE_EROSION | `frameworks/graph.py` (OO Builder 為唯一建圖路徑), `docs/adr/ADR-STR-007.md` | ADR-STR-007 | guards |
| LESSON-051 | GOVERNANCE_BYPASS | `AGENTS.md` (Step 4-8 cannot be bypassed for structural features) | - | guards |
| LESSON-052 | PROCESS_GAP | `phase-0-orchestration.md` (Step 2.5) | - | guards |
| LESSON-060 | LOGIC_FLAW | `pipeline_completeness.py` | - | guards |
| LESSON-061 | LOGIC_FLAW | `micro_validation.py` | - | guards |
| LESSON-062 | PROCESS_GAP | `convergence.py` | - | guards |
| LESSON-053 | PROCESS_GAP | `change_management.py` (區塊完整性檢查) | - | guards |
| LESSON-063 | COGNITIVE_COMPLEXITY | `sonarcloud_gate.py` | - | guards |
| LESSON-071 | ARCHITECTURE_EROSION | `frameworks/config.py` | ADR-SEC-005 | guards |
| LESSON-072 | REFACTORING_GUARD | `frameworks/config.py` | ADR-SEC-005 | guards |
| LESSON-073 | PROCESS_GAP | `phase-0-orchestration.md` (python -m pytest) | - | guards |
| LESSON-074 | CODE_QUALITY | `convergence.py` (unused imports cleanup) | - | guards |
| LESSON-075 | ARCHITECTURE_EROSION | `AGENTS.md` (Scope Rules) | ADR-STR-024 | guards |
| LESSON-076 | NEW_CAPABILITY | `tests/test_code_quality.py` | ADR-STR-027 | guards |

> LESSON-015~019, LESSON-021, LESSON-035~039 不存在（ID 跳號或已合併）

### ADR → Skill 修改映射

| ADR | 修改的 Skill | 連結 |
|-----|-------------|------|
| ADR-GOV-003 | `micro_validation.py` | modified-by |
| ADR-GOV-004 | `micro_validation.py`, `orchestrator.py`, `completion_check.py` | modified-by |
| ADR-GOV-005 | `orchestrator.py` | modified-by |
| ADR-GOV-006 | `micro_validation.py`, `completion_check.py` | modified-by |
| ADR-GOV-007 | `micro_validation.py` | modified-by |
| ADR-GOV-008 | `change_management.py`, `micro_validation.py` | modified-by |
| ADR-GOV-009 | `orchestrator.py` | modified-by |
| ADR-GOV-010 | `change_management.py` | modified-by |
| ADR-GOV-011 | `root_cause_leftshift.py`, `change_management.py` | modified-by |
| ADR-GOV-012 | `AGENTS.md` (Step 0) | modified-by |
| ADR-GOV-013 | `exhaustive_search.py` | modified-by |
| ADR-GOV-016 | 16 個 `workflow-skills/*.md` | modified-by |
| ADR-GOV-020 | `AGENTS.md`, `exhaustive_search.py` | modified-by |
| ADR-GOV-022 | 15 CREATE + `impact_analysis.py` + `AGENTS.md` | modified-by |
| ADR-GOV-023 | `traceability_validator.py`, `root_cause_leftshift.py`, `adr_governance.py` | modified-by |
| ADR-GOV-024 | `AGENTS.md` (#15 + Step 輸出協議 + Step 0-12 輸出標注) | modified-by |
| ADR-GOV-025 | `risk_manager.py` (CREATE), `risk-register.md` (CREATE), `tech-debt-register.md` (CREATE), `tech_debt_manager.py` (Step 5), `ADR-TEMPLATE.md` (關聯產出物), `AGENTS.md` (Routing+12.5), `security_audit.py` (Step 5), `orchestrator.py` (Step 3.5), `orchestrator.py` (Step 5.5), `root_cause_leftshift.py` (Step 7.5), `orchestrator.py` (Step 4.5) | modified-by |
| ADR-GOV-026 | `pyproject.toml`, `test_invariants_verifier.py`, `graph.py`, `nodes.py`, `warning_policy_verifier.py` | modified-by |
| ADR-STR-001 | `src/agentic_workflow/` (全目錄結構重構，每 Class 獨立檔案) | modified-by |
| ADR-STR-007 | `adapters/langgraph/graph_builder.py` (DELETED), `tests/test_graph_builder.py` (DELETED), `config.yaml` (workflow_graph removed), `docs/adr/ADR-STR-006.md` (amended), `invariants_verifier.py`, `test_invariants_verifier.py`, `tests/step_defs/test_langgraph_dag.py`, `README.md`, `CHANGELOG.md` | modified-by |
| ADR-STR-008 | `adapters/llm/langchain_adapter.py` (TokenLimitExceededError + continuation) | modified-by |
| ADR-STR-009 | `ruff.toml` (line-length 88→120), `pyproject.toml` (line-length 88→120) | modified-by |
| ADR-OPS-001 | `domain/algorithms/sonarcloud_gate.py`, `adapters/langgraph/nodes.py` (node_sonarcloud_gate) | modified-by |
| ADR-SEC-005 | `frameworks/config.py` → `frameworks/config/` (重構), `adapters/langgraph/nodes.py` | modified-by |
| ADR-STR-024 | `invariants_verifier.py`, `invariants_run.py`, tests | modified-by |

> ADR-GOV-001/002/014/015/017/018/019/021 為治理原則定義，嵌入 AGENTS.md Core Directives

### ADR 取代關係圖

```
FR-014 → Superseded by → FR-014-v2 (ADR-STR-003: 自主收斂取代 HITL)
FR-019 → Superseded by → FR-019-v2 (ADR-STR-003: DAG checkpoint 取代 workflow-state.md)
FR-021 → Superseded by → FR-021-v2 (ADR-STR-003: checkpoint recovery 取代 file recovery)
INV-002 → Superseded by → INV-002-v2 (ADR-STR-003: auto-gate取代 HITL gate)
INV-005 → Superseded by → INV-005-v2 (ADR-STR-003: stepM before auto-gate)
ADR-STR-006 (workflow_graph 部分) → Superseded by → ADR-STR-007 (單一建圖路徑)
```

> 當 ADR 狀態變更為 Superseded 時，在此記錄取代鏈：`ADR-xxx → Superseded by → ADR-yyy`

---

## 孤兒報告

| ID | 缺少 | 狀態 |
|----|------|------|
| （無孤兒） | — | — |

---

## 覆蓋統計

| 階段 | ID 前綴 | 已指派 | 有上游 | 有下游 | 覆蓋率 |
|------|---------|--------|--------|--------|--------|
| Phase 2.0 | BG-xxx | 5 | — (源頭) | 5/5 | 100% |
| Phase 2.1 | S-xxx | 3 | 3/3 | — | 100% |
| Phase 2.2 | FEA-xxx | 23 | 23/23 | 23/23 | 100% |
| Phase 2.2 | RISK-xxx | 5 | 5/5 | — (ISO 31000 完整欄位) | 100% |
| Phase 2.2 | DEBT-xxx | 6 | 6/6 | — | 100% |
| Stage 3 | FR-xxx | 42+3v2 | 45/45 | 45/45 | 100% |
| Stage 3 | NFR-xxx | 10 | 10/10 | — (約束) | 100% |
| Stage 3 | UC-xxx | 15 | 15/15 | 15/15 | 100% |
| Stage 3 | ADR-STR-xxx | 14 | 14/14 | — | 100% |
| 治理層 | ADR-GOV-xxx | 27 | 27/27 | — (治理) | 100% |
| Stage 4 | ALG-xxx | 11 | 11/11 | 11/11 | 100% |
| Stage 5 | CLS-xxx | 21 | 21/21 | 21/21 | 100% |
| Stage 5 | EVT-xxx | 10 | 10/10 | — | 100% |
| Stage 6 | INV-xxx | 25 | 25/25 | 25/25 | 100% |
| Stage 7 | SC-xxx | 21 | 21/21 | 21/21 | 100% |
| **自動化** | FR→Hook | 1 | 1/1 | — (實作) | 100% |
| Stage 8 | TC-xxx | 24 | 24/24 | 24/24 | 100% |
| Skill 實作 | FR→Skill | 28 | 28/28 | — (映射) | 100% |
| Skill 守衛 | LESSON→Skill | 45 | 45/45 | — (映射) | 100% |
| Skill 修改 | ADR→Skill | 29 | 29/29 | — (映射) | 100% |
| 風險追溯 | RISK→FEA | 5 | 5/5 | — (治理) | 100% |
| 技術債追溯 | DEBT→FR | 6 | 6/6 | — (治理) | 100% |
| **合計** | — | **360** | — | — | **100%** |

> **Status**: RISK-001 已驗證緩解，實作切換邏輯並補齊 TC-SONAR-004。
> **未應對風險**: 1 (RISK-004 MEDIUM)
> **技術債**: 1 (DEBT-008 P3)
