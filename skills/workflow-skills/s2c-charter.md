# Skill: S2C 專案章程生成

> **觸發條件**：Phase 2.0
> **輸入**：專案目錄、使用者描述
> **輸出**：`docs/project-charter.md` (含 BG-xxx ID)

---

## Step 1: 資源掃描

1. FOR each file IN project_directory → classify(file) → source_code / config / docs / test / asset
2. extract_metadata(file) → language, framework, dependencies
3. 產出：project_profile

## Step 2: 商業目標萃取

1. FROM user_description → problem_statement → verb_extraction → required_action → BG-xxx
2. FROM success_metrics → metric → measurable_condition → target_value → BG-xxx

## Step 3: 風險分類

1. FOR each BG-xxx → impact = assess(1-5), probability = assess(1-5)
2. risk_level = impact × probability
3. IF risk_level >= 10 → flag_for_hitl()

## Step 4: 產出

1. 寫入 `docs/project-charter.md`
2. 初始化追溯矩陣

## Step 5: PGVG 驗證

1. **格式驗證**：ASSERT all backtick pairs matched, headings sequential, no hardcoded absolute paths, metadata block properly formatted
2. **BG ID 完備性**：ASSERT BG-xxx count >= 1, each BG-xxx has 描述/成功指標/優先順序
3. **風險交叉驗證**：FOR each BG-xxx with risk_level >= 10 → ASSERT flagged_for_hitl == true
