# Skill: 技術債收集 + RICE 排序

> **觸發條件**：Stage 8（SonarCloud 後）、Phase 10（Retro 時）
> **輸入**：SonarCloud 報告、測試覆蓋、Agent α 審查、安全審計
> **輸出**：DEBT-xxx → `docs/tech-debt-register.md`

---

## Step 1: 收集來源盤點

從以下 7 個來源識別技術債：

| # | 來源 | 偵測方式 |
|---|------|----------|
| 1 | 程式碼品質 | SonarCloud Code Smells |
| 2 | 測試缺口 | 覆蓋率報告 + BDD 場景缺口 |
| 3 | 架構債 | Agent α 審查 + /review |
| 4 | 效能債 | 基線量測 + /benchmark |
| 5 | 安全債 | 三層審計 HIGH+ 項目 |
| 6 | 文件債 | 追溯矩陣孤兒 |
| 7 | 流程債 | 追溯缺口 + 影響分析紀錄 |

## Step 2: RICE 計算

對每個 debt_item 計算：

1. reach = count_affected_components (1-100)
2. impact = assess_improvement (0.5=低, 1.0=中, 2.0=高, 3.0=極高)
3. confidence = assess_certainty (0.5-1.0)
4. effort = estimate_person_days (0.25-20)
5. RICE = (reach × impact × confidence) / effort

## Step 3: 分類與排序

1. classify(impact, effort) → 象限分類
2. assign_priority(quadrant) → P0/P1/P2/P3
3. 產出 DEBT-xxx

## Step 4: Sprint 容量分配

1. 20% Sprint 容量用於債務償還
2. 依 RICE 降序貪心選取
