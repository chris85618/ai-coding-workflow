# Skill: 技術債收集 + RICE 排序

> **觸發條件**：Stage 8（SonarCloud 後）、Phase 10（Retro 時）
> **輸入**：SonarCloud 報告、測試覆蓋、Agent α 審查、安全審計
> **輸出**：DEBT-xxx → `docs/tech-debt-register.md`

---

## 收集來源

| 來源 | 偵測方式 |
|------|---------|
| 程式碼品質 | SonarCloud Code Smells |
| 測試缺口 | 覆蓋率報告 + BDD 場景缺口 |
| 架構債 | Agent α 審查 + /review |
| 效能債 | 基線量測 + /benchmark |
| 安全債 | 三層審計 HIGH+ 項目 |
| 文件債 | 追溯矩陣孤兒 |
| 流程債 | 追溯缺口 + 影響分析紀錄 |

## RICE 計算

```
RICE = (Reach × Impact × Confidence) / Effort

FOR each debt_item:
  reach = count_affected_components(1-100)
  impact = assess_improvement(0.5=低, 1.0=中, 2.0=高, 3.0=極高)
  confidence = assess_certainty(0.5-1.0)
  effort = estimate_person_days(0.25-20)
  rice = (reach × impact × confidence) / effort
  quadrant = classify(impact, effort)
  priority = assign_p0_to_p3(quadrant)
  → DEBT-xxx
```

Sprint 容量：20% 用於債務償還，貪心依 RICE 降序選取。
