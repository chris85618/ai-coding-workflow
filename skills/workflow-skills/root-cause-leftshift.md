# Skill: 根因左移

> **觸發條件**：**所有變更，無例外。全面強制執行。**
> **禁止 N/A 判定**：AI 不得以「非 FIX」「本次無問題」「變更太小」等任何理由跳過此步驟。
> **強制等級**：與 INV-CM-005（Session-End Hook 後置不變量）同級。未執行 RCA 即執行 Session-End Hook 構成治理違規。
> **輸出**：LESSON-xxx + 更新觸發問題的 skill（若為 MODIFY/CREATE 且無問題，仍須產出「變更動機紀錄」寫入對應 ADR 的「變更紀錄」區段）

---

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

1. 搜尋 `docs/adr/` 中各 ADR 已存在的 LESSON-xxx
2. 若有相同根因類別 + 相似模式 → `mode = GUARD_STRENGTHENING`（強化既有守衛，不建新 LESSON）
3. 若無相同根因 → `mode = NEW_LESSON`（標準 RCA 流程）

## Step 2: 根因鑽取（5 Whys）

1. Why 1: 為什麼這個錯誤出現？
2. Why 2: 為什麼沒有被阻止？
3. Why 3: 為什麼驗證沒有偵測到？
4. Why 4: 為什麼流程允許它通過？
5. Why 5: 什麼結構性改變可以消除它？
6. 若 `mode == GUARD_STRENGTHENING`：Why Extra: 為什麼既有守衛沒有攔截？

## Step 3: 定位觸發源 Skill

- 若 `mode == GUARD_STRENGTHENING` → 直接定位到有缺陷的既有守衛
- 否則 → 從 `change_record.file` 和 `change_record.stage` 反向追溯至來源 skill

## Step 4: 設計/強化左移守衛

**若 GUARD_STRENGTHENING**：
1. 分析原始守衛為何未攔截
2. 擴展守衛覆蓋範圍或收緊匹配條件
3. 記錄守衛演進歷史

**若 NEW_LESSON**：
1. FORMAT_ERROR → 在 source_skill 加入格式 lint 指令
2. COVERAGE_GAP → 在 source_skill 加入自動化計數斷言
3. LLM_HALLUCINATION → 在 source_skill 加入二次驗證 + 結構化約束
4. PROCESS_GAP → 在 stage doc 加入強制步驟
5. SEMANTIC_DRIFT → 在 micro-validation 強化 Step 4

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
- **左移守衛**: [guard description]
- **守衛驗證證據**: [guard_name] 能攔截 [scenario] 的證據（grep 結果/測試輸出/步驟引用）
- **更新的 Skill**: [skill file path]
- **驗證**: 模擬原始輸入，確認問題不再出現
```
