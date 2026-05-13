# Skill: 根因左移

> **觸發條件**：**所有變更，無例外。全面強制執行。**
> **禁止 N/A 判定**：AI 不得以「非 FIX」「本次無問題」「變更太小」等任何理由跳過此步驟。
> **強制等級**：與 INV-CM-005（Session-End Hook 後置不變量）同級。未執行 RCA 即執行 Session-End Hook 構成治理違規。
> **輸出**：LESSON-xxx + 更新觸發問題的 skill（若為 MODIFY/CREATE 且無問題，仍須產出「變更動機紀錄」寫入對應 ADR 的「變更紀錄」區段）

---

## Meta-RCA 觸發器（LESSON-025 左移守衛）

> **根因**: DECLARATION_IMPLEMENTATION_GAP — RCA 始終由使用者要求才執行，AI 未自主觸發
> **ADR**: ADR-GOV-022

**自檢規則**：在執行 RCA 時，先回答以下問題：

1. **本次 RCA 是 AI 自主觸發的，還是使用者要求的？**
   - 若使用者要求 → 本身就是 GOVERNANCE_BYPASS，必須追加一條 LESSON 記錄「為什麼 AI 沒有自主觸發」
   - 若 AI 自主觸發 → 正常流程

2. **本次 RCA 窮舉了本對話中所有問題嗎？**
   - 若未窮舉 → SCAN_INCOMPLETENESS，必須先窮舉再逐一 RCA
   - 窮舉方法：回顧本 session 每一次工具呼叫和回應，識別所有偏離協議的點

3. **每個 LESSON 是否有對應的 skill 檔案實際修改？**
   - 若 LESSON 宣稱「守衛已存在」但守衛明顯失敗 → GUARD_STRENGTHENING，不是 NEW_LESSON
   - 禁止宣稱「Step 12 會攔截」— 如果 Step 12 沒有攔截到，它就不是有效守衛

## 窮舉式 Session 掃描協議

在 Step 12 執行 RCA 前，強制執行：

```
SESSION-SWEEP:
  FOR each tool_call IN session_history:
    IF tool_call.type IN [write_to_file, replace_file_content, multi_replace_file_content]:
      CHECK: was CM-GATE declared before this call?
      CHECK: was the write tracked in session_changes?
    IF tool_call.result contains error or retry:
      RECORD: potential LESSON candidate
    IF user_message contains correction or dissatisfaction:
      RECORD: governance gap → mandatory LESSON
```

## Step 1: 根因分類

對當前變更進行分類（所有變更類型皆適用）：

| 分類 | 觸發條件 |
|------|----------|
| FORMAT_ERROR | 涉及格式/語法 |
| COVERAGE_GAP | 覆蓋宣稱 vs 實際不符 |
| LLM_HALLUCINATION | LLM 輸出不一致 |
| PROCESS_GAP | 缺少流程步驟 |
| SEMANTIC_DRIFT | 上下游語意不匹配 |
| NAMING_INCONSISTENCY | 命名規則例外 |
| GOVERNANCE_BYPASS | 跳過治理步驟 |
| SCAN_INCOMPLETENESS | 掃描/審計不完整 |
| DECLARATION_IMPLEMENTATION_GAP | 宣告規則無對應強制機制 |
| NEW_CAPABILITY | CREATE 且無先前缺口（仍須記錄動機） |
| IMPROVEMENT | MODIFY 改善既有（仍須記錄「為什麼原先不完整」） |

## Step 1.5: LESSON 重用檢查（FR-023）

1. 查追溯矩陣「LESSON → Skill 守衛映射」段落，篩選相同根因分類的 LESSON
2. 若找到匹配 → 載入對應 ADR（透過矩陣的 ADR 來源欄位定位）→ `mode = GUARD_STRENGTHENING`
3. 若未找到 → `mode = NEW_LESSON`

> 框架變更：查 `$FRAMEWORK_ROOT/docs/traceability-matrix.md`
> 專案變更：查 `{target_repo}/docs/traceability-matrix.md`

## Step 2: 根因鑽取（5 Whys）

1. Why 1: 為什麼這個錯誤出現？
2. Why 2: 為什麼沒有被阻止？
3. Why 3: 為什麼驗證沒有偵測到？
4. Why 4: 為什麼流程允許它通過？
5. Why 5: 什麼結構性改變可以消除它？
6. 若 `mode == GUARD_STRENGTHENING`：Why Extra: 為什麼既有守衛沒有攔截？

## Step 3a: 因果鏈建構

從 Why 5（結構性修正）出發，建構完整因果鏈：

1. **問題發生點**（Occurrence Point）：錯誤第一次出現在哪個 Stage/Step/檔案？
2. **逃逸路徑**（Escape Path）：錯誤經過了哪些驗證點？逐一列出每個驗證點及未攔截原因。
3. **最早可偵測點**（Earliest Detection Point）：因果鏈上最上游可偵測此問題的位置。
4. **FR/NFR 對應**：查追溯矩陣「FR → Skill」映射，找出實作受影響 FR/NFR 的 Skill。

## Step 3b: 瓶頸識別（Theory of Constraints）

在因果鏈上找最有效的單一介入點：

| 優先序 | 條件 | 瓶頸 | 介入類型 |
|--------|------|------|----------|
| 1 | 最早可偵測點已有守衛但失敗 | 該守衛 | `GUARD_STRENGTHENING` |
| 2 | 最早可偵測點無守衛 | 該位置 | `NEW_GUARD` |
| 3 | 多位置同時缺守衛 | 最上游者 | `NEW_GUARD`（最大左移） |
| 4 | 成本差異大 | 成本最低 + 覆蓋最大 | 按情況判定（Ockham's Razor） |

輸出：
- `bottleneck_location`: Skill 檔案 + Step/行號
- `intervention_type`: GUARD_STRENGTHENING | NEW_GUARD | STEP_ADDITION
- `expected_coverage`: 此介入能阻擋的失敗模式列表

## Step 3c: 追溯矩陣交叉驗證

1. 確認 `bottleneck_location` 的 Skill 在追溯矩陣「FR → Skill」映射中對應了受影響的 FR
2. 若不一致 → 重新執行 Step 3a（因果鏈可能有錯）
3. 確認 `mode`（來自 Step 1.5）與 `intervention_type` 一致：
   - `mode == GUARD_STRENGTHENING` 但 `intervention_type == NEW_GUARD` → 矛盾，重新檢查
   - `mode == NEW_LESSON` 但 `intervention_type == GUARD_STRENGTHENING` → 矛盾，重新檢查

## Step 4: 設計/強化左移守衛

**使用 Step 3b 的 `bottleneck_location` 和 `intervention_type`。**

**若 GUARD_STRENGTHENING**：
1. 定位 `bottleneck_location` 的既有守衛
2. 分析原始守衛為何未攔截（對照 Step 3a 逃逸路徑）
3. 擴展守衛覆蓋範圍或收緊匹配條件
4. 記錄守衛演進歷史

**若 NEW_GUARD / STEP_ADDITION**：
1. 在 `bottleneck_location` 設計新守衛
2. 守衛類型依根因分類：
   - FORMAT_ERROR → 格式 lint 指令
   - COVERAGE_GAP → 自動化計數斷言
   - LLM_HALLUCINATION → 二次驗證 + 結構化約束
   - PROCESS_GAP → 強制步驟
   - SEMANTIC_DRIFT → 語意一致性檢查
3. 守衛必須覆蓋 `expected_coverage` 中列出的所有失敗模式

## Step 5: 更新 Skill

執行 `update_skill(source_skill, guard)`。

## Step 6: 驗證左移有效性

1. 模擬原始輸入 + 更新後的 skill
2. 斷言：原始錯誤不再出現
3. 若 `mode == GUARD_STRENGTHENING`：斷言過往 LESSON 的原始錯誤也不再出現

## Step 7: 寫入紀錄

**若 NEW_LESSON**：
- 建立 LESSON-xxx（含 id, fix_ref, category, root_cause, guard, skill_updated, timestamp）
- 寫入對應 ADR 的「根因分析與教訓」區段

**若 GUARD_STRENGTHENING**：
- 更新既有 LESSON（附加強化紀錄：trigger, why_guard_failed, guard_before, guard_after, timestamp）
- 寫入對應 ADR 的「根因分析與教訓」區段

---

## LESSON-xxx 格式

```
### LESSON-xxx

- **變更來源**: ADR-{CAT}-xxx 變更 #N
- **變更類型**: CREATE | MODIFY | FIX
- **根因分類**: [category]
- **5 Whys 結果**: [why_5]
- **變更動機**: [為什麼需要這個變更？原先缺了什麼？]
- **瓶頸識別**:
  - 問題發生點: [Stage/Step/檔案]
  - 逃逸路徑: [驗證點1 → 未攔截原因; 驗證點2 → 未攔截原因]
  - 最早可偵測點: [位置]
  - 瓶頸位置: [Skill 檔案 + Step/行號]
  - 介入類型: GUARD_STRENGTHENING | NEW_GUARD | STEP_ADDITION
  - 預期覆蓋: [此介入能阻擋的失敗模式]
- **左移守衛**: [guard description]
- **守衛驗證證據**: [guard_name] 能攔截 [scenario] 的證據（grep 結果/測試輸出/步驟引用）
- **更新的 Skill**: [skill file path]
- **驗證**: 模擬原始輸入，確認問題不再出現
```
