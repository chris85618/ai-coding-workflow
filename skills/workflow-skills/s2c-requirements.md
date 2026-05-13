# Skill: S2C 需求分解

> **觸發條件**：Stage 3（技術規劃）
> **輸入**：FEA-xxx（In-Scope）
> **輸出**：FR-xxx, NFR-xxx, UC-xxx → `docs/requirements.md`, `docs/use-cases.md`

---

## 執行協議

```
FOR each FEA-xxx IN in_scope:
  decompose → FR-xxx (functional requirements)
    TYPE: FUNCTIONAL | INTERFACE | DATA | SECURITY | PERFORMANCE
    FORMAT: "系統必須 [動詞] [受詞]，以 [目的]"
  extract_nfr → NFR-xxx (non-functional requirements)
    TYPES: PERFORMANCE | SECURITY | SCALABILITY | RELIABILITY | USABILITY
  identify_use_cases → UC-xxx
    FORMAT: "作為 [角色]，我想 [動作]，以便 [目的]"

FOR each UC-xxx:
  define_preconditions()      # 前置條件（系統狀態要求）
  define_invariants()         # 不變量（執行期間必須恆真的命題；引用相關 INV-xxx）
  define_postconditions()     # 後置條件（成功/失敗後系統狀態）
  define_main_flow()          # 主流程（步驟編號清單）
  define_alternative_flows()  # 替代流程（命名為 Alt-N）
  define_exception_flows()    # 例外流程（命名為 Exc-N）

FOR each UC-xxx:
  risk_score = impact × probability   # 1-5 × 1-5 = 1-25
  IF risk_score >= 15: classify_as_critical()
  enumerate_edge_cases()
  identify_failure_modes()
```

產出 → `docs/requirements.md` + `docs/use-cases.md` + 更新追溯矩陣

---

## Post-Generation Validation Gate (PGVG)

每次執行後立即驗證：

```
2a 格式驗證：
   - 所有 FR-xxx 格式符合 "系統必須 [動詞]..."
   - 所有 NFR-xxx 有明確度量標準（非主觀描述）
   - 所有 UC-xxx 有完整的 5 個組成部分

2b 覆蓋斷言：
   - 每個 in_scope FEA-xxx 至少有 1 個 FR-xxx
   - 每個 in_scope FEA-xxx 至少有 1 個 UC-xxx
   - verify: count(FR-xxx) >= count(FEA-xxx)

2c 計數驗證（grep 實際計數，非自我報告）：
   fr_count   = grep "^| FR-" docs/requirements.md | wc -l
   uc_count   = grep "^| UC-" docs/use-cases.md | wc -l
   fea_count  = grep "^| FEA-" docs/scope-definition.md | wc -l
   ASSERT fr_count >= fea_count
   ASSERT uc_count >= fea_count

2d 語意驗證：
   FOR each FR-xxx: verify 可測試性（有明確 pass/fail 條件）
   FOR each NFR-xxx: verify 有量化標準（e.g., 95th percentile < 200ms）

2e 追溯驗證：
   FOR each FR-xxx: verify link_to(FEA-xxx) exists in traceability-matrix.md
   FOR each UC-xxx: verify link_to(FEA-xxx) exists in traceability-matrix.md
   FOR each UC-xxx: verify link_to(FR-xxx) exists
```

> **LESSON-001**：計數必須用 grep 實際驗算，禁止 LLM 自我報告。
