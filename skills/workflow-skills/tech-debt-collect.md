# Skill: 技術債收集 + RICE 排序

> **觸發條件**：Stage 8（SonarCloud 後）、Phase 10（Retro 時）
> **輸入**：SonarCloud 報告、測試覆蓋、Agent α 審查、安全審計
> **輸出**：DEBT-xxx → `docs/tech-debt-register.md`

---

## Step 1: 收集來源盤點

從以下 8 個來源識別技術債：

| # | 來源 | 偵測方式 |
|---|------|----------|
| 1 | 程式碼品質 | SonarCloud Code Smells |
| 2 | 測試缺口 | 覆蓋率報告 + BDD 場景缺口 |
| 3 | 架構債 | Agent α 審查 + /review |
| 4 | 效能債 | 基線量測 + /benchmark |
| 5 | 安全債 | 三層審計 HIGH+ 項目 |
| 6 | 文件債 | 追溯矩陣孤兒 |
| 7 | 流程債 | 追溯缺口 + 影響分析紀錄 |
| 8 | 延後實作債 | `/ponytail-debt` 掃描 `ponytail:` 註解（工具不可用時 `grep -rn "ponytail:"`） |

> **ID 指派前置條件 (LESSON-030 守衛)**：指派 DEBT-xxx ID 前，**必須**讀取 `{target_repo}/docs/traceability-matrix.md` § DEBT→FR 節，掃描最大序號後遞增。若矩陣不存在則窮舉搜尋全 repo（grep -rn "DEBT-"）。禁止「假設從 DEBT-001 開始」。

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
3. P0（Critical）不受容量限制，立即處理
4. 每季度全面重新評估 RICE 分數

## Step 5: 更新登錄表 & 追溯矩陣（強制）

> **每次識別或更新 DEBT-xxx 後必須執行**：

1. 打開 `{target_repo}/docs/tech-debt-register.md`
   - 新增/更新對應 DEBT-xxx 完整記錄（含所有必填欄位）
   - 更新 `Total Active Items` 計數
2. 打開 `{target_repo}/docs/traceability-matrix.md`
   - 在「DEBT → FR」節新增/更新對應行
   - 在覆蓋統計更新 DEBT-xxx 計數
3. 若 DEBT 狀態變 resolved/cancelled → 移至 `Closed Debt` 節，更新計數
4. DEBT-xxx 若有對應 RISK-xxx → 同步呼叫 `risk-management.md` (Step 5) 更新風險登錄

