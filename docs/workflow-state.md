# Workflow State — Unified Agentic Workflow System

**Pipeline Position**: Phase 11 (Release v0.1.6) — ✅ DONE
**Last Position**: Phase 11 (Release v0.1.6)
**Status**: Domain Governance & Invariants Dependency Inversion Hardened.
**Last Updated**: 2026-05-17T15:20+08:00

## ⏳ WBS (Work Breakdown Structure)

- [x] DDD-01: 建立 ADR-STR-020 (DDD 實施準則) — ✅ DONE
- [x] DDD-02: 建立 `Findings`, `RepoMap`, `SymbolDef` 等值物件 (VO) — ✅ DONE
- [x] DDD-03: 將 `Stage` 重構為實體 (Entity) 並移至 `entities/` — ✅ DONE
- [x] DDD-04: 將 `Pipeline` 重構為聚合根 (Aggregate Root) — ✅ DONE
- [x] DDD-05: 實作應用層 Use Cases (Start, Advance, RunIteration) — ✅ DONE
- [x] DDD-06: 更新 `StateMapper` 與 LangGraph `nodes.py` 對齊 DDD — ✅ DONE
- [x] DDD-07: 修復 100% 類型檢查 (Mypy) 與格式 (Ruff) 錯誤 — ✅ DONE
- [x] DDD-08: 移除 `src/` 下所有 Legacy `models/` 檔案 — ✅ DONE
- [x] DDD-09: 重構 `tests/` 下所有內容改用 DDD 術語與結構 — ✅ DONE
- [x] DDD-10: 修復 `Pipeline` 與 `StateMapper` 的覆蓋率缺口 (100% Coverage) — ✅ DONE
- [x] CAD-01: 建立 ADR-STR-021 (Clean Architecture 深度對齊) — ✅ DONE
- [x] CAD-09: 語意化 Orchestrator 與 SecurityAudit 領域服務 — ✅ DONE
- [x] CAD-10: 實作 RepositoryCheckpointer 並接入 LangGraph — ✅ DONE
- [x] CAD-11: 更新測試套件對齊新 DI 結構 (828 Tests Pass) — ✅ DONE
- [x] CAD-02: 提煉 `TraceableIdVO` 與 `Findings` VO — ✅ DONE
- [x] CAD-03: 實作 `IPipelineRepository` 與 `MarkdownPipelineRepository` — ✅ DONE
- [x] CAD-04: 建立 `DependencyContainer` 並重構 Use Cases 依賴注入 — ✅ DONE
- [x] CAD-05: 隔離 LLM 邏輯至 `IAgentReasoner` Port — ✅ DONE
- [x] CAD-06: 重構 `nodes.py` 使用 DI 與通用語言 (Alpha/Beta) — ✅ DONE
- [x] CAD-07: 實作 `AnthropicReasoner` Adapter — ✅ DONE
- [x] CAD-08: 重構 `ImpactAnalysis` 為 Domain Service — ✅ DONE
- [x] CAD-09: 重構 `BlastRadius` 為 Specification — ✅ DONE
- [x] CAD-10: 補齊 DI Container 與 Use Case 單元測試 — ✅ DONE
- [x] LLM-01: 擴充 Domain `ModelConfig` VO 支援 `base_url` — ✅ DONE
- [x] LLM-02: 擴充 Framework `ModelConfig` Pydantic 支援 `base_url` — ✅ DONE
- [x] LLM-03: 修改 `OpenAIProvider` 整合 `base_url` — ✅ DONE
- [x] LLM-04: 更新測試案例驗證自定義 Endpoint 注入 — ✅ DONE
- [x] LLM-05: 更新 `config.yaml` 範例與 `.env.example` — ✅ DONE
- [x] CAD-12: 徹底重構 `nodes.py` 與 `sonar_adapter.py` 以使用 `SonarCloudConfig` 與 `InvariantsConfig` 依賴反轉，消除全域 singleton — ✅ DONE
- [x] CAD-13: 修正 Mock 引起的 truthiness 問題，以真實 value objects 取代測試中的 MagicMock 確保可靠測試 — ✅ DONE
- [x] CAD-14: 達成 100.00% 程式碼覆蓋率與 842 個測試案例全數通過，Mypy 與 Ruff 無任何錯誤 — ✅ DONE
- [x] CAD-15: 徹底移除 domain/algorithms/invariants_verifier.py 中 frameworks 之外層動態 imports，並於 frameworks/graph/ 下建立獨立 invariants_run.py 指令碼以符合依賴反轉原則，100% 覆蓋通過 — ✅ DONE

## 🚦 Gate Status

- [✅] Phase 0: 環境啟動
- [✅] Phase 1: 程式碼理解
- [✅] Phase 2: 專案分析
- [✅] Stage 3: 技術規劃 (ADR-STR-020)
- [✅] Stage 4: 演算法設計
- [✅] Stage 5: OOAD + 安全審計 (DDD Aggregates)
- [✅] Stage 6: 形式化驗證設計 (INV-xxx Migration)
- [✅] Stage 7: BDD/ATDD
- [✅] Stage 8: TDD + 測試 + 修復 (100% Pass)
- [✅] Phase 10: 反思與學習 (Dependency Inversion Hardening) — ✅ DONE

## 📌 Pending Escalations

- 無

## 📝 Session Summary

1. **Dependency Inversion Hardening**: Removed illegal dynamic imports from `invariants_verifier.py` (domain) to outer frameworks layer, and created a dedicated framework-layer run script `invariants_run.py` that imports inner-layer components.
2. **Test Suite Refactoring**: Ported and rewrote test cases to test the new framework-layer invariants runner script, securing 100.00% statement and branch coverage with zero type checking or linting errors.
