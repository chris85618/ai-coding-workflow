# Technical Debt Register

> **獨立文件**：每個專案在 `docs/` 下維護一份 `tech-debt-register.md`。
> 本文件為範本與執行協議定義。

---

## 技術債識別來源

| 來源 | 偵測方式 | 指派 Stage |
|------|---------|-----------|
| 程式碼品質問題 | SonarCloud 掃描 + Stage 8 品質閘門 | Stage 8 |
| 測試覆蓋缺口 | 覆蓋率報告 + BDD 場景缺口 | Stage 7/8 |
| 架構債 | Agent α 審查 + `/review` | Stage 5 |
| 效能債 | 基線量測 + `/benchmark` | Stage 4/8 |
| 文件債 | 追溯矩陣孤兒偵測 | 任意 Stage |
| 流程債 | 追溯缺口 + 影響分析紀錄 | Phase 10 |
| 安全債 | 三層安全審計 HIGH+ 項目 | Stage 5/8 |

---

## RICE 優先排序框架

每個 DEBT-xxx 項目必須計算 RICE 分數：

```
RICE = (Reach × Impact × Confidence) / Effort

Reach:     受影響的元件/使用者數量 (1-100)
Impact:    修復後的改善程度 (0.5=低, 1.0=中, 2.0=高, 3.0=極高)
Confidence: 對 Reach 和 Impact 估算的信心 (0.5-1.0)
Effort:    修復所需人天 (0.25-20)
```

---

## 四象限分類

```
                    高影響
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    │   Strategic     │   Quick Wins    │
    │   P1 下個 Sprint │   P0 立即修復   │
    │                 │                 │
高努力 ────────────────┼──────────────── 低努力
    │                 │                 │
    │   Avoid         │   Incremental   │
    │   P3 稍後評估    │   P2 排入 Backlog│
    │                 │                 │
    └─────────────────┼─────────────────┘
                      │
                    低影響
```

**分類規則**:
- Quick Wins: Impact >= 1.5 AND Effort <= 2.0 → P0
- Strategic: Impact >= 1.5 AND Effort > 2.0 → P1
- Incremental: Impact < 1.5 AND Effort <= 2.0 → P2
- Avoid: Impact < 1.5 AND Effort > 2.0 → P3

---

## Tech Debt Register 文件格式

每個專案維護 `docs/tech-debt-register.md`：

```markdown
# Technical Debt Register - [專案名稱]

**Generated**: [ISO 8601 timestamp]
**Last Updated**: [ISO 8601 timestamp]
**Total Debt Items**: [N]
**Total Estimated Effort**: [N] person-days

---

## Executive Summary

### 類型分佈
| 類型 | 數量 | 佔比 | 總努力 (天) |
|------|------|------|------------|
| 程式碼品質 | [N] | [%] | [N] |
| 測試債 | [N] | [%] | [N] |
| 架構債 | [N] | [%] | [N] |
| 效能債 | [N] | [%] | [N] |
| 安全債 | [N] | [%] | [N] |
| **合計** | **[N]** | **100%** | **[N]** |

### 嚴重度分佈
| 嚴重度 | 數量 | 佔比 |
|--------|------|------|
| CRITICAL | [N] | [%] |
| HIGH | [N] | [%] |
| MEDIUM | [N] | [%] |
| LOW | [N] | [%] |

---

## Quick Wins (P0 - 立即修復)

| DEBT-ID | 標題 | 類型 | Impact | Effort | RICE | 追溯 |
|---------|------|------|--------|--------|------|------|
| DEBT-001 | [標題] | [類型] | [N] | [N]d | [N] | FR-xxx |

## Strategic (P1 - 下個 Sprint)

| DEBT-ID | 標題 | 類型 | Impact | Effort | RICE | 追溯 |
|---------|------|------|--------|--------|------|------|

## Incremental (P2 - Backlog)

| DEBT-ID | 標題 | 類型 | Impact | Effort | RICE | 追溯 |
|---------|------|------|--------|--------|------|------|

## Avoid (P3 - 稍後評估)

| DEBT-ID | 標題 | 類型 | Impact | Effort | RICE | 追溯 |
|---------|------|------|--------|--------|------|------|

---

## 詳細項目

### DEBT-001: [標題]

**類型**: [CODE_QUALITY / TEST_DEBT / ARCHITECTURAL / PERFORMANCE / SECURITY]
**嚴重度**: [CRITICAL / HIGH / MEDIUM / LOW]
**位置**: [檔案路徑或元件名稱]
**優先序**: P0 / P1 / P2 / P3

**描述**: [問題描述]

**RICE 計算**:
- Reach: [N] ([說明])
- Impact: [N] ([說明])
- Confidence: [N] ([說明])
- Effort: [N] 天 ([說明])
- RICE Score: [N]

**修復步驟**:
1. [步驟 1]
2. [步驟 2]

**追溯**:
- 相關需求: [FR-xxx]
- 相關測試: [TC-xxx]
- 相關影響分析: [IMP-xxx]

**狀態**: Open / In Progress / Fixed / Won't Fix
**目標 Sprint**: [Sprint N]
```

---

## Sprint 債務容量規則

- 每個 Sprint 分配 **20% 容量**用於技術債償還
- 使用貪心演算法：依 RICE 分數降序選取項目，直到容量用盡
- P0 (Quick Wins) 優先於所有其他象限
- CRITICAL 嚴重度的 DEBT 項目阻塞 Phase 9 `/ship`
