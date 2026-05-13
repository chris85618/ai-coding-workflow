# Iteration Log

> **用途**：記錄每個 Stage 的 AI 自主收斂迭代過程和 HITL 決策。
> **格式**：結構化、可機器解析。每輪迭代一個區塊。
> **更新頻率**：每輪 Step A/B/M 完成後立即寫入。

---

## 格式定義

每個 Stage 的迭代紀錄使用以下格式：

```markdown
## Stage {N}: {名稱}

### Round {M}

**Timestamp**: [ISO 8601]
**Agent α Findings**:

| # | Severity | Dimension | Finding | Affected IDs |
|---|----------|-----------|---------|--------------|
| 1 | CRITICAL | T1 | [描述] | FR-001, UC-003 |
| 2 | HIGH | T3 | [描述] | ADR-STR-001 |

**Severity Distribution**: CRITICAL: {N}, HIGH: {N}, MEDIUM: {N}, LOW: {N}, YAGNI: {N}

**Agent β Resolutions**:

| # | α Finding | Resolution | Decision Flow Step | Files Modified |
|---|-----------|------------|--------------------|----------------|
| 1 | #1 | [修復摘要] | Occam + Merge | docs/requirements.md |

**Micro-validation Result**: PASS / FAIL (Step {N})
**Impact Analysis**: ADR-{CAT}-{xxx} 變更 #{N} (severity: {level})
**Fixed-point Assessment**: NOT_REACHED / APPROACHING / REACHED
  - Rationale: [為什麼判定為此狀態]

---

### HITL Decision (Round {M} 後)

> 僅在 AI 判定達不動點後填寫。

**Presented Summary**: [AI 收斂報告摘要（含不動點判定理由）]
**Fixed-point Status**: REACHED | DIVERGING
**User Choice**: [1] 加入需求後繼續 / [2] 通過 ✅
**User Feedback**: [若有]
**ADR Reference**: ADR-GATE-S{N}-{xxx}
**New Requirements** (if [1]): [描述]
```

---

## 活紀錄

> 以下為當前專案的實際迭代紀錄。

(尚無迭代紀錄)
