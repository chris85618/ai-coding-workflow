# Stage 7：BDD/ATDD 測試開發 → 形式化驗證開發

> **[雙 Agent 迭代]** 先寫驗收條件與測試，再寫形式化驗證程式碼。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Stage 3 | 使用案例 | UC-xxx |
| Stage 5 | 類別/聚合 | CLS-xxx |
| Stage 6 | 不變量 | INV-xxx |
| Stage 6 | Contract 規格 | — |

---

## 子步驟 7a：BDD 整合自動化測試 / ATDD 驗收測試開發

### 審查維度（Agent α）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| B1 | 場景覆蓋率 | Given/When/Then 是否覆蓋所有 Stage 4 的理論保證？ |
| B2 | 邊界場景 | 退化情境（空輸入、極值、溢位）是否被測試？ |
| B3 | 驗收標準對齊 | 每個 BDD 場景是否可追溯回 Stage 3 的需求（UC-xxx）？ |
| B4 | 測試獨立性 | 測試之間是否有隱性依賴或順序耦合？ |
| B5 | 可讀性 | 非技術人員是否能讀懂 BDD 場景？ |

### S2C 增強輸入

> 由 `skills/workflow-skills/s2c-bdd-scenarios.md` 技能執行。
> 輸入：UC-xxx, INV-xxx。輸出：SC-xxx → `docs/bdd-scenarios.md` + 測試檔案。

- **BDD 場景生成**：每個 UC-xxx 生成 happy path / alternative / exception / boundary 場景 → SC-xxx，格式化為 Given/When/Then，連結至 UC-xxx 和 INV-xxx
- **測試結構**：bdd/ → SC-xxx（本 Stage）、property/ → SC-xxx（本 Stage）、unit/integration/e2e/ → TC-xxx（Stage 8）

---

## 子步驟 7b：形式化驗證開發

### 審查維度（Agent α）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| V1 | Stage 6 規格覆蓋 | 每個 INV-xxx 和 Contract 是否有對應的驗證程式碼？ |
| V2 | Property-based 涵蓋 | 是否為每個啟發式設計了隨機化 property test？ |
| V3 | 反例追蹤 | 發現的反例是否被系統性追蹤並轉為回歸測試？ |
| V4 | 邊界值分析 | 參數邊界是否被 property generators 涵蓋？ |

---

## 自動保障（ECC Hooks 在此 Stage 開始啟動）

| Hook | 作用 |
|------|------|
| `pre:edit-write:gateguard-fact-force` | 首次編輯測試檔案前強制先調查 |
| `post:quality-gate` | 每次檔案編輯後品質檢查 |
| `post:edit:console-warn` | console.log 警告 |
| `post:ecc-context-monitor` | Context/成本/範圍監控 |

---

## 迭代協議

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 B1-B5 + V1-V4 維度                     │
│  → 驗證 SC-xxx 覆蓋所有 UC-xxx 和 INV-xxx    │
│  → 產出：問題清單 + 方向建議                 │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → BDD 場景收斂 + Property test 設計         │
│  → 產出：完整測試套件                        │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈                          │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → SC-xxx 追溯至 UC-xxx 和/或 INV-xxx        │
│  → TC-xxx 追溯至 SC-xxx                      │
│  → 全數通過才進入 Step C                     │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 迭代閘門                    │
│  → [1] 繼續迭代  [2] 加入新需求              │
│  → [3] 通過 ✅ → 出口閘門驗證               │
└──────────────────────────────────────────────┘
```

---

## 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| BDD 場景 | `SC-xxx` | `docs/bdd-scenarios.md` + 測試檔案 |
| 測試結構 | — | `docs/test-structure.md` |
| Property tests | `TC-xxx` | 測試檔案 |
| 形式化驗證程式碼 | `TC-xxx` | 測試檔案 |

---

## HITL 出口閘門

### 原有檢查
- [ ] BDD 場景覆蓋所有需求與理論保證
- [ ] 形式化驗證程式碼覆蓋 Stage 6 所有 Contract
- [ ] 所有 property tests 通過（或反例已轉為 issue）

### 追溯矩陣驗證
- [ ] 所有 UC-xxx 至少有一個對應 SC-xxx
- [ ] 所有 INV-xxx 至少有一個對應 SC-xxx 或 TC-xxx
- [ ] 所有 SC-xxx 可追溯至 UC-xxx 和/或 INV-xxx
- [ ] 正向追溯完整：UC → SC → TC
- [ ] 反向追溯完整：TC → SC → UC → FR → FEA → BG
- [ ] 零孤兒 ID
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 8
