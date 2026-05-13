# Skill: Phase 10 反思與學習編排

> **觸發條件**：AGENTS.md Step 11
> **輸入**：完整部署後的專案
> **輸出**：DEBT-xxx, LESSON-xxx, 知識圖譜更新
> **依賴 skill**：`tech-debt-collect.md`、`root-cause-leftshift.md`

---

## Step 1: /retro 回顧

```
/retro                         # gstack: 回顧本次開發週期
```

- 識別成功模式
- 識別改善機會

## Step 2: 全對話 RCA 掃描

> 此步驟回顧本 session 所有對話，搜尋被遺漏的改善機會。

```python
# Pseudocode
for each exchange in conversation_history:
    # 10.2.1: 識別被遺漏的 LESSON
    if contains_correction or contains_retry:
        candidate = extract_lesson_candidate(exchange)
        if not already_captured(candidate):
            classify_root_cause(candidate)
            generate_lesson(candidate)
    
    # 10.2.2: 識別可強化的守衛
    if contains_process_deviation:
        guard = identify_weakened_guard(exchange)
        strengthen_guard(guard)
    
    # 10.2.3: 識別新模式
    if contains_novel_approach:
        pattern = extract_pattern(exchange)
        if information_novelty_level(pattern) >= L2:
            record_pattern(pattern)
```

## Step 3: 技術債收集

觸發 `skills/workflow-skills/tech-debt-collect.md`。

## Step 4: 知識圖譜增量更新（Path B）

```
/understand                    # 增量更新知識圖譜
```

## Step 5: /evolve 工作流改善

```
/evolve                        # gstack: 工作流改善建議
```

- 識別瓶頸
- 建議自動化機會

## Step 6: 教訓歸檔

1. 所有 LESSON-xxx 已寫入對應 ADR
2. 所有 DEBT-xxx 已寫入 `docs/tech-debt-register.md`
3. 所有更新的 skill 已驗證有效性

## Step 7: 追溯歸檔

1. 匯出最終追溯矩陣快照
2. 歸檔至 `docs/archive/traceability-{timestamp}.md`

## Step 8: 工作流狀態重置

1. 更新 `docs/workflow-state.md`：
   - Pipeline Position = "Phase 10 Complete"
   - 所有 Gate Status = ✅
   - 清空 Pending Escalations
   - Last Updated = now()

## Step 9: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 技術債登記 | `DEBT-xxx` | `docs/tech-debt-register.md` |
| 教訓紀錄 | `LESSON-xxx` | 各 ADR 文件 |
| 知識圖譜 | — | 知識圖譜存儲 |
| 追溯矩陣歸檔 | — | `docs/archive/` |
