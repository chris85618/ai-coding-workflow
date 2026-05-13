# Phase 2：專案分析與產品思考

> **主角：gstack + S2C 結構化分析**
> 在寫任何程式碼之前，先建立完整的專案基礎：商業目標、利害關係人、範圍定義、策略驗證。
> 本階段所有產出物皆指派 ID 並納入追溯矩陣。

---

## 步驟 2.0：專案章程（Project Charter）

### 目標
建立專案的單一事實來源：核心願景、目標使用者、成功指標、風險等級。

### S2C 分析流程

**Step 1: 資源掃描**
```
FOR each existing_file IN project_directory:
  classify(file) → source_code / config / docs / test / asset
  extract_metadata(file) → language, framework, dependencies
  REPORT: project_profile
```

**Step 2: 商業目標萃取**
```
問題陳述 → 動詞萃取 → 所需行動 → 商業目標 → BG-xxx ID
成功指標 → 可量測條件 → 目標值 → BG-xxx ID
```

**Step 3: 風險分類**
```
FOR each charter_field:
  impact = assess_impact(1-5)
  probability = assess_probability(1-5)
  risk_level = impact × probability
  IF risk_level >= 10: flag_for_hitl()
```

### 工具
- `/understand` context（若 Path B）
- 手動結構化輸出

### 產出物
| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 專案章程 | `BG-xxx` | `docs/project-charter.md` |

### HITL 閘門
- [ ] 所有 BG-xxx 已指派且描述明確
- [ ] 成功指標可量測
- [ ] 風險等級已分類
- [ ] 追溯矩陣已初始化

---

## 步驟 2.1：利害關係人與問題分析

### 目標
識別所有利害關係人，建立影響力矩陣、RACI 責任分工、溝通策略。

### 整合工具

```
/office-hours
```

gstack 會扮演 YC Office Hours 的角色：
1. 提出 6 個逼迫性問題（forcing questions），挖掘真正的需求
2. 挑戰你的前提假設
3. 重新定義問題框架
4. 提出 3 個實作方案與工作量估算
5. **產出：Design Doc**（自動餵入下游 skill）

### S2C 增強：結構化利害關係人分析

**在 `/office-hours` 之後追加**：

```
FROM charter(BG-xxx):
  extract_target_users → S-xxx (Primary User)
  extract_metric_owners → S-xxx (Management)
  extract_decision_authority → S-xxx (Decision Maker)
  infer_technical_roles → S-xxx (Technical)

FOR each S-xxx:
  profile(interests, concerns, power, engagement)
  classify_influence(power × interest) → quadrant
  assign_raci(activities)
  plan_communication(frequency, format, content)

VALIDATE:
  all_raci_have_single_accountable()
  high_influence_have_communication_plan()
  no_stakeholder_accountable_for_50_percent_plus()
```

### 產出物
| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 利害關係人分析 | `S-xxx` | `docs/stakeholder-analysis.md` |
| Design Doc | — | gstack 自動管理 |

### 追溯驗證
- [ ] 所有 S-xxx 可追溯至 BG-xxx
- [ ] 影響力矩陣已完成
- [ ] RACI 已驗證（每活動僅一個 A）

---

## 步驟 2.2：範圍定義

### 目標
定義系統邊界、約束條件和假設，確保可執行的專案範圍。

### S2C 分析流程

**Feature 衍生**：
```
FOR each BG-xxx:
  problem_statement → verb_extraction → required_action → feature_name → FEA-xxx
FOR each success_metric IN BG-xxx:
  metric → data_needed → feature_providing_data → FEA-xxx
FOR each S-xxx WHERE influence = HIGH:
  interest → desired_outcome → feature_name → FEA-xxx
```

**排除項目衍生**：
```
FOR each related_but_unmentioned_feature:
  evidence = search_charter_for_mention()
  IF evidence = NONE:
    classify_as_out_of_scope(rationale)
```

**約束萃取**：
```
FROM charter.trade_off_matrix:
  FOR each dimension WHERE rank <= 3:
    map_to_constraint_type(time / budget / technical / regulatory)
    extract_specific_limitation()
```

### Red Team 挑戰（強制執行）

本步驟必須執行以下三個挑戰：

**挑戰 1: 範圍蔓延偵測**
```
FOR each FEA-xxx IN in_scope:
  adjacent_features = identify_commonly_requested_adjacent()
  IF adjacent_feature NOT IN out_of_scope:
    WARN: "FEA-xxx 常伴隨 [adjacent]，建議明確排除或納入"
    → HITL 決策：納入 / 排除 / 接受風險
```

**挑戰 2: 約束衝突偵測**
```
scope_complexity = count(FEA-xxx) × avg_complexity
available_capacity = timeline × team_size
IF scope_complexity > available_capacity:
  WARN: "範圍-時程衝突"
  → HITL 決策：縮減範圍 / 延長時程 / 增加資源 / 接受技術債
```

**挑戰 3: 隱性依賴偵測**
```
FOR each FEA-xxx IN out_of_scope:
  FOR each S-xxx WHERE influence = HIGH:
    IF FEA-xxx satisfies S-xxx.core_interest:
      WARN: "排除 FEA-xxx 可能衝突 S-xxx 期望"
      → HITL 決策：納入 / 記錄為已知風險 / 安排對齊會議
```

### 產出物
| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 範圍定義 | `FEA-xxx` | `docs/scope-definition.md` |
| 約束條件 | — | `docs/scope-definition.md` |
| 假設登記 | `ASM-xxx` | `docs/scope-definition.md` |

### 追溯驗證
- [ ] 所有 FEA-xxx 可追溯至 BG-xxx 和/或 S-xxx
- [ ] 至少 3 個 FEA-xxx 為 In-Scope
- [ ] 至少 2 個排除項目有明確理由
- [ ] Red Team 三個挑戰皆已執行並記錄決策

---

## 步驟 2.3：策略驗證

```
/plan-ceo-review
```

以 CEO 視角審查 Design Doc，提供 4 種模式：
- **Expansion**：想更大
- **Selective Expansion**：局部擴展
- **Hold Scope**：維持範圍
- **Reduction**：縮減至 MVP

### 產出物
| 產出 | 寫入位置 |
|------|---------|
| 策略審查報告 | gstack 自動管理 |
| 範圍決策紀錄 | `docs/scope-definition.md` 追加 |

---

## Phase 2 出口閘門

### 原有檢查
- [ ] 專案章程已核准
- [ ] 利害關係人已識別並分析
- [ ] 範圍已凍結（In-Scope / Out-of-Scope 明確）
- [ ] 策略已驗證
- [ ] 使用者確認 ✅

### 追溯矩陣驗證
- [ ] 所有 BG-xxx 已指派
- [ ] 所有 S-xxx 可追溯至 BG-xxx
- [ ] 所有 FEA-xxx 可追溯至 BG-xxx 和/或 S-xxx
- [ ] 零孤兒 ID
- [ ] 語意一致性通過
- [ ] 追溯矩陣文件已寫入 `docs/`

**通過後進入 Stage 3（技術規劃）**
