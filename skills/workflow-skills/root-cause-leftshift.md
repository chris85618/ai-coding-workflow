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

  # Step 1.5: LESSON 重用檢查（FR-023）
  existing_lessons = search("docs/change-log.md", LESSON-xxx)
  matching = [L for L in existing_lessons
              if L.category == category
              AND L.root_cause_pattern ~= fix_record.pattern]

  IF matching is not empty:
    # 過去已處理過相同根因 → 左移守衛不足
    prior = matching[0]  # 最近的匹配 LESSON
    mode = GUARD_STRENGTHENING
    target_guard = prior.guard
    target_skill = prior.skill_updated
    # 不建立新 LESSON，強化既有守衛
  ELSE:
    mode = NEW_LESSON
    # 標準 RCA 流程

  # Step 2: 根因鑽取（5 Whys）
  root = five_whys(fix_record):
    why_1: 為什麼這個錯誤出現？
    why_2: 為什麼沒有被阻止？
    why_3: 為什麼驗證沒有偵測到？
    why_4: 為什麼流程允許它通過？
    why_5: 什麼結構性改變可以消除它？
    IF mode == GUARD_STRENGTHENING:
      why_extra: 為什麼既有守衛（{target_guard}）沒有攔截？

  # Step 3: 定位觸發錯誤的 skill/prompt
  IF mode == GUARD_STRENGTHENING:
    source_skill = target_skill  # 直接定位到有缺陷的守衛
  ELSE:
    source_skill = trace_back(fix_record.file, fix_record.stage)

  # Step 4: 設計/強化左移守衛
  IF mode == GUARD_STRENGTHENING:
    guard = strengthen_guard(target_guard, root):
      → 分析原始守衛為何未攔截
      → 擴展守衛覆蓋範圍或收緊匹配條件
      → 記錄守衛演進歷史
  ELSE:
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
    IF mode == GUARD_STRENGTHENING:
      ASSERT 過往 LESSON 的原始錯誤也不再出現

  # Step 7: 寫入紀錄
  IF mode == NEW_LESSON:
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
  ELSE:  # GUARD_STRENGTHENING
    update_lesson(prior.id):
      append_strengthening_record(
        trigger = fix_record.id,
        why_guard_failed = root.why_extra,
        guard_before = target_guard,
        guard_after = guard,
        timestamp = now()
      )
    persist(update, "docs/change-log.md")
```

---

## LESSON-xxx 格式

```
### LESSON-xxx

- **FIX 來源**: IMP-xxx
- **根因分類**: [category]
- **5 Whys 結果**: [why_5]
- **左移守衛**: [guard description]
- **守衛驗證證據**: [guard_name] 能攔截 [scenario] 的證據（grep 結果/測試輸出/步驟引用）
- **更新的 Skill**: [skill file path]
- **驗證**: 模擬原始輸入，確認錯誤不再出現
```
