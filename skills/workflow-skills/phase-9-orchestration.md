# Skill: Phase 9 Ship & Deploy 編排

> **觸發條件**：AGENTS.md Step 10
> **輸入**：Stage 8 完成、所有測試通過、安全審計 PASS
> **輸出**：部署紀錄、ADR-OPS-xxx

---

## Step 1: 預發布完成檢查

觸發 `skills/workflow-skills/completion-check.md`：
- 全部 PASS → 繼續
- 任一 FAIL → 回到 Stage 8

## Step 2: Ship

> **交付模型守衛 (LESSON-044)**：
> 確認專案當前的交付規範。對於快速迭代專案，`branch push` (如直接 push 至特定 branch) 即視為完成初版交付，此時不需要建立 local/remote Git Tag，Tag 僅保留給 formal release 階段使用。

```
/ship                          # gstack: lint → test → build → PR → deploy
```

- PR 標題需包含 BG-xxx 參照
- PR body 需包含追溯矩陣摘要

## Step 3: 部署

```
/land-and-deploy               # gstack: merge → 觸發 CI/CD
```

## Step 4: Canary 監控

```
/canary https://your-url.com   # gstack: 即時健康檢查
```

- 監控成功率、延遲、錯誤率
- 發現問題 → 回滾 → 回到 Stage 8 調查

## Step 5: 文件更新

```
/document-release              # gstack: changelog, API docs, README
```

## Step 6: 產出

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 部署紀錄 | — | `docs/deployment-log.md` |
| 營運決策 | `ADR-OPS-xxx` | `docs/adr/ADR-OPS-xxx.md` |
| Changelog | — | `CHANGELOG.md` |
