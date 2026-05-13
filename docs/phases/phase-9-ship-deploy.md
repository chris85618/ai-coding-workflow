# Phase 9：Ship & Deploy

> **主角：gstack**

---

## 步驟 9.1：Ship

```
/ship
```

- 同步 main branch、執行測試套件、審計覆蓋率
- Push 並開啟 PR、自動壓縮 WIP commits

### 預發布完成檢查

在 `/ship` 前強制驗證（執行 `skills/workflow-skills/completion-check.md`）：
- 每個 FR-xxx 至少有一個 TC-xxx
- 每個 UC-xxx 至少有一個 SC-xxx
- 每個 INV-xxx 至少有一個驗證
- 零孤兒 ID、零斷裂追溯鏈
- 無 CRITICAL 技術債
- SonarCloud 品質閘門通過
- 三層安全審計通過

## 步驟 9.2：Merge + Deploy

```
/land-and-deploy
```

## 步驟 9.3：Post-Deploy 監控

```
/canary
```

## 步驟 9.4：更新文件

```
/document-release
```

發布後更新追溯矩陣、歸檔影響日誌、快照技術債登記冊，寫入 `docs/`。
