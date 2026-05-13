# Skill: SonarCloud 品質閘門

> **觸發條件**：Stage 8 子步驟 8c（所有測試通過後）
> **輸入**：測試通過的程式碼
> **輸出**：品質閘門結果 + DEBT-xxx 項目

---

## 門檻

| 維度 | 全局 | 新程式碼 |
|------|------|---------|
| 覆蓋率 | ≥ 80% | ≥ 85% |
| 重複率 | ≤ 5% | ≤ 3% |
| 函式複雜度 | ≤ 15 | ≤ 15 |
| 認知複雜度 | ≤ 15 | ≤ 15 |
| 安全漏洞 (Critical/High) | 0 | 0 |
| Blocker/Critical Smells | 0 | 0 |
| Major Smells | ≤ 10 | ≤ 3 |
| 技術債比率 | ≤ 5% | ≤ 5% |
| 可靠性/可維護性 | A | A |

## 執行協議

```
1. 執行 SonarCloud 掃描
2. 全部 PASS → 繼續
3. 任何 FAIL → 自主修復 → 重新掃描
4. 修復 3 次仍 FAIL → 上報 HITL
5. 安全熱點審查率 100%
6. TODO/FIXME → 轉為 DEBT-xxx（觸發 tech-debt-collect.md）
```
