# Skill: S2C DDD 領域建模

> **觸發條件**：Stage 5（OOAD）
> **輸入**：UC-xxx, ALG-xxx
> **輸出**：CLS-xxx, EVT-xxx → `docs/domain-model.md`

---

## Step 1: 聚合識別

1. FOR each UC-xxx → identify_transaction_boundary()
2. extract_entities_and_value_objects()
3. define_aggregate_root() → CLS-xxx
4. document_preconditions() → CLS-xxx 方法的 [PRE] 標記
5. document_invariants() → INV-xxx（預留至 Stage 6）
6. document_postconditions() → CLS-xxx 方法的 [POST] 標記

## Step 2: 限界上下文

1. FOR each functional_domain → define_bounded_context()
2. establish_ubiquitous_language()
3. map_context_interfaces()

## Step 3: 領域事件

1. FOR each cross_aggregate_operation → identify_domain_event() → EVT-xxx
2. define_event_payload()
3. map_consumers()

## Step 4: 產出

1. 寫入 `docs/domain-model.md`
2. 更新追溯矩陣

## Step 5: PGVG 驗證

1. **UC↔CLS 逐一覆蓋斷言**：FOR each UC-xxx in input → ASSERT exists at least one CLS-xxx with trace "UC-xxx (models)"。覆蓋報告格式: "UC-001→CLS-001 ✅, UC-002→CLS-012 ✅, ..."（逐一列出）
2. **限界上下文 ↔ CLS 一致性**：FOR each bounded_context → FOR each UC in context → ASSERT context's UC has matching CLS。不接受泛稱 "N/N 覆蓋"
3. **自動化計數**：actual_cls = grep -c "### CLS-" domain-model.md；actual_evt = grep -c "### EVT-" domain-model.md；ASSERT matches claimed count
4. **格式驗證**：ASSERT all backtick pairs matched, tables aligned, no hardcoded paths
