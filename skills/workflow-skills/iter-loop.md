# Skill: 雙 Agent 迭代迴圈

> **觸發條件**：Stage 3-8 的每一輪迭代
> **輸入**：該 Stage 的審查維度表、前輪產出物
> **輸出**：改善後的產出物（已通過微驗證、已達 AI 不動點）
> **核心原則**：AI 自主持續迭代直至達不動點，**然後**才彙整全貌交給人類。人類不在每一輪迭代中介入，僅在 AI 收斂後做最終判定。

---

## Step 1: Agent α — 破綻發掘

1. 載入該 Stage 的審查維度表
2. 逐維度對當前產出物進行窮盡式批判
3. 對每個發現標注：
   - 嚴重度：CRITICAL / HIGH / MEDIUM / LOW / YAGNI
   - 影響範圍：哪些 ID 受影響
   - 建議方向（不是解法，是方向）
4. 產出：問題清單（按嚴重度降序排列）
5. 寫入 `docs/iteration-log.md`

## Step 2: Agent β — 收斂整合

對 Agent α 的每個問題，依序執行決策流：

1. 分類：是 bug / 設計缺陷 / 遺漏 / 風格 / YAGNI？
2. 奧卡姆剃刀：最簡方案是什麼？（強制剃除過度設計）
3. 前提窮盡：修復前提是否完整？是否有隱含假設？
4. 併吞分析：此修復能否順便解決其他問題？
5. 循環依賴破解：修復是否引入新的循環？
6. 邊界內化：修復後的系統邊界是否更清晰？

產出：完整自包含改善文件（不引用外部內容）。寫入 `docs/iteration-log.md`。

## Step 3: 微驗證迴圈

1. 觸發 `skills/workflow-skills/micro-validation.md`（完整 Step 0-7 + 5.5/5.7）
2. 觸發 `skills/workflow-skills/impact-analysis-exec.md`
3. 執行 ADG（假設依賴圖）檢查：確認無 CONFLICTS_WITH 矛盾
4. 執行 PAG（門控思維鏈）：確保步驟執行皆有驗證證明
5. 全數通過 → 進入 Step 4
6. 任一失敗 → 自主修復 → 重新執行本 Step
7. 修復 3 次仍失敗 → 上報至 HITL（ESCALATION 類型）

## Step 4: 不動點判定

依以下規則判定收斂狀態：

- **REACHED**：Agent α 本輪所有發現的嚴重度皆為 YAGNI → 進入 Step 5
- **DIVERGING**：本輪 CRITICAL + HIGH 數量 ≥ 前輪 → 停止自主迭代 → 進入 Step 5（需人類方向指引）
- **NOT_REACHED**：仍有非 YAGNI 發現但趨勢收斂 → 更新 `docs/iteration-log.md` + `docs/workflow-state.md` (iteration round++) → 回到 Step 1

## Step 5: HITL 收斂確認

呈現完整收斂報告：
- 總迭代輪次
- 每輪 Agent α 的嚴重度分佈趨勢
- 最終殘餘問題（僅 YAGNI 級，或發散原因）
- 產出物完整清單及追溯狀態
- 建議：通過 / 需人類指引

使用者選擇：
- **[1] 加入新需求/方向後繼續** → 更新輸入 → 回到 Step 1（完整迴圈重啟）
- **[2] 通過 ✅** → 進入 Step 6

## Step 6: 出口閘門驗證

1. 執行該 Stage 的原有檢查項
2. 執行追溯矩陣驗證（見 `traceability-system.md` Step 5）
3. 執行影響分析完成確認
4. 確認所有文件已寫入 `docs/`
5. 更新 `docs/workflow-state.md`（移除已完成 leaf）
6. 全數通過 → 進入下一 Stage
7. 任一失敗 → 回到 Step 1 繼續迭代（AI 自主收斂）
