# Skill: S2C BDD 場景生成

> **觸發條件**：Stage 7（BDD/ATDD）
> **輸入**：UC-xxx, INV-xxx
> **輸出**：SC-xxx → `docs/bdd-scenarios.md` + 測試檔案

---

## 執行協議

```
FOR each UC-xxx:
  generate_happy_path_scenario() → SC-xxx
  generate_alternative_flow_scenarios() → SC-xxx
  generate_exception_flow_scenarios() → SC-xxx
  generate_boundary_scenarios() → SC-xxx

FOR each SC-xxx:
  format_given_when_then()
  link_to_uc(UC-xxx)
  link_to_inv(INV-xxx) IF applicable

Test organization:
  unit/          → TC-xxx (Stage 8)
  integration/   → TC-xxx (Stage 8)
  e2e/           → TC-xxx (Stage 8)
  bdd/           → SC-xxx (this Stage)
  property/      → SC-xxx (this Stage)
```

產出 → `docs/bdd-scenarios.md` + `docs/test-structure.md` + 更新追溯矩陣
