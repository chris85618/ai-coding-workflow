# Risk Register — Unified Agentic Workflow System

> **標準**: ISO 31000:2018
> **Last Updated**: 2026-05-15T17:42+08:00
> **Total Active (Open/In-Progress)**: 3 (RISK-001, RISK-004, RISK-005) — RISK-004 降評 MEDIUM(8)→MEDIUM(6)
> **Total Closed/Rejected**: 2 (RISK-002, RISK-003)
> **維護 Skill**: `skills/workflow-skills/risk-management.md`
> **追溯矩陣**: `docs/traceability-matrix.md` § RISK → FEA

---

## Active Risks

### RISK-001: SonarCloud 依賴外部服務帳號

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-001 |
| **狀態** | in-progress |
| **類別** | OPERATIONAL |
| **機率** | 1 (罕見 <5%) ↓ 降評 |
| **影響** | 3 (中等 — 品質閘門無法執行) |
| **風險強度** | 3 (LOW) ↓ |
| **應對策略** | MT (緩解) |
| **應對動作** | 實作 `SonarCloudGate.verify_configuration` 校驗參數；缺失時自動降級為 WARNING 並記錄於 metadata (ADR-OPS-001) — **已於 2026-05-16 實測 active 成功** |
| **預期殘餘風險** | 2 (LOW) |
| **觸發來源** | Phase 2 — 範圍定義 Red Team 挑戰 3 |
| **受影響 FEA** | FEA-006 |
| **對應 LESSON** | LESSON-071, LESSON-072 |
| **對應 ADR** | ADR-OPS-001, ADR-SEC-005 |
| **建立日期** | 2026-05-13T00:00+08:00 |
| **最後更新** | 2026-05-16T07:42+08:00 |
| **負責人** | HITL |

**風險描述**：FEA-006 (SonarCloud 品質閘門) 依賴外部服務帳號。若帳號未設定或服務不可用，Stage 8 品質閘門無法執行，導致品質保證缺口。

---

### RISK-002: ADR 數量膨脹導致管理困難 — **CLOSED**

| 欄位 | 値 |
|------|-----|
| **ID** | RISK-002 |
| **狀態** | **closed** |
| **類別** | PROCESS |
| **機率** | 2 (5-25%) ↓ 降評 |
| **影響** | 2 (小 — 管理負擔增加但不阻塞) |
| **風險強度** | 4 (LOW) ↓ |
| **應對策略** | MT (緩解) → **已完成** |
| **應對動作** | ADR 登記簿已合併至 traceability-matrix.md 統一管理（ADR-GOV-016）；ADR 數量穩定在 ~30 筆 |
| **殖餘風險** | 2 (LOW) |
| **至 FEA** | FEA-009 |
| **對應 ADR** | ADR-GOV-002, ADR-GOV-016 |
| **關閉日期** | 2026-05-15T00:47+08:00 |
| **關閉理由** | ADR 數量穩定，traceability-matrix 統一管理有效。Phase 10 確認緩解完成 |

---

### RISK-003: docs/ 與 skills/ 版本漂移 — **CLOSED**

| 欄位 | 値 |
|------|-----|
| **ID** | RISK-003 |
| **狀態** | **closed** |
| **類別** | PROCESS |
| **機率** | 2 (5-25%) ↓ 降評 |
| **影響** | 2 (小 — 執行逻輯已全部在 skills/) |
| **風險強度** | 3 (LOW) ↓ |
| **應對策略** | MT (緩解) → **已完成** |
| **應對動作** | skills/workflow-skills/ 為唯一執行來源（AGENTS.md 型別规則）；docs/ 全部標記 Reference Only |
| **殖餘風險** | 2 (LOW) |
| **至 FEA** | FEA-001, FEA-009 |
| **對應 LESSON** | LESSON-022 |
| **對應 ADR** | ADR-GOV-022 |
| **關閉日期** | 2026-05-15T00:47+08:00 |
| **關閉理由** | Phase 10 完成確認，skills/ 為唯一執行來源，docs/ Reference Only 標記 16 個檔案已完成 |

---

### RISK-004: Session 結束前未執行完整 CM 協議

| 欄位 | 値 |
|------|-----|
| **ID** | RISK-004 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | **2 (5-25%)** |
| **影響** | **3 (中等 — 追溯品質下降但可補救)** |
| **風險強度** | **6 (MEDIUM) ↓ 降評** |
| **應對策略** | MT (緩解) |
| **應對動作** | AGENTS.md Step 12 CM 前置斷言（12.1 窮舉式檔案列舉）強制執行；ADR-GOV-010 規定 Session-End Hook 前置條件 |
| **殘餘風險** | 4 (LOW) |
| **觸發來源** | 歷史 session RCA — LESSON-009, LESSON-011 |
| **受影響 FEA** | FEA-006 |
| **對應 LESSON** | LESSON-009, LESSON-011, LESSON-030 |
| **對應 ADR** | ADR-GOV-010, ADR-GOV-011 |
| **最後更新** | 2026-05-16T07:40+08:00 |
| **負責人** | AI (本次 Session 驗證緩解有效) |

**風險描述**：AI Agent 在 session 結束前可能跳過 Step 12 的 Change Management 步驟，包括但不限於：未窮舉搜尋就建立 ID（如本次 RISK-001 ID 衝突事件）、未更新追溯矩陣、未登錄已知 DEBT/RISK。本 session (2026-05-14) 再次驗證此風險存在：AI 未窮舉搜尋 RISK-xxx 引用就直接從 RISK-001 開始編號，導致 ID 衝突。

---

### RISK-005: ADR-TEMPLATE 欄位過長導致 LLM 省略必填欄位

| 欄位 | 値 |
|------|-----|
| **ID** | RISK-005 |
| **狀態** | open |
| **類別** | PROCESS |
| **機率** | **2 (5-25%) ↓ 降評** |
| **影響** | 3 (中等 — 登錄表不完整，追溯品質下降) |
| **風險強度** | **6 (MEDIUM) ↓** |
| **應對策略** | MT (緩解) |
| **應對動作** | ADR-TEMPLATE 欄位標記「必填」/「選填 (optional)」；micro-validation.md 已加入 RISK/DEBT 欄位完整性檢查 |
| **殖餘風險** | 3 (LOW) |
| **觸發來源** | ADR-GOV-025 — 本次治理擴充識別 |
| **受影響 FEA** | FEA-006, FEA-007 |
| **對應 LESSON** | LESSON-029 |
| **對應 ADR** | ADR-GOV-025 |
| **最後更新** | 2026-05-15T00:47+08:00 |
| **負責人** | AI |

**風險描述**：RISK/DEBT 登錄表欄位較多（ISO 31000 屬性），當 LLM 在 token 預算緊張時可能省略非明顯必填欄位。

---

## Closed / Rejected Risks

### RISK-002: ADR 數量膨脹 — **Closed 2026-05-15**
ADR 數量穩定在 ~30 筆，traceability-matrix.md 統一管理有效，Phase 10 確認緩解完成。

### RISK-003: docs/skills 版本漂移 — **Closed 2026-05-15**
skills/workflow-skills/ 為唯一執行來源，docs/ Reference Only 標記 16 個檔案全部完成，Phase 10 確認緩解完成。

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
