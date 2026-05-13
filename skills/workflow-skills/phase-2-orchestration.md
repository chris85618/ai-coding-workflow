# Skill: Phase 2 專案分析編排

> **觸發條件**：AGENTS.md Step 3
> **輸入**：使用者描述、專案目錄、知識圖譜（Path B）
> **輸出**：BG-xxx, S-xxx, FEA-xxx → `{target_repo}/docs/`
> **子 skill**：`s2c-charter.md` → `s2c-stakeholder.md` → `s2c-scope-redteam.md`

---

## Step 1: Phase 2.0 — 專案章程

觸發 `skills/workflow-skills/s2c-charter.md`：
- 輸入：專案目錄、使用者描述
- 輸出：BG-xxx → `docs/project-charter.md`

## Step 2: Phase 2.1 — 利害關係人分析

```
/office-hours                   # gstack 產品腦力激盪
```

觸發 `skills/workflow-skills/s2c-stakeholder.md`：
- 輸入：BG-xxx、/office-hours 產出
- 輸出：S-xxx → `docs/stakeholder-analysis.md`

## Step 3: Phase 2.2 — 範圍定義 + Red Team

觸發 `skills/workflow-skills/s2c-scope-redteam.md`：
- 輸入：BG-xxx, S-xxx
- 輸出：FEA-xxx → `docs/scope-definition.md`
- 包含 3 輪 Red Team 挑戰（HITL）

## Step 4: Phase 2.3 — 策略審查

```
/plan-ceo-review               # gstack CEO/Strategy 審查
```

- 挑戰假設、市場定位、商業模式
- 產出：策略驗證報告

## Step 5: 出口閘門（HITL）

### 原有檢查
- [ ] 專案章程已批准
- [ ] 利害關係人已識別且有溝通策略
- [ ] 範圍已明確（In-Scope / Out-of-Scope）
- [ ] Red Team 質疑已處理

### 追溯矩陣驗證
- [ ] 所有 BG-xxx 已產出
- [ ] 所有 S-xxx 可追溯至 BG-xxx
- [ ] 所有 FEA-xxx 可追溯至 BG-xxx 和/或 S-xxx
- [ ] 零孤兒 ID
- [ ] 初始追溯矩陣已建立
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 3
