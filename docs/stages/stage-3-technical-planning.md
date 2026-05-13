# Stage 3：技術規劃

> **[雙 Agent 迭代]** 將專案分析轉化為可執行的技術計畫。
> 本 Stage 的迭代迴圈定義見下方「迭代協議」節。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Phase 2.0 | 專案章程 | BG-xxx |
| Phase 2.1 | 利害關係人分析 | S-xxx |
| Phase 2.2 | 範圍定義 | FEA-xxx |
| Phase 2.3 | 策略審查報告 | — |
| Phase 1 | 知識圖譜（Path B） | — |

---

## 審查維度（Agent α）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| T1 | 架構可行性 | 技術方案是否能滿足所有 FEA-xxx 和 FR-xxx？邊界情境？ |
| T2 | 規模與效能 | 資料量/並行/延遲是否被系統性考量？NFR-xxx 是否完整？ |
| T3 | 安全威脅面 | 攻擊面是否被窮舉？STRIDE 是否完整？ |
| T4 | 測試策略 | 測試矩陣是否覆蓋所有分支？驗收標準是否明確？ |
| T5 | 技術債評估 | 是否引入不必要的耦合或捷徑？ |
| T6 | 依賴風險 | 第三方依賴的穩定性、授權、維護狀態？ |
| T7 | 範圍鎖定 | scope 是否精確？是否有隱性 scope creep？ |

---

## S2C 增強輸入

> 以下分析由 `skills/workflow-skills/s2c-requirements.md` 技能執行。
> 技能輸入：FEA-xxx（來自 Phase 2.2）。
> 技能輸出：FR-xxx, NFR-xxx, UC-xxx → `docs/requirements.md`, `docs/use-cases.md`。

### 分析涵蓋

- **需求分解**：每個 FEA-xxx 分解為 FR-xxx（功能需求）和 NFR-xxx（非功能需求）
- **使用案例識別**：每個 FR-xxx 對應至少一個 UC-xxx，含前/後置條件、替代流程、例外流程
- **關鍵場景**：risk_score ≥ 15 的 UC-xxx 標記為 critical，窮舉 edge cases
- **模式驗證**：架構決策的適用性驗證、陷阱檢查、替代方案比較

---

## 整合既有工具

```
/autoplan                  # gstack 自動全套審查 (CEO→Design→Eng→DX)
/plan-eng-review           # 架構圖、資料流、edge case、測試矩陣
/plan-design-review        # 設計維度 0-10 評分
/plan-devex-review         # DX 審查（若開發 API/SDK/CLI）
```

> gstack 的 `/autoplan` 產出物直接作為 Agent α 的審查輸入。Agent α 在 gstack 審查的基礎上進行更深層的窮盡式質疑。

---

## 迭代協議

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 T1-T7 維度，窮盡式批判                 │
│  → 驗證所有 FR-xxx, NFR-xxx, UC-xxx 完整性   │
│  → 產出：問題清單 + 方向建議                 │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → 對每個破綻執行決策流：                    │
│    分類 → 奧卡姆剃刀 → 前提窮盡             │
│    → 併吞分析 → 循環依賴破解 → 邊界內化     │
│  → 產出：完整自包含改善文件                  │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈（每個改善後立即執行）    │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → 全數通過才進入 Step C                     │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 迭代閘門                    │
│  → 使用者審查本輪摘要                        │
│  → [1] 繼續迭代  [2] 加入新需求後繼續        │
│  → [3] 通過 ✅ → 進入出口閘門驗證           │
└──────────────────────────────────────────────┘

不動點偵測：當 Agent α 僅剩 YAGNI 級質疑
→ 自動建議終止迭代
```

---

## 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 技術架構圖（ASCII） | — | `docs/architecture.md` |
| 功能需求登記 | `FR-xxx` | `docs/requirements.md` |
| 非功能需求登記 | `NFR-xxx` | `docs/requirements.md` |
| 使用案例登記 | `UC-xxx` | `docs/use-cases.md` |
| 架構決策紀錄 | `ADR-xxx` | `docs/adr/ADR-xxx.md` |
| 測試矩陣 | — | `docs/test-matrix.md` |
| 設計評分報告 | — | gstack 管理 |
| 迭代決策日誌 | — | `docs/iteration-log.md` |

---

## HITL 出口閘門

### 原有檢查
- [ ] 架構方案已批准
- [ ] 測試策略已定義
- [ ] 安全考量已識別
- [ ] 實作範圍已鎖定

### 追溯矩陣驗證
- [ ] 所有 FEA-xxx 已分解為 FR-xxx 和/或 NFR-xxx
- [ ] 所有 FR-xxx 已對應至少一個 UC-xxx
- [ ] 所有 ADR-xxx 可追溯至 FR-xxx
- [ ] 正向追溯完整：FEA → FR → UC
- [ ] 反向追溯完整：UC → FR → FEA → BG
- [ ] 零孤兒 ID
- [ ] 語意一致性通過
- [ ] 影響分析紀錄已完成（若有修改已核准產出物）
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 4
