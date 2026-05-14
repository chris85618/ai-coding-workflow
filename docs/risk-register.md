# Risk Register — Unified Agentic Workflow System

> **標準**: ISO 31000:2018
> **Last Updated**: 2026-05-14T07:17+08:00
> **Total Active (Open/In-Progress)**: 5
> **Total Closed/Rejected**: 0
> **維護 Skill**: `skills/workflow-skills/risk-management.md`
> **追溯矩陣**: `docs/traceability-matrix.md` § RISK → FEA

---

## Active Risks

### RISK-001: SonarCloud 依賴外部服務帳號

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-001 |
| **狀態** | open |
| **類別** | OPERATIONAL |
| **機率** | 2 (5-25%) |
| **影響** | 3 (中等 — 品質閘門無法執行) |
| **風險強度** | 6 (MEDIUM) |
| **應對策略** | MT (緩解) |
| **應對動作** | 定義 SonarCloud 帳號設定為 Phase 0 環境啟動的前置條件；備援方案使用本地 linter |
| **預期殘餘風險** | 3 (LOW) |
| **觸發來源** | Phase 2 — 範圍定義 Red Team 挑戰 3 |
| **受影響 FEA** | FEA-006 |
| **對應 LESSON** | N/A |
| **對應 ADR** | N/A |
| **建立日期** | 2026-05-13T00:00+08:00 |
| **最後更新** | 2026-05-14T07:17+08:00 |
| **負責人** | HITL |

**風險描述**：FEA-006 (SonarCloud 品質閘門) 依賴外部服務帳號。若帳號未設定或服務不可用，Stage 8 品質閘門無法執行，導致品質保證缺口。

---

### RISK-002: ADR 數量膨脹導致管理困難

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-002 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | 3 (25-50%) |
| **影響** | 2 (小 — 管理負擔增加但不阻塞) |
| **風險強度** | 6 (MEDIUM) |
| **應對策略** | MT (緩解) |
| **應對動作** | ADR 登記簿已合併至 traceability-matrix.md 統一管理（ADR-GOV-016）；定期審查是否需要 Supersede 舊 ADR |
| **預期殘餘風險** | 2 (LOW) |
| **觸發來源** | ADR-GOV-002 — ADR 治理框架建立時 |
| **受影響 FEA** | FEA-009 |
| **對應 LESSON** | N/A |
| **對應 ADR** | ADR-GOV-002 |
| **建立日期** | 2026-05-13T00:00+08:00 |
| **最後更新** | 2026-05-14T07:17+08:00 |
| **負責人** | AI |

**風險描述**：治理框架演進過程中 ADR 數量持續增加（目前 26 筆），可能導致 LLM context 壓力和人類審閱負擔。ADR-INDEX 已合併至追溯矩陣以緩解。

---

### RISK-003: docs/ 與 skills/ 版本漂移

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-003 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | 3 (25-50%) |
| **影響** | 3 (中等 — 執行邏輯與歷史參照不一致) |
| **風險強度** | 9 (MEDIUM) |
| **應對策略** | MT (緩解) |
| **應對動作** | AGENTS.md Repository Scope Rules 明確定義 skills/ 為唯一執行來源、docs/ 為歷史參照（ADR-GOV-022）；Phase 10 增量更新知識圖譜 |
| **預期殘餘風險** | 3 (LOW) |
| **觸發來源** | ADR-GOV-022 — docs/ 執行邏輯吸收至 skills/ |
| **受影響 FEA** | FEA-001, FEA-009 |
| **對應 LESSON** | LESSON-022 |
| **對應 ADR** | ADR-GOV-022 |
| **建立日期** | 2026-05-14T05:15+08:00 |
| **最後更新** | 2026-05-14T07:17+08:00 |
| **負責人** | AI |

**風險描述**：ADR-GOV-022 將執行邏輯從 docs/ 遷移至 skills/ 後，docs/ 中的原始方法論檔案（phases/、stages/、governance/）可能隨時間與 skills/ 中的對應 skill 產生版本漂移，導致混淆。

---

### RISK-004: Session 結束前未執行完整 CM 協議

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-004 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | 3 (25-50%) |
| **影響** | 4 (大 — 產出物未持久化，治理繞道) |
| **風險強度** | 12 (HIGH) |
| **應對策略** | MT (緩解) |
| **應對動作** | AGENTS.md Step 12 CM 前置斷言（12.1 窮舉式檔案列舉）強制執行；ADR-GOV-010 規定 Session-End Hook 前置條件 |
| **預期殘餘風險** | 4 (LOW) |
| **觸發來源** | 歷史 session RCA — LESSON-009, LESSON-011 |
| **受影響 FEA** | FEA-006 |
| **對應 LESSON** | LESSON-009, LESSON-011, LESSON-030 |
| **對應 ADR** | ADR-GOV-010, ADR-GOV-011 |
| **建立日期** | 2026-05-14T07:03+08:00 |
| **最後更新** | 2026-05-14T07:17+08:00 |
| **負責人** | AI |

**風險描述**：AI Agent 在 session 結束前可能跳過 Step 12 的 Change Management 步驟，包括但不限於：未窮舉搜尋就建立 ID（如本次 RISK-001 ID 衝突事件）、未更新追溯矩陣、未登錄已知 DEBT/RISK。本 session (2026-05-14) 再次驗證此風險存在：AI 未窮舉搜尋 RISK-xxx 引用就直接從 RISK-001 開始編號，導致 ID 衝突。

---

### RISK-005: ADR-TEMPLATE 欄位過長導致 LLM 省略必填欄位

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-005 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | 3 (25-50%) |
| **影響** | 3 (中等 — 登錄表不完整，追溯品質下降) |
| **風險強度** | 9 (MEDIUM) |
| **應對策略** | MT (緩解) |
| **應對動作** | ADR-TEMPLATE 欄位標記「必填」/「選填 (optional)」；micro-validation.md 加入 RISK/DEBT 欄位完整性檢查 |
| **預期殘餘風險** | 3 (LOW) |
| **觸發來源** | ADR-GOV-025 — 本次治理擴充識別 |
| **受影響 FEA** | FEA-006, FEA-007 |
| **對應 LESSON** | LESSON-029 |
| **對應 ADR** | ADR-GOV-025 |
| **建立日期** | 2026-05-14T07:03+08:00 |
| **最後更新** | 2026-05-14T07:17+08:00 |
| **負責人** | AI |

**風險描述**：RISK/DEBT 登錄表欄位較多（ISO 31000 屬性），當 LLM 在 token 預算緊張時可能省略非明顯必填欄位。

---

## Closed / Rejected Risks

（目前無）

---

## 風險矩陣快照

```
影響\機率  | 1(罕見) | 2(不太可能) | 3(可能)  | 4(很可能) | 5(幾乎確定)
-----------|---------|------------|---------|----------|------------
5(災難)    |   5M    |    10H     |  15C    |   20C    |    25C
4(大)      |   4L    |     8M     | [12H]*  |   16C    |    20C
3(中等)    |   3L    |    [6M]†   |  [9M]‡§ |   12H    |    15C
2(小)      |   2L    |     4L     |  [6M]†† |    8M    |    10H
1(微小)    |   1L    |     2L     |   3L   |    4L    |     5M

* RISK-004 (機率3×影響4=12)
† RISK-001 (機率2×影響3=6)
†† RISK-002 (機率3×影響2=6)
‡ RISK-003 (機率3×影響3=9)
§ RISK-005 (機率3×影響3=9)

L=LOW, M=MEDIUM, H=HIGH, C=CRITICAL
```
