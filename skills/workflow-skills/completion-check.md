# Skill: 預發布完成檢查

> **觸發條件**：Phase 9（/ship 前）
> **輸入**：全專案追溯矩陣
> **輸出**：PASS / FAIL + 缺失報告

---

## Step 1: 追溯完整性

1. FOR each FR-xxx → ASSERT has_at_least_one(TC-xxx)，否則報 "FR-xxx 缺少驗證測試"
2. FOR each UC-xxx → ASSERT has_at_least_one(SC-xxx)，否則報 "UC-xxx 缺少 BDD 場景"
3. FOR each INV-xxx → ASSERT has_at_least_one(TC-xxx OR property_test)，否則報 "INV-xxx 缺少驗證"

## Step 2: DbC 三元組完整性

1. FOR each INV-xxx in `docs/invariants.md` → ASSERT has_precondition AND has_postcondition
2. FOR each CLS-xxx in `docs/domain-model.md` → ASSERT has_tag("[PRE]") AND has_tag("[INV]") AND has_tag("[POST]")

## Step 3: 追溯矩陣完整性

1. ASSERT no_orphan_ids()
2. ASSERT no_broken_chains()

## Step 4: 技術債檢查

1. ASSERT no_critical_debt()

## Step 5: 品質閘門

1. ASSERT sonarcloud_quality_gate_passed()

## Step 6: 安全審計

1. ASSERT three_layer_security_passed()

## Step 7: 自動化 ID 計數驗證（LESSON-005）

1. FOR each prefix IN {BG, S, FEA, RISK, FR, NFR, UC, ADR, ALG, CLS, EVT, INV, SC, TC}：
   - actual = grep -c "{prefix}-\d{3}" 來源文件
   - claimed = traceability-matrix.md 覆蓋統計表數字
   - ASSERT actual == claimed
2. 不接受 LLM 自我報告數字，必須從文件 grep

## Step 8: 變更紀錄完整性

1. FOR each ADR in `docs/adr/`：ASSERT has 「變更紀錄」區段（若有變更）
2. FOR each LESSON in ADR：ASSERT references updated skill
3. FOR each updated skill → ASSERT contains left-shift guard

---

## 判定

- 全部 PASS → /ship 放行
- 任一 FAIL → 阻塞，列出缺失清單
