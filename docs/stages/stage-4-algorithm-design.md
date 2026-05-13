# Stage 4：演算法設計 → 演算法層級安全審計

> **[雙 Agent 迭代]** 包含兩個序列子步驟，在同一個迭代迴圈中執行。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Stage 3 | 功能需求 | FR-xxx |
| Stage 3 | 非功能需求 | NFR-xxx |
| Stage 3 | 使用案例 | UC-xxx |
| Stage 3 | 架構決策 | ADR-STR-xxx |

---

## 子步驟 4a：演算法設計

### 審查維度（Agent α）— 22 維（A-V）

| 代號 | 維度 | 代號 | 維度 |
|------|------|------|------|
| A | 風險忠實度 | L | 不變量靜態檢查 |
| B | 響應延遲最佳化 | M | 分布假設稽核 |
| C | 啟發式窮舉與升級 | N | 冗餘與失效項清除 |
| D | 理論保證升級（非🅐⁺→🅐⁺） | O | Pseudo code 處理 |
| E | 錨定參數資料驅動化 | P | 統計方法升級候選 |
| F | 邊界系統性檢查 | Q | 寫死常數推導 |
| G | 循環依賴 | R | 章節結構審查 |
| H | 穩態收斂 | S | 併吞分析 |
| I | 圖靈可計算性 | T | 風險再證明 |
| J | 職責正交性 | U | 流程性事件時點 |
| K | 拆離點與耦合 | V | 典範轉移審查 |

### S2C 增強輸入

> 效能基線和模式目錄分析由外部工具提供，結果作為 Agent α/β 輸入。

- **效能基線**：每個 NFR-xxx (type=PERFORMANCE) 建立量測基線（延遲、吞吐量、資源用量），設定目標閾值 → feed Agent α 維度 B
- **模式目錄**：每個已驗證的架構模式記錄適用性和取捨 → feed Agent β 收斂

### Agent β 收斂心法

- **絕對最佳優先**：能升🅐⁺就升
- 加速技術：Minimax 下界(→🅐)、Variance Reduction(🅒→🅑)、K-FAC/Shampoo、Polyak-Ruppert Averaging
- **禁止 fallback / 條件旁路**（數學彙整除外）
- **暫禁降為🅓**
- 每張理論保證表必須加新欄位說明加速/逼近技術

---

## 子步驟 4b：演算法層級安全審計

在演算法設計達不動點後，於同一迭代迴圈內執行安全審計：

```bash
# SkillFortify 供應鏈掃描（若演算法引入外部依賴）
skillfortify scan . --severity-threshold high
skillfortify trust <algorithm-module>
```

| 審計維度 | 檢查項 |
|---------|--------|
| 數值安全 | 溢位、精度損失、NaN 傳播 |
| 輸入邊界 | 對抗性輸入是否被系統性處理？ |
| 隨機性安全 | CSPRNG 使用是否正確？種子管理？ |
| 供應鏈 | 演算法依賴的數學庫是否經 SkillFortify 驗證？ |

---

## 迭代協議

> 完整迭代協議定義見 `skills/workflow-skills/iter-loop.md`。以下為本 Stage 的具體化。

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 A-V 22 維度，窮盡式批判                │
│  → 產出：問題清單 + 方向建議（按嚴重度降序） │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → 絕對最佳優先收斂                          │
│  → 產出：完整自包含改善文件                  │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈（每個改善後立即執行）    │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → 驗證 ALG-xxx 追港至 NFR-xxx/UC-xxx        │
│  → 全數通過才進入 Step F                     │
├──────────────────────────────────────────────┤
│  Step F: 不動點判定（AI 自主）               │
│  → 所有發現皆 YAGNI → REACHED → Step C      │
│  → CRITICAL+HIGH 未收斂 → DIVERGING → Step C │
│  → 否則 → NOT_REACHED → 回到 Step A         │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 收斂確認（僅不動點時觸發） │
│  → [1] 加入新需求後繼續 → 回到 Step A       │
│  → [2] 通過 ✅ → 出口閘門驗證                │
└──────────────────────────────────────────────┘
```

---

## 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 演算法規格 | `ALG-xxx` | `docs/algorithm-specs.md` |
| 理論保證表 | — | `docs/algorithm-specs.md` |
| 效能基線 | — | `docs/performance-baseline.md` |
| 安全審計報告 | — | `docs/security-audit-stage4.md` |

---

## HITL 出口閘門

### 原有檢查
- [ ] 所有理論保證達目標等級
- [ ] 所有啟發式已被識別並標記
- [ ] 安全審計無 HIGH+ 發現

### 追溯矩陣驗證
- [ ] 所有 ALG-xxx 可追溯至 NFR-xxx 和/或 UC-xxx
- [ ] 正向追溯：ALG-xxx → CLS-xxx（預留）
- [ ] 反向追溯：ALG-xxx → NFR-xxx → FEA-xxx → BG-xxx
- [ ] 零孤兒 ID
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 5
