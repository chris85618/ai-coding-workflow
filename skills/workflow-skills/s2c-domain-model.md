# Skill: S2C DDD 領域建模

> **觸發條件**：Stage 5（OOAD）
> **輸入**：UC-xxx, ALG-xxx
> **輸出**：CLS-xxx, EVT-xxx → `docs/domain-model.md`

---

## 執行協議

```
Track 1: 聚合識別
FOR each UC-xxx:
  identify_transaction_boundary()
  extract_entities_and_value_objects()
  define_aggregate_root() → CLS-xxx
  document_invariants() → INV-xxx（預留至 Stage 6）

Track 2: 限界上下文
FOR each functional_domain:
  define_bounded_context()
  establish_ubiquitous_language()
  map_context_interfaces()

Track 3: 領域事件
FOR each cross_aggregate_operation:
  identify_domain_event() → EVT-xxx
  define_event_payload()
  map_consumers()
```

產出 → `docs/domain-model.md` + 更新追溯矩陣

---

## Post-Generation Validation Gate (PGVG) [LESSON-002]

```
PGVG-1: UC↔CLS 逐一覆蓋斷言
  FOR each UC-xxx in input:
    ASSERT exists at least one CLS-xxx with trace "UC-xxx (models)"
    IF missing: FAIL → 補建 CLS 再重驗
  覆蓋報告格式: "UC-001→CLS-001 ✅, UC-002→CLS-012 ✅, ..." （逐一列出）

PGVG-2: 限界上下文 ↔ CLS 一致性
  FOR each bounded_context:
    FOR each UC in context:
      ASSERT context's UC has matching CLS
  不接受泛稱 "N/N 覆蓋"，必須逐一列出

PGVG-3: 自動化計數
  actual_cls = grep -c "### CLS-" domain-model.md
  actual_evt = grep -c "### EVT-" domain-model.md
  ASSERT actual_cls matches claimed count
  ASSERT actual_evt matches claimed count

PGVG-4: 格式驗證
  ASSERT all backtick pairs matched
  ASSERT all markdown tables properly aligned
  ASSERT no hardcoded absolute paths
```
