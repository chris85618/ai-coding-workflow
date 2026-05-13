# Skill: 影響分析執行

> **觸發條件**：任何修改（由 micro-validation.md Step 6 觸發，或獨立觸發）
> **輸入**：變更 ID、變更內容
> **輸出**：ADR 變更紀錄、嚴重度分類、受影響 ID 清單

---

## Step 1: 識別變更

1. 記錄變更 ID + 變更前/後內容
2. 分類：新增 / 修改 / 刪除
3. 記錄時間戳和觸發 Stage

## Step 2: 正向影響追溯

1. 沿正向追溯鏈遞迴展開至末端
2. 標記每個下游 ID 為「可能受影響」

## Step 3: 反向影響追溯

1. 沿反向追溯鏈檢查上游 ID 語意一致性
2. 標記不一致的上游 ID

## Step 4: 爆炸半徑計算

1. `blast_radius` = count(affected_downstream) + count(inconsistent_upstream)
2. `cross_stage_impact` = 受影響 ID 橫跨幾個 Stage

## Step 5: 嚴重度分類

| 等級 | 條件 | 處理方式 |
|------|------|----------|
| COSMETIC | blast_radius = 0 | 記錄至 ADR 變更紀錄，繼續 |
| MINOR | 1-3, 同 Stage | 自主更新 + 微驗證 + 記錄 |
| MODERATE | 4-10 或跨 1 Stage | 自主更新 + 重新驗證出口閘門 + 記錄 |
| MAJOR | >10 或跨 2+ Stage | 暫停 → 影響報告 → 上報 HITL → 核准後更新 |

## Step 6: 產出變更紀錄

1. 寫入對應 ADR 的「變更紀錄」區段
2. 更新追溯矩陣
