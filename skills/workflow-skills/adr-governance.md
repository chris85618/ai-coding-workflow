# Skill: ADR 治理框架

> **觸發條件**：任何決策（人類 HITL 或 AI 自主）需要記錄時
> **用途**：ADR 粒度決策、類別判定、生命週期管理、HITL 進入點參照
> **核心原則**：每個決策都是 ADR，分層分類，雙向追溯

---

## Step 1: ADR 類別判定

| 類別 | 前綴 | 定義 | 決策者 |
|------|------|------|--------|
| STRUCTURAL | `ADR-STR-xxx` | 系統架構、模組邊界、技術棧 | AI + HITL |
| GOVERNANCE | `ADR-GOV-xxx` | 流程規則、閘門標準、審計 | AI + HITL |
| SECURITY | `ADR-SEC-xxx` | 安全控制、威脅模型回應 | AI + HITL |
| SCOPE | `ADR-SCP-xxx` | 功能邊界、MVP 定義、排除 | 人類 (Red Team) |
| GATE | `ADR-GATE-xxx` | HITL 閘門決策紀錄 | 人類 |
| OPERATIONAL | `ADR-OPS-xxx` | 部署、監控、事件回應 | AI + HITL |

編號：`ADR-{CATEGORY}-{NNN}`（例：ADR-GOV-001）

## Step 2: Decision Unit 理論

Decision Unit (DU) 滿足三性質：

| 性質 | 定義 | 違反後果 |
|------|------|---------|
| 共享關注點 | 所有選擇回答同一架構問題 | 不相關決策混入 → 拆分 |
| 後果耦合 | 後果分析互相依賴 | 後果獨立 → 拆分 |
| 反轉原子性 | 必須一起反轉 | 可獨立反轉 → 拆分 |

### 三個形式化測試

**DBT（Decision Boundary Test）**：
- 用一句話陳述核心決策
- 計算內聚分數 = 必要元素數 / 總元素數
- ≥ 0.8 → 高內聚 ✅；< 0.8 → 拆分

**CCT（Consequence Containment Test）**：
- 所有後果是否源自同一決策？
- 存在不同來源後果 → 拆分

**RIT（Reversal Independence Test）**：
- 能否反轉子決策 A 而保持 B 不變？
- 可獨立反轉 → 拆分為獨立 ADR

### ADR-GATE 頻率判定

每個 Decision Unit 一個 ADR-GATE，非每輪/每 Stage：

```
用戶 HITL 輸入 I：
  ├─ I 回答與當前 ADR 相同的架構問題？
  │   ├─ 是 → RIT 判定 → 同/不同 DU
  │   └─ 否 → 新 DU → 新 ADR
  └─ I 是 [通過] → 關閉 ADR → Accepted
```

## Step 3: 資訊新穎性評估

可推導性梯度（記錄門檻：L2+）：

| 等級 | 定義 | 判定 |
|------|------|------|
| L0 明示 | 逐字存在於現有文件 | 不記錄 |
| L1 平凡推論 | 單一文件、一步顯然推論 | 不記錄 |
| **L2 多步推論** | **需 2+ 文件、2+ 推論步驟** | **記錄** |
| **L3 跨域綜合** | **需結合不同領域知識** | **記錄** |
| **L4 隱性/默會** | **揭示未文字化的設計意圖** | **記錄** |
| **L5 湧現** | **單一元件無法預測的系統行為** | **記錄** |

「新工程師」啟發法：具備領域能力的工程師，閱讀所有文件一遍，15 分鐘內確定能推導 → 不記錄；否則 → 記錄。

## Step 4: ADR 生命週期

```
Proposed → Accepted → Superseded
              │
              └→ Deprecated
              └→ Amended (minor, 不產生新 ADR)
```

## Step 5: HITL 進入點登記冊

### Phase 0
| ID | 類型 | 進入點 | 產出 |
|----|------|--------|------|
| HITL-P0-01 | 💬 | gstack 首次引導 | ADR-GOV-xxx |
| HITL-P0-02 | ⚖️ | 恢復協議確認 | ADR-GATE-P0-xxx |

### Phase 2
| ID | 類型 | 進入點 | 產出 |
|----|------|--------|------|
| HITL-P2-00 | 🚪 | 專案章程核准 | ADR-SCP-xxx |
| HITL-P2-01 | 💬 | /office-hours | ADR-SCP-xxx |
| HITL-P2-20~22 | ⚖️ | Red Team 1~3 | ADR-SCP-xxx |
| HITL-P2-23 | 💬 | /plan-ceo-review | ADR-SCP-xxx |
| HITL-P2-EXIT | 🚪 | Phase 2 出口 | ADR-GATE-P2-xxx |

### Stage 3-8（每 Stage）
| ID 模式 | 類型 | 進入點 | ADR 行為 |
|---------|------|--------|---------|
| HITL-S{N}-CONVERGE | 🚪 | 收斂確認 | DU 判定 → 追加/新建/關閉 |
| HITL-S{N}-EXIT | 🚪 | Stage 出口 | 彙總 ADR-GATE |

### 跨切面
| ID | 類型 | 進入點 | 產出 |
|----|------|--------|------|
| HITL-GOV-MAJOR | 🚪 | MAJOR 影響確認 | ADR-{CAT}-xxx |
| HITL-GOV-MICRO | 🚨 | 微驗證 3 次失敗 | ADR-GATE-xxx |

### Phase 9-10
| ID | 類型 | 進入點 | 產出 |
|----|------|--------|------|
| HITL-P9-SHIP | 💬 | /ship | ADR-OPS-xxx |
| HITL-P10-RETRO | 💬 | /retro | ADR-GOV-xxx |
| HITL-P10-RCA | 🚪 | RCA 掃描確認 | ADR-GOV-xxx |

**統計**：16 必經閘門 + 12 互動 + 4 條件決策 + 4 失敗上報 = **36 HITL 點**

## Step 6: ADR 與治理產出物整合

- 每個變更追溯至一個 ADR（變更紀錄寫入 ADR）
- 每個 DEBT-xxx 追溯至 ADR
- MAJOR 影響分析 → 產出新 ADR
- 所有 LESSON-xxx 追溯至 ADR
- 每個 LESSON 必須包含「瓶頸識別推論」欄位（因果鏈 + 瓶頸位置 + 介入類型）
- 每個 LESSON 的「更新的 Skill」必須在追溯矩陣「LESSON → Skill」段落登記

