# Skill: S2C 利害關係人分析

> **觸發條件**：Phase 2.1（在 /office-hours 之後）
> **輸入**：專案章程 (BG-xxx)、/office-hours 產出
> **輸出**：`docs/stakeholder-analysis.md` (含 S-xxx ID)

---

## Step 1: 利害關係人識別

1. FROM charter(BG-xxx) → extract_target_users → S-xxx (Primary User)
2. FROM charter(BG-xxx) → extract_metric_owners → S-xxx (Management)
3. FROM charter(BG-xxx) → extract_decision_authority → S-xxx (Decision Maker)
4. FROM charter(BG-xxx) → infer_technical_roles → S-xxx (Technical)

## Step 2: 影響力分析

1. FOR each S-xxx → profile(interests, concerns, power, engagement)
2. classify_influence(power × interest) → 象限分類：
   - High Power + High Interest = Manage Closely
   - High Power + Low Interest = Keep Satisfied
   - Low Power + High Interest = Keep Informed
   - Low Power + Low Interest = Monitor

## Step 3: RACI 分配

1. FOR each activity IN project_activities → assign R/A/C/I
2. 約束：每活動僅一個 Accountable

## Step 4: 驗證

1. ASSERT all_raci_have_single_accountable()
2. ASSERT high_influence_have_communication_plan()
3. ASSERT no_stakeholder_accountable_for_50_percent_plus()

## Step 5: 產出

1. 寫入 `docs/stakeholder-analysis.md`
2. 更新追溯矩陣：S-xxx → BG-xxx
