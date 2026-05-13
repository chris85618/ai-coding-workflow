# Stage 6：形式化驗證設計

> **[雙 Agent 迭代]** 為關鍵元件設計形式化驗證規格。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Stage 4 | 演算法規格 | ALG-xxx |
| Stage 5 | 類別/聚合 | CLS-xxx |
| Stage 5 | 領域事件 | EVT-xxx |

---

## 審查維度（Agent α）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| F1 | 不變量完備性 | 是否窮盡所有系統不變量？遺漏了哪些？ |
| F2 | 前置/後置條件 | 每個公開方法的 contract 是否嚴謹？ |
| F3 | 狀態機正確性 | 狀態轉移是否窮盡？不可能的狀態組合是否被排除？ |
| F4 | 活性與終止性 | 是否保證進度（liveness）？迴圈是否終止？ |
| F5 | 並行安全 | 共享資源是否有 data race？鎖序是否一致（deadlock-free）？ |
| F6 | 型別安全 | 是否可用型別系統編碼更多不變量（Phantom Types, Newtype）？ |

### Agent β 收斂心法

- 驗證規格必須**可執行**（Property-based testing 或 Model checking 可用）
- 優先使用**型別系統編碼**不變量（compile-time > runtime）
- 形式化規格不得引入實作細節

---

## 迭代協議

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 F1-F6 維度，窮盡式批判                 │
│  → 產出：問題清單 + 方向建議                 │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → 可執行驗證規格收斂                        │
│  → 產出：不變量 + Contract + 狀態機          │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈                          │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → INV-xxx 追溯至 CLS-xxx/ALG-xxx            │
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
| 不變量總表 | `INV-xxx` | `docs/invariants.md` |
| Contract 規格 | — | `docs/contracts.md` |
| 狀態機圖 | — | `docs/state-machines.md` |
| 驗證策略 | — | `docs/verification-strategy.md` |

---

## HITL 出口閘門

### 原有檢查
- [ ] 不變量覆蓋所有關鍵路徑
- [ ] Contract 規格可直接轉為測試
- [ ] 並行安全問題已系統性處理

### 追溯矩陣驗證
- [ ] 所有 INV-xxx 可追溯至 CLS-xxx 和/或 ALG-xxx
- [ ] 正向追溯：INV-xxx → SC-xxx → TC-xxx
- [ ] 反向追溯：INV-xxx → CLS-xxx → UC-xxx → FR-xxx → BG-xxx
- [ ] 零孤兒 ID
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 7
