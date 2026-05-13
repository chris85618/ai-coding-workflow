# Stage 5：物件導向設計 → 安全審計

> **[雙 Agent 迭代]** 將演算法規格轉化為 OOAD 類別圖，然後執行架構層安全審計。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Stage 3 | 使用案例 | UC-xxx |
| Stage 3 | 架構決策 | ADR-STR-xxx |
| Stage 4 | 演算法規格 | ALG-xxx |

---

## 子步驟 5a：OOAD 設計

### 審查維度（Agent α）— 4 維

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| OA | GRASP 責任分配 | Information Expert / Creator / Coupling / Cohesion 是否正確？ |
| OB | GoF 必要性證偽 | 有罪推定。每個設計模式真的需要嗎？Strategy 是否只需 Lambda？ |
| OC | 封裝漏洞 | 集合暴露？不變量可繞過？非法狀態可建構？ |
| OD | UML 語意與依賴 | 組合/聚合精確嗎？循環依賴？LSP 違反？繼承可替換為組合？ |

### S2C 增強：DDD 領域建模

> 由 `skills/workflow-skills/s2c-domain-model.md` 技能執行。
> 輸入：UC-xxx, ALG-xxx。輸出：CLS-xxx, EVT-xxx → `docs/domain-model.md`。

- **Track 1: 聚合識別**：每個 UC-xxx 識別交易邊界、實體/值物件、聚合根 → CLS-xxx，記錄不變量 → INV-xxx（預留至 Stage 6）
- **Track 2: 限界上下文**：每個功能領域定義限界上下文、通用語言、上下文介面
- **Track 3: 領域事件**：每個跨聚合操作識別領域事件 → EVT-xxx

### S2C 增強：安全測試映射

- 每個 UC-xxx 映射至 OWASP Top 10 分類（A01-A10）
- 產出安全測試模板 → feed 子步驟 5b

### Agent β 收斂心法

- **最小完備抽象**：無法再拔除任何介面而不破壞 OCP，也無法再新增任何介面而不違反 YAGNI
- **充血模型優先**：將 Service/Manager 邏輯強制收斂回 Domain Classes
- **如無必要，勿增實體**：勇敢降級設計模式
- **依賴方向是靈魂**：箭頭指向核心、指向穩定

### 產出格式

PlantUML Design Class Diagram，必須：
- 標示 `<<interface>>`、`<<abstract>>`、可見性（`+`, `-`, `#`）
- 嚴格使用正確 UML 關係箭頭（`<|--` 繼承、`<|..` 實現、`*--` 組合、`o--` 聚合）
- 大量使用 `note` 標注 GRASP/SOLID 設計意圖

---

## 子步驟 5b：安全審計（三層縱深）

```bash
# Layer 1: 應用安全
/cso                                      # gstack OWASP/STRIDE

# Layer 2: Agent 安全
npx ecc-agentshield scan --opus --stream  # ECC 紅藍隊審計

# Layer 3: 供應鏈安全
skillfortify scan . --format json         # 形式化供應鏈驗證
skillfortify sbom . --format cyclonedx    # ASBOM 生成
skillfortify lock . --output skill-lock.json
```

三層縱深防禦皆須通過，任一層 HIGH+ 發現 → 回到子步驟 5a 修改設計。

---

## 迭代協議

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 OA-OD 4 維度 + DDD 分析               │
│  → 產出：問題清單 + 方向建議                 │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → 最小完備抽象收斂                          │
│  → 產出：PlantUML 類別圖 + DDD 模型         │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈                          │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → CLS-xxx 追溯至 UC-xxx/ALG-xxx             │
│  → EVT-xxx 追溯至 CLS-xxx                    │
│  → 全數通過才進入 Step C                     │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 迭代閘門                    │
│  → [1] 繼續迭代  [2] 加入新需求              │
│  → [3] 通過 ✅ → 執行子步驟 5b 安全審計     │
│  → 安全審計通過 → 出口閘門驗證               │
└──────────────────────────────────────────────┘
```

---

## 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| PlantUML 類別圖 | `CLS-xxx` | `docs/class-diagram.puml` |
| DDD 領域模型 | `CLS-xxx`, `EVT-xxx` | `docs/domain-model.md` |
| OWASP 映射表 | — | `docs/security-mapping.md` |
| 安全審計報告 | — | `docs/security-audit-stage5.md` |
| ASBOM | — | `docs/asbom.json` |

---

## HITL 出口閘門

### 原有檢查
- [ ] UML 類別圖達最小完備抽象
- [ ] Agent α 僅剩 YAGNI 級質疑
- [ ] 三層安全審計全部 PASS
- [ ] SkillFortify 信任等級 ≥ COMMUNITY_VERIFIED

### 追溯矩陣驗證
- [ ] 所有 CLS-xxx 可追溯至 UC-xxx 和/或 ALG-xxx
- [ ] 所有 EVT-xxx 可追溯至 CLS-xxx
- [ ] DDD 限界上下文涵蓋所有 UC-xxx
- [ ] 正向追溯：CLS-xxx → INV-xxx（預留）→ SC-xxx → TC-xxx
- [ ] 反向追溯：CLS-xxx → UC-xxx → FR-xxx → FEA-xxx → BG-xxx
- [ ] 零孤兒 ID
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 6
