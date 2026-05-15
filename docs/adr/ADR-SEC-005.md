# ADR-SEC-005: 配置網關安全性與 Clean Architecture 存取限制

**Status**: Accepted
**Date**: 2026-05-16
**Category**: SEC (Security) / STR (Architecture)

## Context

目前的配置機制存在以下風險：
1. `.env` 變數可能被 `src/` 中任何地方透過 `os.getenv` 直接存取，違反 Clean Architecture 的邊界規則。
2. SonarCloud 等敏感參數（TOKEN）若放在 `config.yaml` 中，容易被無意間 commit。
3. `config.yaml` 的職責過於模糊，混合了策略配置與環境變數引用。

## Decision

實施嚴格的配置隔離機制：

1. **唯一入口 (Single Entry Point)**：
   - 只有 `src/agentic_workflow/frameworks/config.py` (Infrastructure Layer) 被允許呼叫 `dotenv` 和 `os.getenv`。
   - 禁止在 `src/` 的其餘任何地方（Domain, Application, Adapters）直接存取環境變數。

2. **祕鑰隔離 (Secret Isolation)**：
   - `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `SONAR_TOKEN` 等敏感資訊**必須**存放在 `.env`。
   - `config.yaml` 僅存放非敏感的模型參數、提示詞範本與 SonarCloud 元數據（Project Key, Org）。

3. **依賴反轉 (Dependency Inversion)**：
   - Domain Layer 定義配置的實體 (Entity) 或數值物件 (Value Object)。
   - Frameworks Layer 的 `config.py` 負責將 `.env` 與 `config.yaml` 合併並轉換為 Domain Model。
   - 內層透過構造函數注入或介面存取配置。

4. **SonarCloud 參數規範**：
   - `SONAR_TOKEN` 強制移出 `config.yaml` 並進入 `.env`。
   - 更新 `.env.example` 以反映此變更。

## Consequences

- (+) 確保祕鑰安全，防止洩漏至版本控制。
- (+) 強制執行 Clean Architecture 邊界，提升程式碼可測試性（可輕易 Mock 配置）。
- (+) 統一配置管理路徑，降低認知負擔。
- (-) 增加了新增配置項時的層次轉換開銷。

## FR/NFR Justification

- FR-032 (外部化配置) - 強化安全性
- NFR-004 (架構整潔度)
- NFR-011 (安全性規範)
