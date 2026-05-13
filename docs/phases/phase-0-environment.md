# Phase 0：環境啟動

> 每次 Session 開始時自動執行。

---

## 自動觸發

| 工具 | 自動行為 | 說明 |
|------|---------|------|
| **ECC** | `SessionStart` hook | 載入前次 context、偵測 package manager、啟動觀察器 |
| **gstack** | SKILL.md Preamble | 版本檢查、session 追蹤、learnings 載入、GBrain 連接、artifacts sync |

## Step 0.1: 首次使用引導（僅首次）

gstack 首次使用會依序詢問：
1. Boil the Lake 理念介紹
2. Telemetry 偏好（community / anonymous / off）
3. Proactive 建議開關
4. CLAUDE.md 路由規則注入
5. 寫作風格選擇

> 這些引導只出現一次，之後的 session 會直接跳過。
> **必須完成 gstack 首次引導後才繼續後續步驟。**

## Step 0.2: Pipeline 完備性檢查

> 取代舊版的「是否有既有程式碼庫？」問題。
> 執行 `skills/workflow-skills/pipeline-completeness-check.md`。

**判定的不是「是否有既有 codebase」，而是「此框架是否已基於既有內容做出詳盡記錄、分析、開發」。**

```
pipeline_completeness_check() → completeness_score

├─ 100% → Pipeline 完整
│         → 檢查 workflow-state.md 的 current position
│         → 若有中斷工作 → Step 0.3（恢復協議）
│         → 若無中斷 → Phase 9 或 Phase 10（視狀態而定）
│
├─ 60-99% → Pipeline 部分完成
│           → 觸發 Step 0.3（恢復協議）從斷點繼續
│
├─ 1-59% → Pipeline 剛起步
│          → 判定 Path A/B（掃描是否有原始碼）
│          → Path B → Phase 1 → Phase 2
│          → Path A → Phase 2
│
└─ 0% → 全新專案
        → 判定 Path A/B（掃描專案目錄）
        → Path B → Phase 1 → Phase 2
        → Path A → Phase 2
```

## Step 0.3: 恢復協議（條件觸發）

> 僅在 `docs/workflow-state.md` 存在且有進行中的工作時觸發。
> 執行 `skills/workflow-skills/workflow-resume.md`。

```
1. 載入 workflow-state.md 的 Pipeline Position 和 Gate Status
2. 載入 pending escalations
3. 呈現恢復摘要給使用者
4. 使用者確認：
   [1] 從斷點繼續
   [2] 有其他指令（執行後回到工作流）
   [3] 重置工作流
```

> **為什麼需要與使用者確認**：使用者可能下了與工作流無關的 prompt，
> 不應假設每次 session 都要恢復工作流。

## 產出物

| 產出 | 說明 |
|------|------|
| Session context | 前次工作狀態還原 |
| Completeness score | Pipeline 完備度 |
| 路徑決策 | 繼續/恢復/重置/Path A/Path B |
