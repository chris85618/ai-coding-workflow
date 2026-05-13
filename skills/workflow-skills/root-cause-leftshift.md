# Root Cause Left-Shift Skill

> **觸發條件**：任何 FIX 類型變更
> **輸出**：LESSON-xxx + 更新觸發錯誤的 skill

---

## 執行流程

```
root_cause_leftshift(fix_record):
  # Step 1: 根因分類
  category = classify(fix_record):
    IF fix involves format/syntax → FORMAT_ERROR
    IF fix involves coverage claim vs actual → COVERAGE_GAP
    IF fix involves LLM output inconsistency → LLM_HALLUCINATION
    IF fix involves missing process step → PROCESS_GAP
    IF fix involves upstream/downstream mismatch → SEMANTIC_DRIFT

  # Step 2: 根因鑽取（5 Whys）
  root = five_whys(fix_record):
    why_1: 為什麼這個錯誤出現？
    why_2: 為什麼沒有被阻止？
    why_3: 為什麼驗證沒有偵測到？
    why_4: 為什麼流程允許它通過？
    why_5: 什麼結構性改變可以消除它？

  # Step 3: 定位觸發錯誤的 skill/prompt
  source_skill = trace_back(fix_record.file, fix_record.stage)

  # Step 4: 設計左移守衛
  guard = design_guard(category, root):
    IF FORMAT_ERROR → 在 source_skill 加入格式 lint 指令
    IF COVERAGE_GAP → 在 source_skill 加入自動化計數斷言
    IF LLM_HALLUCINATION → 在 source_skill 加入二次驗證 + 結構化約束
    IF PROCESS_GAP → 在 stage doc 加入強制步驟
    IF SEMANTIC_DRIFT → 在 micro-validation 強化 Step 4

  # Step 5: 更新 skill
  update_skill(source_skill, guard)

  # Step 6: 驗證左移有效性
  simulate(original_input, updated_skill):
    ASSERT 原始錯誤不再出現

  # Step 7: 寫入 LESSON-xxx
  lesson = LESSON(
    id = next_lesson_id(),
    fix_ref = fix_record.id,
    category = category,
    root_cause = root.why_5,
    guard = guard,
    skill_updated = source_skill,
    timestamp = now()
  )
  persist(lesson, "docs/change-log.md")
```

---

## LESSON-xxx 格式

```
### LESSON-xxx

- **FIX 來源**: IMP-xxx
- **根因分類**: [category]
- **5 Whys 結果**: [why_5]
- **左移守衛**: [guard description]
- **更新的 Skill**: [skill file path]
- **驗證**: 模擬原始輸入，確認錯誤不再出現
```
