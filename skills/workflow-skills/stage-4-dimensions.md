# Skill: Stage 4 審查維度 + 演算法層級安全審計

> **觸發條件**：Stage 4（演算法設計）迭代迴圈中
> **輸入**：FR-xxx, NFR-xxx, UC-xxx, ADR-STR-xxx（Stage 3 產出）
> **輸出**：ALG-xxx → `{target_repo}/docs/algorithm-specs.md`
> **依賴 skill**：`iter-loop.md`、`security-audit-3layer.md`

---

## Step 1: 審查維度表（Agent α）— 22 維

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

## Step 2: S2C 增強輸入

- **效能基線**：每個 NFR-xxx (type=PERFORMANCE) 建立量測基線（延遲、吞吐量、資源用量），設定目標閾值 → feed Agent α 維度 B
- **模式目錄**：每個已驗證的架構模式記錄適用性和取捨 → feed Agent β 收斂

## Step 3: Agent β 收斂心法

- **絕對最佳優先**：能升🅐⁺就升
- 加速技術：Minimax 下界(→🅐)、Variance Reduction(🅒→🅑)、K-FAC/Shampoo、Polyak-Ruppert Averaging
- **禁止 fallback / 條件旁路**（數學彙整除外）
- **暫禁降為🅓**
- 每張理論保證表必須加新欄位說明加速/逼近技術

## Step 4: 演算法層級安全審計

在演算法設計達不動點後，於同一迭代迴圈內執行：

```bash
skillfortify scan . --severity-threshold high
skillfortify trust <algorithm-module>
```

| 審計維度 | 檢查項 |
|---------|--------|
| 數值安全 | 溢位、精度損失、NaN 傳播 |
| 輸入邊界 | 對抗性輸入是否被系統性處理？ |
| 隨機性安全 | CSPRNG 使用是否正確？種子管理？ |
| 供應鏈 | 演算法依賴的數學庫是否經 SkillFortify 驗證？ |

## Step 5: 迭代協議

觸發 `iter-loop.md`，參數：
- 審查維度 = A-V (22 維)
- Agent β 收斂心法 = 絕對最佳優先
- 追溯驗證 = ALG-xxx → NFR-xxx/UC-xxx

## Step 6: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 演算法規格 | `ALG-xxx` | `docs/algorithm-specs.md` |
| 理論保證表 | — | `docs/algorithm-specs.md` |
| 效能基線 | — | `docs/performance-baseline.md` |
| 安全審計報告 | — | `docs/security-audit-stage4.md` |

## Step 7: HITL 出口閘門

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
