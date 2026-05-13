# Traceability System Specification

> **強制等級**：所有專案、所有階段、無例外。
> 本系統為統一追溯主幹，嵌入每一個 Stage 的出口閘門與每一個微動作的自主驗證迴圈。

---

## ID 前綴規格表

| 前綴 | 領域 | 指派階段 | 範例 | 上游 | 下游 |
|------|------|---------|------|------|------|
| `BG-xxx` | 商業目標 | Phase 2.0 | BG-001: 降低庫存浪費 | — | FEA, FR |
| `S-xxx` | 利害關係人 | Phase 2.1 | S-001: 營運經理 | BG | FEA |
| `FEA-xxx` | 功能特性（範圍） | Phase 2.2 | FEA-001: 需求預測 | BG, S | FR, NFR |
| `FR-xxx` | 功能需求 | Stage 3 | FR-001: 使用者認證 | FEA | UC, ADR |
| `NFR-xxx` | 非功能需求 | Stage 3 | NFR-001: 回應時間 < 200ms | FEA | UC, ALG |
| `UC-xxx` | 使用案例 | Stage 3 | UC-001: 憑證登入 | FR | SC, CLS |
| `ADR-STR-xxx` | 架構決策（結構類） | Stage 3 | ADR-STR-001: 三層分離架構 | FR | CLS, INV |
| `ADR-GOV-xxx` | 治理決策 | 任意 | ADR-GOV-001: DU 理論+新穎性門檻 | FR, NFR | — |
| `ADR-SEC-xxx` | 安全決策 | Stage 5/8 | ADR-SEC-001: 加密選型 | FR | CLS |
| `ADR-SCP-xxx` | 範圍決策 | Phase 2 | ADR-SCP-001: 功能排除 | BG, S, FEA | — |
| `ADR-GATE-xxx` | 閘門決策 | 任意 Stage | ADR-GATE-S3-001: 通過 | 任意 | — |
| `ADR-OPS-xxx` | 營運決策 | Phase 9 | ADR-OPS-001: 部署策略 | FR | — |
| `ALG-xxx` | 演算法規格 | Stage 4 | ALG-001: LSTM 需求預測器 | NFR, UC | CLS, INV |
| `CLS-xxx` | 類別/聚合 | Stage 5 | CLS-001: UserAggregate | UC, ALG | INV, EVT |
| `EVT-xxx` | 領域事件 | Stage 5 | EVT-001: OrderPaidEvent | CLS | SC, TC |
| `INV-xxx` | 不變量 | Stage 6 | INV-001: Stock >= 0 | CLS, ALG | SC, TC |
| `SC-xxx` | BDD 場景 | Stage 7 | SC-001: 登入成功路徑 | UC, INV | TC |
| `TC-xxx` | 測試案例 | Stage 7/8 | TC-001: test_login_success | SC, INV | — |
| `DEBT-xxx` | 技術債項目 | Phase 10 | DEBT-001: 缺少錯誤處理 | 任意 | ADR |
| `RISK-xxx` | 風險 | 任意階段 | RISK-001: 第三方 API 中斷 | 任意 | ADR |

> **ADR 整合**：所有變更紀錄直接寫入對應 ADR 的「變更紀錄」區段。所有 DEBT-xxx 可追溯至產生原因 ADR。
> 完整 ADR 治理規則見 `docs/governance/ADR-GOVERNANCE.md`。

---

## 雙向追溯鏈

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

每個受影響 ID → 讀取完整文件 → 驗證語意一致性
```

---

## 左移微驗證協議

> 每完成一個最細部的小動作，必須立即執行以下驗證迴圈，直到全數通過。

### 微動作定義

「微動作」指任何產生或修改帶 ID 產出物的操作，包含但不限於：
- 新增一個 ID（例如新增 FR-015）
- 修改一個 ID 的內容（例如修改 FR-003 的描述）
- 刪除一個 ID
- 新增或修改兩個 ID 之間的追溯連結

### 每次微動作後的自主驗證迴圈

```
┌─────────────────────────────────────────────────────────┐
│  MICRO-VALIDATION LOOP（每次微動作後自動執行）           │
│  驗證迴圈（Step 0-7 + Step 5.5/5.7）                     │
│                                                         │
│  Step 0: 格式驗證 (PGVG)                                │
│  → Markdown 格式正確（backtick、表格、標題層次）        │
│  → 覆蓋斷言（輸入 ID ↔ 輸出 ID 交叉驗證）              │
│  → 計數驗證（從實際內容 grep 計數，非自我報告）          │
│  → 外來殘留掃描（inline code blocks 來源檢查）          │
│                                                         │
│  Step 1: 結構完整性檢查                                 │
│  → 新/改 ID 格式是否符合前綴規格？                      │
│  → ID 序號是否連續且無重複？                            │
│  → 自動化計數：不接受泛稱覆蓋，列出每個 N              │
│                                                         │
│  Step 2: 正向追溯檢查                                   │
│  → 該 ID 是否有至少一條正向連結到下游？                 │
│  → （若為終端 ID 如 TC-xxx 則免除）                     │
│                                                         │
│  Step 3: 反向追溯檢查                                   │
│  → 該 ID 是否有至少一條反向連結到上游？                 │
│  → （若為源頭 ID 如 BG-xxx 則免除）                     │
│                                                         │
│  Step 4: 語意一致性檢查                                 │
│  → 該 ID 的描述是否與上游 ID 的語意相容？               │
│  → 下游 ID 的描述是否仍與該 ID 的語意相容？             │
│  → 檢測語意漂移：修改後的意圖是否偏離原始商業目標？     │
│  → 交叉覆蓋驗證：逐一比對上下游映射                    │
│                                                         │
│  Step 5: 孤兒偵測                                       │
│  → 是否存在任何 ID 無上游也無下游連結？                 │
│  → 是否存在任何斷裂的追溯鏈？                           │
│                                                         │
│  Step 5.5: 全方向連結追溯（FR-022）                     │
│  → 從變更 ID 查找所有 justifies/constrains 關係的 ADR  │
│  → 從變更 ID 查找所有 constrains 關係的 NFR             │
│  → 從變更 ID 查找所有 mitigates 關係的 RISK             │
│  → 從變更 ID 查找所有 formalizes/emitted-by 關係       │
│  → 從變更 ID 查找所有 guards 關係的 LESSON             │
│  → 對每個受影響 ID：讀取完整文件驗證語意一致         │
│  → 標記所有方向的受影響 ID                             │
│                                                         │
│  Step 5.7: LESSON 重用檢查（FR-023，所有變更類型）        │
│  → 掃描已存在的 LESSON-xxx                               │
│  → 若有相同根因類別的過往記錄：                       │
│    → 左移守衛不足，對守衛本身執行 RCA 並強化           │
│  → 若無相同根因：標準 RCA 流程                        │
│                                                         │
│  Step 6: 影響分析觸發                                   │
│  → 對修改的 ID 執行 IMPACT-ANALYSIS.md 協議             │
│  → 計算爆炸半徑（含縱向+橫向+守衛方向）                 │
│  → 標記受影響的下游 ID                                  │
│                                                         │
│  Step 7: 變更紀錄 + 根因左移（所有變更類型皆執行）      │
│  → 寫入變更紀錄至對應 ADR 的「變更紀錄」區段             │
│  → 執行 root-cause-leftshift.md（含 LESSON 重用檢查）    │
│  → 產出 LESSON-xxx 或強化既有 LESSON                    │
│  → 更新觸發問題的 skill/prompt/governance 文件          │
│                                                         │
│  Result:                                                │
│  → 全數通過 ✅ → 繼續下一個微動作                      │
│  → 任一失敗 ❌ → 自主修復 → 重新執行驗證迴圈          │
│  → 修復 3 次仍失敗 → 上報至 HITL 閘門                  │
└─────────────────────────────────────────────────────────┘
```

---

## Stage 出口閘門追溯驗證（疊加於原有閘門之上）

每個 Stage 的 HITL 出口閘門，除原有檢查項外，追加以下追溯驗證：

```
追溯矩陣出口驗證（每個 Stage 出口強制執行）：

- [ ] 本 Stage 產出的所有 ID 皆已指派且格式正確
- [ ] 正向追溯：所有 ID 皆有至少一條下游連結（終端 ID 除外）
- [ ] 反向追溯：所有 ID 皆有至少一條上游連結（源頭 ID 除外）
- [ ] 零孤兒：無任何 ID 缺少上下游連結
- [ ] 語意一致性：所有追溯鏈的語意方向一致，無漂移
- [ ] 跨 Stage 連結：本 Stage 的輸入 ID 皆可追溯至前一 Stage 的輸出 ID
- [ ] 影響分析：所有修改過的已核准產出物皆已完成影響分析
- [ ] 全方向追溯（FR-022）：所有變更已驗證 ADR/NFR/RISK/LESSON 連結
- [ ] LESSON 重用（FR-023）：所有變更已檢查過往 LESSON 是否可重用（無例外）
- [ ] 追溯矩陣文件已更新並寫入 docs/ 資料夾
```

---

## 追溯矩陣文件格式

每個專案在 `docs/` 下維護一份活文件 `traceability-matrix.md`：

```markdown
# Traceability Matrix - [專案名稱]

**Generated**: [ISO 8601 timestamp]
**Last Validated**: [ISO 8601 timestamp]
**Validation Status**: ✅ All checks passed / ❌ [N] issues

## 正向追溯矩陣

| 源 ID | 目標 ID | 連結類型 | 語意一致 | 最後驗證 |
|-------|---------|---------|---------|---------|
| BG-001 | FEA-001, FEA-003 | derives | ✅ | [timestamp] |
| FEA-001 | FR-001, FR-002, FR-003 | decomposes | ✅ | [timestamp] |
| FR-001 | UC-001, UC-002 | realizes | ✅ | [timestamp] |

## 反向追溯矩陣

| 源 ID | 追溯至 | 連結類型 | 語意一致 | 最後驗證 |
|-------|-------|---------|---------|---------|
| TC-001 | SC-001 → UC-001 → FR-001 → FEA-001 → BG-001 | full-chain | ✅ | [timestamp] |

## 孤兒報告

| ID | 缺少 | 狀態 | 備註 |
|----|------|------|------|
| （無孤兒） | — | — | — |

## 語意漂移報告

| ID | 原始語意 | 當前語意 | 漂移程度 | 修復動作 |
|----|---------|---------|---------|---------|
| （無漂移） | — | — | — | — |
```

---

## 連結類型定義

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

---

## 語意一致性判定規則

1. **方向一致**：下游 ID 的描述必須是上游 ID 描述的具體化，而非偏離
2. **範圍收斂**：每一層向下追溯，範圍必須等於或小於上游
3. **意圖保留**：修改任何 ID 後，其原始商業意圖（BG-xxx）仍可從追溯鏈推導
4. **無矛盾**：同一追溯鏈上的任意兩個 ID 不得互相矛盾
5. **完備覆蓋**：上游 ID 的所有子面向應被下游 ID 集合完全覆蓋
