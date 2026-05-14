# Tech Debt Register — Unified Agentic Workflow System

> **Last Updated**: 2026-05-14T08:36+08:00
> **Total Active Items**: 0
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

## Closed / Resolved Debt

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
