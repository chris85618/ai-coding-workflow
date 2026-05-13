# Skill: S2C 需求分解

> **觸發條件**：Stage 3（技術規劃）
> **輸入**：FEA-xxx
> **輸出**：FR-xxx, NFR-xxx, UC-xxx → `docs/requirements.md`, `docs/use-cases.md`

---

## 執行協議

```
FOR each FEA-xxx IN in_scope:
  decompose → FR-xxx (functional requirements)
  extract_nfr → NFR-xxx (non-functional requirements)
  identify_use_cases → UC-xxx

FOR each UC-xxx:
  define_preconditions()
  define_postconditions()
  define_main_flow()
  define_alternative_flows()
  define_exception_flows()

FOR each UC-xxx:
  risk_score = impact × probability
  IF risk_score >= 15: classify_as_critical()
  enumerate_edge_cases()
  identify_failure_modes()
```

產出 → `docs/requirements.md` + `docs/use-cases.md` + 更新追溯矩陣
