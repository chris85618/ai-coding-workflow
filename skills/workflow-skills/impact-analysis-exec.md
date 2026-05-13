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

## Step 3.5: 全方向連結追溯（FR-022）

1. 從變更 ID 查找所有 `justifies` / `constrains` 關係的 ADR
2. 從變更 ID 查找所有 `constrains` 關係的 NFR
3. 從變更 ID 查找所有 `mitigates` 關係的 RISK
4. 從變更 ID 查找所有 `formalizes` / `emitted-by` / `guards` 關係
5. 對每個受影響 ID → 讀取完整文件 → 驗證語意一致性
6. ADR 不再成立 → 標記 SUPERSEDED → 寫入對應 ADR
7. NFR 被違反 → 嚴重度自動升至 MAJOR

## Step 4: 爆炸半徑計算

1. `blast_radius` = count(affected_downstream) + count(inconsistent_upstream) + count(affected_lateral_ids)
2. `cross_stage_impact` = 受影響 ID 橫跨幾個 Stage

## Step 5: 嚴重度分類

| 等級 | 條件 | 處理方式 |
|------|------|----------|
| COSMETIC | blast_radius = 0 | 記錄至 ADR 變更紀錄，繼續 |
| MINOR | 1-3, 同 Stage | 自主更新 + 微驗證 + 記錄 |
| MODERATE | 4-10 或跨 1 Stage | 自主更新 + 重新驗證出口閘門 + 記錄 |
| MAJOR | >10 或跨 2+ Stage | 暫停 → 執行 M1-M4 → 上報 HITL |

### MAJOR 影響處理（M1-M4）

**M1 全貌映射**：
- 繪製完整影響圖（文字 ASCII 或 Mermaid）
- 列出所有受影響 ID 和文件

**M2 自主修正**：
- AI 自主更新所有受影響的下游 ID
- 每次更新觸發微驗證
- 更新追溯矩陣

**M3 缺口識別**：
- 識別修正後仍存在的語意缺口
- 標記需要人類決策的歧義點

**M4 HITL 確認**：
- 呈現影響報告：全貌映射 + 已修正 + 殘餘缺口
- 使用者核准 → 繼續
- 使用者拒絕 → 回到 M2 修正

## Step 6: 產出變更紀錄

1. 寫入對應 ADR 的「變更紀錄」區段
2. 更新追溯矩陣

---

## 禁止行為

1. **禁止部分追溯**：必須遞迴展開至末端，不得中途停止
2. **禁止假設無影響**：blast_radius 必須從實際遍歷計算，不得假設
3. **禁止跳過 MAJOR 處理**：MAJOR 影響必須執行 M1-M4，不得降級處理
4. **禁止拆分規避**：不得將一次 MAJOR 變更拆分為多次 MINOR 變更以規避

## 工具整合

| 工具 | 用途 |
|------|------|
| grep/ripgrep | ID 全域搜尋 |
| `traceability-system.md` | ID 關係定義和連結類型參照 |
| `micro-validation.md` | 更新後驗證 |
| `exhaustive-search.md` | 殘留引用掃描 |
