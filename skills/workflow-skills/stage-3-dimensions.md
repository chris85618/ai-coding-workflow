# Skill: Stage 3 審查維度 + 出口閘門

> **觸發條件**：Stage 3（技術規劃）迭代迴圈中
> **輸入**：Phase 2 產出物 (BG-xxx, S-xxx, FEA-xxx)、知識圖譜（Path B）
> **輸出**：FR-xxx, NFR-xxx, UC-xxx, ADR-STR-xxx → `{target_repo}/docs/`
> **依賴 skill**：`s2c-requirements.md`（需求分解）、`iter-loop.md`（迭代迴圈）

---

## Step 1: 輸入確認

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Phase 2.0 | 專案章程 | BG-xxx |
| Phase 2.1 | 利害關係人分析 | S-xxx |
| Phase 2.2 | 範圍定義 | FEA-xxx |
| Phase 2.3 | 策略審查報告 | — |
| Phase 1 | 知識圖譜（Path B） | — |

## Step 2: 審查維度表（Agent α 使用）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| T1 | 架構可行性 | 技術方案是否能滿足所有 FEA-xxx 和 FR-xxx？邊界情境？ |
| T2 | 規模與效能 | 資料量/並行/延遲是否被系統性考量？NFR-xxx 是否完整？ |
| T3 | 安全威脅面 | 攻擊面是否被窮舉？STRIDE 是否完整？ |
| T4 | 測試策略 | 測試矩陣是否覆蓋所有分支？驗收標準是否明確？ |
| T5 | 技術債評估 | 是否引入不必要的耦合或捷徑？ |
| T6 | 依賴風險 | 第三方依賴的穩定性、授權、維護狀態？ |
| T7 | 範圍鎖定 | scope 是否精確？是否有隱性 scope creep？ |

## Step 3: S2C 需求分解

觸發 `skills/workflow-skills/s2c-requirements.md`：
- 輸入：FEA-xxx
- 輸出：FR-xxx, NFR-xxx, UC-xxx → `docs/requirements.md`, `docs/use-cases.md`

## Step 4: 整合工具

```
/autoplan                  # gstack 自動全套審查 (CEO→Design→Eng→DX)
/plan-eng-review           # 架構圖、資料流、edge case、測試矩陣
/plan-design-review        # 設計維度 0-10 評分
/plan-devex-review         # DX 審查（若開發 API/SDK/CLI）
```

gstack `/autoplan` 產出物直接作為 Agent α 審查輸入。Agent α 在 gstack 審查基礎上進行更深層窮盡式質疑。

## Step 5: 迭代協議

觸發 `skills/workflow-skills/iter-loop.md`，參數：
- 審查維度 = T1-T7
- 微驗證 = `micro-validation.md` + `impact-analysis-exec.md`
- 追溯驗證 = FR-xxx → FEA-xxx, UC-xxx → FR-xxx

## Step 6: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 技術架構圖（ASCII） | — | `docs/architecture.md` |
| 功能需求登記 | `FR-xxx` | `docs/requirements.md` |
| 非功能需求登記 | `NFR-xxx` | `docs/requirements.md` |
| 使用案例登記 | `UC-xxx` | `docs/use-cases.md` |
| 架構決策紀錄 | `ADR-STR-xxx` | `docs/adr/ADR-STR-xxx.md` |
| 測試矩陣 | — | `docs/test-matrix.md` |
| 迭代決策日誌 | — | `docs/iteration-log.md` |

## Step 7: HITL 出口閘門

### 原有檢查
- [ ] 架構方案已批准
- [ ] 測試策略已定義
- [ ] 安全考量已識別
- [ ] 實作範圍已鎖定

### 追溯矩陣驗證
- [ ] 所有 FEA-xxx 已分解為 FR-xxx 和/或 NFR-xxx
- [ ] 所有 FR-xxx 已對應至少一個 UC-xxx
- [ ] 所有 ADR-STR-xxx 可追溯至 FR-xxx
- [ ] 正向追溯完整：FEA → FR → UC
- [ ] 反向追溯完整：UC → FR → FEA → BG
- [ ] 零孤兒 ID
- [ ] 語意一致性通過
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 4
