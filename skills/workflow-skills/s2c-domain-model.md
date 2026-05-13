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

產出 → `docs/domain-model.md` + `docs/class-diagram.puml` + 更新追溯矩陣
