# Skill: 追溯系統規格

> **觸發條件**：所有 Stage/Phase，作為追溯矩陣的參照規格
> **用途**：定義 ID 系統、追溯鏈規則、連結類型、語意一致性判定
> **被引用者**：micro-validation.md、iter-loop.md、completion-check.md、impact-analysis-exec.md

---

## Step 1: ID 前綴規格表

| 前綴 | 領域 | 指派階段 | 上游 | 下游 |
|------|------|---------|------|------|
| `BG-xxx` | 商業目標 | Phase 2.0 | — | FEA, FR |
| `S-xxx` | 利害關係人 | Phase 2.1 | BG | FEA |
| `FEA-xxx` | 功能特性（範圍） | Phase 2.2 | BG, S | FR, NFR |
| `FR-xxx` | 功能需求 | Stage 3 | FEA | UC, ADR |
| `NFR-xxx` | 非功能需求 | Stage 3 | FEA | UC, ALG |
| `UC-xxx` | 使用案例 | Stage 3 | FR | SC, CLS |
| `ADR-STR-xxx` | 架構決策（結構類） | Stage 3 | FR | CLS, INV |
| `ADR-GOV-xxx` | 治理決策 | 任意 | FR, NFR | — |
| `ADR-SEC-xxx` | 安全決策 | Stage 5/8 | FR | CLS |
| `ADR-SCP-xxx` | 範圍決策 | Phase 2 | BG, S, FEA | — |
| `ADR-GATE-xxx` | 閘門決策 | 任意 Stage | 任意 | — |
| `ADR-OPS-xxx` | 營運決策 | Phase 9 | FR | — |
| `ALG-xxx` | 演算法規格 | Stage 4 | NFR, UC | CLS, INV |
| `CLS-xxx` | 類別/聚合 | Stage 5 | UC, ALG | INV, EVT |
| `EVT-xxx` | 領域事件 | Stage 5 | CLS | SC, TC |
| `INV-xxx` | 不變量 | Stage 6 | CLS, ALG | SC, TC |
| `SC-xxx` | BDD 場景 | Stage 7 | UC, INV | TC |
| `TC-xxx` | 測試案例 | Stage 7/8 | SC, INV | — |
| `DEBT-xxx` | 技術債項目 | Phase 10 | 任意 | ADR |
| `RISK-xxx` | 風險 | 任意階段 | 任意 | ADR |
| `LESSON-xxx` | 教訓紀錄 | 任意 | 任意 | skill |

## Step 2: 雙向追溯鏈

### 正向追溯（需求 → 測試）
```
BG-xxx → FEA-xxx → FR-xxx → UC-xxx → SC-xxx → TC-xxx
                  → NFR-xxx → ALG-xxx ─────┘
```

### 反向追溯（測試 → 需求）
```
TC-xxx → SC-xxx → UC-xxx → FR-xxx → FEA-xxx → BG-xxx
                          → NFR-xxx → FEA-xxx → BG-xxx
```

### 設計追溯（橫向）
```
UC-xxx → CLS-xxx → EVT-xxx
       → ADR-STR-xxx
ALG-xxx → CLS-xxx → INV-xxx
```

### 全方向連結追溯（FR-022）
```
任意變更 ID → 全方向走訪：
  ↓ 縱向下游（derives/decomposes/realizes/validates）
  ↑ 縱向上游（反向追溯）
  ↔ 橫向（justifies/constrains/mitigates/formalizes/emitted-by）
  ↺ LESSON 守衛（guards）
```

## Step 3: 連結類型定義

| 類型 | 說明 | 範例 |
|------|------|------|
| `derives` | 上游衍生出下游 | BG-001 derives FEA-001 |
| `decomposes` | 上游分解為下游 | FEA-001 decomposes FR-001 |
| `realizes` | 下游實現上游 | UC-001 realizes FR-001 |
| `validates` | 下游驗證上游 | TC-001 validates SC-001 |
| `constrains` | 上游約束下游 | NFR-001 constrains ALG-001 |
| `decides` | 決策影響設計 | ADR-STR-001 decides CLS-001 |
| `mitigates` | 下游緩解上游風險 | TC-005 mitigates RISK-001 |
| `justifies` | ADR 證成 FR/NFR | ADR-GOV-001 justifies FR-001 |
| `formalizes` | 下游形式化上游 | INV-001 formalizes CLS-001 |
| `emitted-by` | 事件由上游發射 | EVT-001 emitted-by CLS-001 |
| `guards` | LESSON 守衛 skill | LESSON-001 guards s2c-*.md |

## Step 4: 語意一致性判定規則

1. **方向一致**：下游 ID 的描述必須是上游 ID 描述的具體化，而非偏離
2. **範圍收斂**：每一層向下追溯，範圍必須等於或小於上游
3. **意圖保留**：修改任何 ID 後，其原始商業意圖（BG-xxx）仍可從追溯鏈推導
4. **無矛盾**：同一追溯鏈上的任意兩個 ID 不得互相矛盾
5. **完備覆蓋**：上游 ID 的所有子面向應被下游 ID 集合完全覆蓋

## Step 5: Stage 出口閘門追溯驗證（每個 Stage 強制）

```
- [ ] 本 Stage 產出的所有 ID 皆已指派且格式正確
- [ ] 正向追溯：所有 ID 皆有至少一條下游連結（終端 ID 除外）
- [ ] 反向追溯：所有 ID 皆有至少一條上游連結（源頭 ID 除外）
- [ ] 零孤兒：無任何 ID 缺少上下游連結
- [ ] 語意一致性：所有追溯鏈的語意方向一致，無漂移
- [ ] 跨 Stage 連結：本 Stage 輸入 ID 皆可追溯至前一 Stage 輸出 ID
- [ ] 影響分析：所有修改過的已核准產出物皆已完成影響分析
- [ ] 全方向追溯（FR-022）：所有變更已驗證 ADR/NFR/RISK/LESSON 連結
- [ ] LESSON 重用（FR-023）：所有變更已檢查過往 LESSON 是否可重用
- [ ] 追溯矩陣文件已更新並寫入 docs/
```

## Step 6: 追溯矩陣文件格式

```markdown
# Traceability Matrix - [專案名稱]

**Generated**: [ISO 8601 timestamp]
**Last Validated**: [ISO 8601 timestamp]

## 正向追溯矩陣

| 源 ID | 目標 ID | 連結類型 | 語意一致 | 最後驗證 |
|-------|---------|---------|---------|---------| 

## 反向追溯矩陣

| 源 ID | 追溯至 | 連結類型 | 語意一致 | 最後驗證 |
|-------|-------|---------|---------|---------| 

## 孤兒報告

| ID | 缺少 | 狀態 | 備註 |
|----|------|------|------|

## 語意漂移報告

| ID | 原始語意 | 當前語意 | 漂移程度 | 修復動作 |
|----|---------|---------|---------|---------| 
```
