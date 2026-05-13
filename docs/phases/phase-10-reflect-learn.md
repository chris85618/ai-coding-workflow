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

## 10.2 技術債登記冊更新

執行 `docs/governance/TECH-DEBT.md` 定義的流程：
- 從 SonarCloud 報告、測試覆蓋缺口、架構審查中收集新 DEBT-xxx
- RICE 優先排序
- 四象限分類
- Sprint 債務容量規劃（20% 容量）
- 更新 `docs/tech-debt-register.md`

## 10.3 知識圖譜更新（Understand Anything）

```
/understand
```

Sprint 結束後執行增量更新。Path A 專案此為首次建立知識圖譜。

## 10.4 持續學習（ECC）

```
/instinct-status    # 查看學到的 instincts
/evolve             # 將 instincts 聚類為新 skill
/instinct-export    # 匯出分享
```

## 10.5 操作經驗記錄（gstack）

```
/learn              # 查看、搜尋、修剪學習記錄
```

## 10.6 追溯矩陣歸檔

```
archive:
  snapshot_traceability_matrix() → docs/archive/
  snapshot_impact_log() → docs/archive/
  snapshot_tech_debt_register() → docs/archive/
  generate_sprint_summary() → docs/archive/
```

## 10.7 跨機器同步（可選）

```
gstack-brain-sync       # 同步 artifacts 到私有 Git repo
/sync-gbrain            # 重新索引程式碼到 GBrain
```
