# Skill: S2C 範圍定義 + Red Team 挑戰

> **觸發條件**：Phase 2.2
> **輸入**：BG-xxx, S-xxx
> **輸出**：`docs/scope-definition.md` (含 FEA-xxx ID)

---

## 執行協議

```
Step 1: Feature 衍生
FOR each BG-xxx:
  problem_statement → verb_extraction → required_action → FEA-xxx
FOR each success_metric IN BG-xxx:
  metric → data_needed → feature_providing_data → FEA-xxx
FOR each S-xxx WHERE influence = HIGH:
  interest → desired_outcome → feature_name → FEA-xxx

Step 2: 排除項目
FOR each related_but_unmentioned_feature:
  evidence = search_charter_for_mention()
  IF evidence = NONE: classify_as_out_of_scope(rationale)

Step 3: 約束萃取
FROM charter.trade_off_matrix:
  FOR each dimension WHERE rank <= 3:
    map_to_constraint_type(time / budget / technical / regulatory)
```

## Red Team 挑戰（強制執行）

```
挑戰 1: 範圍蔓延偵測
FOR each FEA-xxx IN in_scope:
  adjacent = identify_commonly_requested_adjacent()
  IF adjacent NOT IN out_of_scope:
    WARN → HITL: 納入 / 排除 / 接受風險

挑戰 2: 約束衝突偵測
scope_complexity = count(FEA-xxx) × avg_complexity
IF scope_complexity > available_capacity:
  WARN → HITL: 縮減範圍 / 延長時程 / 增加資源

挑戰 3: 隱性依賴偵測
FOR each FEA-xxx IN out_of_scope:
  FOR each S-xxx WHERE influence = HIGH:
    IF FEA-xxx satisfies S-xxx.core_interest:
      WARN → HITL: 納入 / 記錄風險 / 對齊
```

產出 → `docs/scope-definition.md` + 更新追溯矩陣
