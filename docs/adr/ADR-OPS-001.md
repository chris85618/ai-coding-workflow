# ADR-OPS-001: SonarCloud 閉環回饋與降級機制

**Status**: Accepted
**Date**: 2026-05-16
**Category**: OPS (Operations / Quality Gate)

## Context

SonarCloud 作為核心品質閘門（FEA-006），在自動化工作流中面臨以下挑戰：
1. **依賴風險**：外部服務帳號（Token/Project Key）若未設定，會導致 Stage 8 失敗。
2. **回饋斷裂**：SonarCloud 的檢測結果（Smells/Bugs）若只停留在外部平台，AI Agent 無法感知並進行系統性改善。

## Decision

實作 SonarCloud 閉環回饋與自動降級機制：
1. **配置校驗**：在 `node_sonarcloud_gate` 節點增加環境變數檢核。
2. **自動降級 (Graceful Degradation)**：若配置參數缺失，系統不應直接 FAILED，而是標記為 `PASS_WITH_WARNINGS` 並輸出 WARNING 給使用者。這符合 ADR-GOV-017 (LLM 原生與優雅降級)。
3. **閉環回饋 (Closed Loop)**：將 SonarCloud 傳回的 Issues 自動轉化為 `DEBT-SONAR-xxx` 技術債。
4. **追溯性**：所有轉化的技術債必須包含來源（SonarCloud Quality Gate）與影響檔案，以便後續迭代修復。

## Consequences

- (+) 解決了 RISK-001 (依賴外部帳號) 的阻塞風險。
- (+) 實現了品質回饋的系統化管理，讓 Agent 能夠「看到」並「修復」Sonar 報告的問題。
- (+) 確保了工作流的健壯性，參數缺失時仍能繼續執行其他環節。

## FR/NFR Justification

- FR-015 (SonarCloud Gate)
- FR-035 (參數缺失降級)
- FR-036 (結果轉技術債)
- NFR-001 (健壯性)
