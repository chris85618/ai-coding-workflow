# Skill: 預發布完成檢查

> **觸發條件**：Phase 9（/ship 前）
> **輸入**：全專案追溯矩陣
> **輸出**：PASS / FAIL + 缺失報告

---

## 執行協議

```
Step 1: 追溯完整性
FOR each FR-xxx:
  ASSERT has_at_least_one(TC-xxx) → "FR-xxx 缺少驗證測試"
FOR each UC-xxx:
  ASSERT has_at_least_one(SC-xxx) → "UC-xxx 缺少 BDD 場景"
FOR each INV-xxx:
  ASSERT has_at_least_one(TC-xxx OR property_test) → "INV-xxx 缺少驗證"

Step 2: 追溯矩陣完整性
ASSERT no_orphan_ids()
ASSERT no_broken_chains()

Step 3: 技術債檢查
ASSERT no_critical_debt()

Step 4: 品質閘門
ASSERT sonarcloud_quality_gate_passed()

Step 5: 安全審計
ASSERT three_layer_security_passed()

全部 PASS → /ship 放行
任一 FAIL → 阻塞，列出缺失清單
```
