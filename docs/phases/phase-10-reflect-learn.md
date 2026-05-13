# Phase 10：反思 & 學習

> **三個工具共同參與**，確保知識和經驗得到保存。

---

## 10.1 Retrospective（gstack）

```
/retro
```

- 工作分析、Shipping 記錄、測試健康趨勢、成長機會

```
/retro global    # 跨專案全域 retro
```

## 10.2 全對話 RCA 掃描 + 左移

> **為什麼需要**：Stage 3-8 的 root-cause-leftshift 已對所有變更類型觸發（CREATE/MODIFY/FIX）。
> 但對話中可能有未觸發變更的隱性問題：人類修正了 AI 方向、AI 自主回退了某個嘗試、
> 微妙的溝通不一致未達到變更門檻。這些都是流程改善的素材，Phase 10 是最後的安全網。

### 執行協議

```
conversation_rca_sweep():
  # Step 1: 掃描全部對話紀錄（去重：排除已處理）
  existing_lessons = read("docs/change-log.md").filter(LESSON-xxx)
  FOR each conversation_segment IN current_sprint:
    IF segment already covered by existing_lessons:
      SKIP  # CHANGE-MANAGEMENT Step 4 已處理，不重複
    ELSE:
      scan_for:
      - 人類修正 AI 方向的瞬間（user override）
      - AI 自主回退的嘗試（abandoned approaches）
      - 反覆迭代超過 2 輪才解決的問題（friction points）
      - 人類問了澄清性問題（indication of ambiguity）
      - ESCALATION 事件（AI 能力邊界）

  # Step 2: 對每個發現執行 RCA
  FOR each finding:
    category = classify():
      PROMPT_AMBIGUITY     → skill/prompt 不夠明確
      CONTEXT_LOSS         → 重要上下文在迭代中丟失
      PROCESS_GAP          → 流程缺漏（應有步驟未執行）
      TOOL_LIMITATION      → 工具能力不足
      DOMAIN_KNOWLEDGE_GAP → 領域知識不足

    root = five_whys(finding)

  # Step 3: 左移守衛設計
  FOR each rca_result:
    guard = design_guard(category, root):
      IF PROMPT_AMBIGUITY   → 更新對應 skill 的 prompt 明確性
      IF CONTEXT_LOSS       → 強化 iteration-log.md 的記錄要求
      IF PROCESS_GAP        → 更新對應 Stage/Phase 文件加入缺漏步驟
      IF TOOL_LIMITATION    → 記錄為 DEBT-xxx（工具改善）
      IF DOMAIN_KNOWLEDGE_GAP → 記錄至 exploration-log.md

  # Step 4: 更新 skill + 寫入 LESSON-xxx
  FOR each guard:
    update_skill(guard.target_skill, guard.content)
    persist(LESSON-xxx, "docs/change-log.md")

  # Step 5: 驗證左移有效性
  FOR each updated_skill:
    simulate(original_scenario, updated_skill)
    ASSERT 原始問題不再出現
```

### 與 Stage 3-8 root-cause-leftshift 的差異

| 面向 | Stage 3-8 RCA | Phase 10 RCA |
|------|--------------|--------------|
| 觸發 | 所有變更類型（CREATE/MODIFY/FIX） | Sprint 結束 |
| 範圍 | 單一變更 | 全部對話 |
| 目標 | 防止特定問題重現 + 記錄變更動機 | 系統性流程改善 |
| 輸出 | LESSON-xxx（per 變更） | LESSON-xxx（per pattern） |

## 10.3 技術債登記冊更新

執行 `docs/governance/TECH-DEBT.md` 定義的流程：
- 從 SonarCloud 報告、測試覆蓋缺口、架構審查中收集新 DEBT-xxx
- RICE 優先排序
- 四象限分類
- Sprint 債務容量規劃（20% 容量）
- 更新 `docs/tech-debt-register.md`

## 10.4 知識圖譜更新（Understand Anything）

```
/understand
```

Sprint 結束後執行增量更新。Path A 專案此為首次建立知識圖譜。

## 10.5 持續學習（ECC）

```
/instinct-status    # 查看學到的 instincts
/evolve             # 將 instincts 聚類為新 skill
/instinct-export    # 匯出分享
```

## 10.6 操作經驗記錄（gstack）

```
/learn              # 查看、搜尋、修剪學習記錄
```

## 10.7 追溯矩陣歸檔

```
archive:
  snapshot_traceability_matrix() → docs/archive/
  snapshot_impact_log() → docs/archive/
  snapshot_tech_debt_register() → docs/archive/
  snapshot_iteration_log() → docs/archive/
  generate_sprint_summary() → docs/archive/
```

## 10.8 工作流狀態重置

```
reset_workflow_state():
  archive("docs/workflow-state.md") → docs/archive/
  create_fresh("docs/workflow-state.md")  # 為下個 Sprint 準備
```

## 10.9 跨機器同步（可選）

```
gstack-brain-sync       # 同步 artifacts 到私有 Git repo
/sync-gbrain            # 重新索引程式碼到 GBrain
```
