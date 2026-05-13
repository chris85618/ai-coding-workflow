# Skill: S2C 專案章程生成

> **觸發條件**：Phase 2.0
> **輸入**：專案目錄、使用者描述
> **輸出**：`docs/project-charter.md` (含 BG-xxx ID)

---

## 執行協議

```
Step 1: 資源掃描
FOR each file IN project_directory:
  classify(file) → source_code / config / docs / test / asset
  extract_metadata(file) → language, framework, dependencies
  REPORT: project_profile

Step 2: 商業目標萃取
FROM user_description:
  problem_statement → verb_extraction → required_action → BG-xxx
FROM success_metrics:
  metric → measurable_condition → target_value → BG-xxx

Step 3: 風險分類
FOR each BG-xxx:
  impact = assess(1-5)
  probability = assess(1-5)
  risk_level = impact × probability
  IF risk_level >= 10: flag_for_hitl()

Step 4: 產出
→ 寫入 docs/project-charter.md
→ 初始化追溯矩陣
```
