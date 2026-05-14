# Skill: ISO 31000 風險管理

> **觸發條件**：
>   - Phase 2 (RISK 識別時)
>   - Stage 8 安全審計後
>   - Phase 10 Retro
>   - 任何 skill 識別出 RISK-xxx 時（主動呼叫）
> **輸入**：風險描述、觸發情境、受影響 FEA/FR
> **輸出**：RISK-xxx → `{target_repo}/docs/risk-register.md` + 追溯矩陣更新
> **標準**: ISO 31000:2018 風險管理原則

---

## Step 1: 風險識別 (Risk Identification)

> **前置條件 (LESSON-030 守衛)**：指派 RISK-xxx ID 前，**必須**讀取 `{target_repo}/docs/traceability-matrix.md` § RISK→FEA 節，掃描最大序號後遞增。若矩陣不存在則窮舉搜尋全 repo（grep -rn "RISK-"）。禁止「假設從 RISK-001 開始」。

對每個候選風險執行：

1. 讀取 traceability-matrix.md § RISK→FEA 取得最大序號
2. 指派 `RISK-xxx` ID（MAX + 1）
3. 填寫基本屬性：
   - **標題**: 一句話描述
   - **類別**: TECHNICAL | SECURITY | PROCESS | COMPLIANCE | STRATEGIC | OPERATIONAL
   - **觸發來源**: {識別此風險的 Skill / Stage / Phase}
   - **受影響 FEA**: {FEA-xxx 列表}

## Step 2: 風險分析 (Risk Analysis)

對每個 RISK-xxx 量化：

```
機率 (Likelihood):
  1 = 罕見 (<5%)
  2 = 不太可能 (5-25%)
  3 = 可能 (25-50%)
  4 = 很可能 (50-75%)
  5 = 幾乎確定 (>75%)

影響 (Impact):
  1 = 微小 (可忽略)
  2 = 小 (輕微影響)
  3 = 中等 (中等影響)
  4 = 大 (嚴重影響)
  5 = 災難性 (系統性失敗)

風險強度 (Risk Score) = 機率 × 影響

強度等級:
  1-4   = LOW
  5-9   = MEDIUM
  10-14 = HIGH
  15-25 = CRITICAL
```

## Step 3: 風險評估 (Risk Evaluation)

依強度等級決定優先序：

| 強度等級 | 處理時限 | 需 HITL 確認 |
|----------|----------|--------------|
| CRITICAL | 立即（本 Sprint） | 是 |
| HIGH | 本 Sprint 內 | 是 |
| MEDIUM | 下個 Sprint | 建議 |
| LOW | 季度審查 | 否 |

## Step 4: 風險應對策略 (Risk Treatment)

從四種策略中選擇：

| 策略 | 代號 | 適用情境 |
|------|------|---------|
| 規避 (Avoid) | AV | 強度 CRITICAL，可以消除風險根源 |
| 轉移 (Transfer) | TF | 可透過第三方/合約轉移損失 |
| 緩解 (Mitigate) | MT | 降低機率或影響至可接受水準 |
| 接受 (Accept) | AC | 強度 LOW，或緩解成本大於風險成本 |

應對措施填寫：
- **應對動作**: {具體可執行的措施}
- **負責人**: AI | HITL
- **預期殘餘風險**: {應對後的強度}
- **對應 LESSON**: {LESSON-xxx（若有類似歷史）}

## Step 5: 更新風險登錄表 (Risk Register Update)

**強制步驟**：每次識別或更新 RISK-xxx 後，立即執行：

```
1. 打開 {target_repo}/docs/risk-register.md
2. 在「Active Risks」或「Closed Risks」節新增/更新 RISK-xxx 完整記錄
3. 打開 {target_repo}/docs/traceability-matrix.md
4. 在「RISK → FEA」節更新對應行（補充完整屬性欄）
5. 在覆蓋統計更新 RISK-xxx 計數
6. 若 RISK 狀態變 Closed/Rejected → 移至 Closed Risks 節
```

## Step 6: 風險監控 (Risk Monitoring)

每個 Phase/Stage 出口閘門時：

1. 掃描 risk-register.md 中所有 `status: open` 的 RISK-xxx
2. 重新評估機率/影響（情況可能已變）
3. 更新狀態：open | in-progress | closed | rejected
4. 在 Step 12.5 輸出「未應對風險數量」= status 為 `open` 且強度 >= MEDIUM 的 RISK-xxx 計數

## Step 7: 風險登錄表格式 (Register Format)

```markdown
### RISK-{NNN}: {標題}

| 欄位 | 值 |
|------|-----|
| **ID** | RISK-{NNN} |
| **狀態** | open \| in-progress \| closed \| rejected |
| **類別** | TECHNICAL \| SECURITY \| PROCESS \| COMPLIANCE \| STRATEGIC \| OPERATIONAL |
| **機率** | 1-5 ({百分比範圍}) |
| **影響** | 1-5 ({影響描述}) |
| **風險強度** | {機率×影響} ({LOW\|MEDIUM\|HIGH\|CRITICAL}) |
| **應對策略** | AV (規避) \| TF (轉移) \| MT (緩解) \| AC (接受) |
| **應對動作** | {具體措施} |
| **預期殘餘風險** | {強度等級} |
| **觸發來源** | {Skill / Stage / Phase} |
| **受影響 FEA** | {FEA-xxx 列表} |
| **對應 LESSON** | {LESSON-xxx 或 N/A} |
| **對應 ADR** | {ADR-xxx 或 N/A} |
| **建立日期** | {ISO 8601} |
| **最後更新** | {ISO 8601} |
| **負責人** | AI \| HITL |

**風險描述**：{詳細描述風險場景、觸發條件、潛在後果}
```
