# ADR-STR-006: 外部化 YAML 配置 (Model & Prompts)

**Status**: Accepted
**Date**: 2026-05-15
**Category**: STR (Architecture)

## Context

LangGraph 工作流中的每一個節點（Agent α 破綻發掘、Agent β 收斂、微驗證、根因左移、影響分析）都需要與 LLM 互動。
將 Prompt 和指定的 Model 名稱 hardcode 在 Python 原始碼中會導致：
1. 難以針對單一專案進行調整與優化。
2. 違反開閉原則（OCP），更改 Prompt 需修改業務邏輯層。

## Decision

建立 `config.yaml` 作為所有 LLM 互動行為的單一事實來源。
1. **模型配置**：定義 `reasoning_model`（發散）、`editing_model`（收斂/微驗證）、`fallback_model` 等。
2. **提示詞配置 (Prompts)**：將所有 Agent 角色指令（System Prompts）與具體任務指令外部化。包含 Agent α 的批判指引、Agent β 的整合策略、微驗證的修復指示、根因左移的 5 Whys 分析模板等。
3. Python `config.py` 負責在初始化時將 `config.yaml` 載入為不可變的 Pydantic 模型（`CLS-019 YamlConfig`）。

## Consequences

- (+) 完全解耦了提示詞工程與流程工程。
- (+) 允許使用者在不修改原始碼的情況下，客製化 AGENTS.md 所規定的數十種檢查邏輯與角色設定。
- (+) 提高了系統的可移植性與實驗彈性。

## FR/NFR Justification

- FR-032 (外部化模型與提示詞配置)
- NFR-010 (配置可熱載與易讀性)
