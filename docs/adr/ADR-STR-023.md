# ADR-STR-023: 支援 OpenAI 相容 Provider 之配置策略

**Status**: Proposed
**Date**: 2026-05-17
**Category**: STR (Architecture)

## Context

隨著 LLM 生態系的發展，許多 Provider（如 OpenRouter, DeepSeek, Groq 等）提供與 OpenAI API 100% 相容的介面。
目前的系統架構雖然已具備 `OpenAIProvider`，但其 `base_url` 被硬編碼在 LangChain `ChatOpenAI` 的預設值中，無法透過配置修改。
這限制了系統切換至更具成本效益或特定能力之相容 Provider 的能力。

## Decision

擴充現有的 LLM 配置與適配器層，以支援自定義 Endpoints：

1. **值物件擴充 (Domain Layer)**：
   - 在 `agentic_workflow.domain.value_objects.ModelConfig` 新增 `base_url: str | None = None` 欄位。

2. **配置模型擴充 (Framework Layer)**：
   - 在 `agentic_workflow.frameworks.config.model_config.ModelConfig` (Pydantic) 新增 `base_url: str | None = None`。
   - 更新 `WorkflowConfigLoader` 確保能正確解析 YAML 中的 `base_url` 並支援環境變數置換。

3. **適配器邏輯更新 (Adapter Layer)**：
   - 修改 `agentic_workflow.adapters.llm.providers.openai.OpenAIProvider`，將 `model_cfg.base_url` 傳遞給 `ChatOpenAI` 構造函數。

4. **環境變數規範**：
   - 鼓勵使用 `${VAR:-default}` 語法在 `config.yaml` 中配置，並在 `.env` 中定義具體的 URL。

## Consequences

- (+) 增加系統的擴充性，可輕鬆接入任何 OpenAI 相容服務。
- (+) 降低對單一 Vendor 的依賴 (Vendor Lock-in)。
- (+) 維持 Clean Architecture 的整潔度，配置由外向內注入。
- (!) 需要注意不同 Provider 對於 `max_tokens` 或 `temperature` 的細微處理差異（由開發者配置負責）。

## FR/NFR Justification

- FR-065 (擴充 ModelConfig)
- FR-066 (OpenAIProvider 整合)
- FR-067 (YAML 配置支援)
- NFR-012 (安全性隔離)
