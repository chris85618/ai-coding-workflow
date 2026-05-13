# Skill: S2C 利害關係人分析

> **觸發條件**：Phase 2.1（在 /office-hours 之後）
> **輸入**：專案章程 (BG-xxx)、/office-hours 產出
> **輸出**：`docs/stakeholder-analysis.md` (含 S-xxx ID)

---

## 執行協議

```
Step 1: 利害關係人識別
FROM charter(BG-xxx):
  extract_target_users → S-xxx (Primary User)
  extract_metric_owners → S-xxx (Management)
  extract_decision_authority → S-xxx (Decision Maker)
  infer_technical_roles → S-xxx (Technical)

Step 2: 影響力分析
FOR each S-xxx:
  profile(interests, concerns, power, engagement)
  classify_influence(power × interest) → quadrant
  → High Power + High Interest = Manage Closely
  → High Power + Low Interest = Keep Satisfied
  → Low Power + High Interest = Keep Informed
  → Low Power + Low Interest = Monitor

Step 3: RACI 分配
FOR each activity IN project_activities:
  assign_responsible(S-xxx)
  assign_accountable(S-xxx)  # 每活動僅一個 A
  assign_consulted(S-xxx[])
  assign_informed(S-xxx[])

VALIDATE:
  all_raci_have_single_accountable()
  high_influence_have_communication_plan()
  no_stakeholder_accountable_for_50_percent_plus()

Step 4: 產出
→ 寫入 docs/stakeholder-analysis.md
→ 更新追溯矩陣：S-xxx → BG-xxx
```
