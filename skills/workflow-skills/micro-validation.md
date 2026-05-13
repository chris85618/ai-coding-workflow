# Skill: 左移微驗證迴圈

> **觸發條件**：每次微動作後自動執行（由 iter-loop.md 的 Step M 觸發）
> **輸入**：變更的 ID 和內容
> **輸出**：PASS / FAIL + 修復建議

---

## 微動作定義

任何產生或修改帶 ID 產出物的操作：
- 新增 ID
- 修改 ID 的內容或描述
- 刪除 ID
- 新增或修改追溯連結

---

## 執行協議

```
Step 1: 結構完整性
→ ID 格式是否符合前綴規格？（BG/S/FEA/FR/NFR/UC/ADR/ALG/CLS/EVT/INV/SC/TC/DEBT/RISK/IMP）
→ 序號是否連續且無重複？

Step 2: 正向追溯
→ 該 ID 是否有至少一條正向連結到下游？
→ 終端 ID（TC-xxx）免除

Step 3: 反向追溯
→ 該 ID 是否有至少一條反向連結到上游？
→ 源頭 ID（BG-xxx）免除

Step 4: 語意一致性
→ 下游 ID 描述是否為上游 ID 描述的具體化？
→ 範圍是否收斂（每層向下 ≤ 上游）？
→ 修改後意圖是否偏離原始 BG-xxx？
→ 同一追溯鏈上是否有矛盾？

Step 5: 孤兒偵測
→ 是否有 ID 無上游也無下游？
→ 是否有斷裂追溯鏈？

Step 6: 影響分析觸發
→ 觸發 skills/workflow-skills/impact-analysis-exec.md
→ 標記受影響下游 ID
```

## 結果判定

```
全數通過 ✅ → 繼續下一個微動作
任一失敗 ❌ → 自主修復 → 重新執行
修復 3 次仍失敗 → 上報 HITL
```
