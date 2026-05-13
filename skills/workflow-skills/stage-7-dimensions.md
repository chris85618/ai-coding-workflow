# Skill: Stage 7 審查維度 + BDD/ATDD

> **觸發條件**：Stage 7（BDD/ATDD）迭代迴圈中
> **輸入**：UC-xxx (Stage 3), CLS-xxx (Stage 5), INV-xxx (Stage 6), Contract 規格
> **輸出**：SC-xxx, TC-xxx → `{target_repo}/docs/bdd-scenarios.md` + 測試檔案
> **依賴 skill**：`s2c-bdd-scenarios.md`、`iter-loop.md`

---

## Step 1: BDD 審查維度（Agent α）— 5 維

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| B1 | 場景覆蓋率 | Given/When/Then 是否覆蓋所有 Stage 4 的理論保證？ |
| B2 | 邊界場景 | 退化情境（空輸入、極值、溢位）是否被測試？ |
| B3 | 驗收標準對齊 | 每個 BDD 場景是否可追溯回 UC-xxx？ |
| B4 | 測試獨立性 | 測試之間是否有隱性依賴或順序耦合？ |
| B5 | 可讀性 | 非技術人員是否能讀懂 BDD 場景？ |

## Step 2: 形式化驗證審查維度（Agent α）— 4 維

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| V1 | Stage 6 規格覆蓋 | 每個 INV-xxx 和 Contract 是否有對應的驗證程式碼？ |
| V2 | Property-based 涵蓋 | 是否為每個啟發式設計了隨機化 property test？ |
| V3 | 反例追蹤 | 發現的反例是否被系統性追蹤並轉為回歸測試？ |
| V4 | 邊界值分析 | 參數邊界是否被 property generators 涵蓋？ |

## Step 3: S2C BDD 場景生成

觸發 `skills/workflow-skills/s2c-bdd-scenarios.md`：
- 輸入：UC-xxx, INV-xxx
- 輸出：SC-xxx → `docs/bdd-scenarios.md` + 測試檔案

## Step 4: ECC Hooks（本 Stage 開始啟動）

| Hook | 作用 |
|------|------|
| `pre:edit-write:gateguard-fact-force` | 首次編輯測試檔案前強制先調查 |
| `post:quality-gate` | 每次檔案編輯後品質檢查 |
| `post:edit:console-warn` | console.log 警告 |
| `post:ecc-context-monitor` | Context/成本/範圍監控 |

## Step 5: 迭代協議

觸發 `iter-loop.md`，參數：
- 審查維度 = B1-B5 + V1-V4
- 追溯驗證 = SC-xxx → UC-xxx/INV-xxx, TC-xxx → SC-xxx

## Step 6: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| BDD 場景 | `SC-xxx` | `docs/bdd-scenarios.md` + 測試檔案 |
| 測試結構 | — | `docs/test-structure.md` |
| Property tests | `TC-xxx` | 測試檔案 |
| 形式化驗證程式碼 | `TC-xxx` | 測試檔案 |

## Step 7: HITL 出口閘門

### 原有檢查
- [ ] BDD 場景覆蓋所有需求與理論保證
- [ ] 形式化驗證程式碼覆蓋 Stage 6 所有 Contract
- [ ] 所有 property tests 通過

### 追溯矩陣驗證
- [ ] 所有 UC-xxx 至少有一個對應 SC-xxx
- [ ] 所有 INV-xxx 至少有一個對應 SC-xxx 或 TC-xxx
- [ ] 正向追溯完整：UC → SC → TC
- [ ] 反向追溯完整：TC → SC → UC → FR → FEA → BG
- [ ] 零孤兒 ID
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 8
