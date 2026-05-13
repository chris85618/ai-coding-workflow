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

### 審查維度（Agent α）— 4 維（擴充版）

> **基本心法**：所有 GoF 設計模式預設「有罪推定」。除非能具體指出應對哪種「Protected Variation」，否則一律建議降級。

#### OA：GRASP 責任分配
- **Information Expert**：每個方法是否放在擁有最多相關資訊的類別中？是否有不合理的外部狀態讀取？
- **Creator**：A 建立 B 的理由是否滿足 Creator 規範（A 包含 B / A 頻繁使用 B / A 擁有 B 的初始化資料）？是否需要提煉為 Factory？
- **Low Coupling / High Cohesion**：哪個類別的依賴度（出度/入度）過高？哪個類別承擔了不相干的職責？
- **貧血模型獵殺**：Domain 物件是否淪為只有 Getter/Setter 的資料結構？邏輯是否全部集中在 `Manager`/`Service`/`Controller` 這種上帝類別？

#### OB：GoF 必要性證偽
> 針對每一個使用中的 GoF 模式，逐一追問：
- 這裡真的**確定**會發生擴充嗎？發生機率與代價多高？
- 如果只有一種實作，這個介面是否為**冗餘抽象**？
- 這裡的 Strategy 是否只需 Enum 或 Higher-order Function 就能解決？
- 這裡的 Observer 是否導致邏輯碎裂與追蹤困難（Callback Hell）？能否改為其他流向？
- 這裡的 Abstract Factory 是否只是 `new` 的複雜化？
- 這裡的 Decorator 是否只需一個 `if` 條件？

#### OC：封裝漏洞（Encapsulation Leaks）
- **集合暴露**：集合是否被直接 expose（回傳 `List<T>` 而非 `IReadOnlyList<T>` 或業務方法）？
- **不變量可繞過**：類別內部狀態是否能被外部繞過不變量直接修改？
- **非法狀態可建構**：建構子是否允許建立出不合法的非穩態物件？
- **DIP 所有權**：介面的所有權是否屬於**呼叫端**（高階策略）而非實作端（低階細節）？高階策略是否依賴了低階細節？

#### OD：UML 語意與依賴合理性
- **生命週期綁定**：組合（`*--`）與聚合（`o--`）是否精確？真的「同生共死」才能用 `*--`？
- **循環依賴**：是否存在 A→B→C→A 的環形依賴？如何透過引入介面（DIP）或中介者（Mediator）打破？
- **LSP 違反**：繼承（`<|--`）是否違反 Liskov 替換原則？是否可「組合優於繼承」取代？
- **依賴方向**：箭頭是否指向核心穩定層？是否有高階模組依賴低階模組的情況？

### S2C 增強：DDD 領域建模

> 由 `skills/workflow-skills/s2c-domain-model.md` 技能執行。
> 輸入：UC-xxx, ALG-xxx。輸出：CLS-xxx, EVT-xxx → `docs/domain-model.md`。

- **Track 1: 聚合識別**：每個 UC-xxx 識別交易邊界、實體/值物件、聚合根 → CLS-xxx，記錄不變量 → INV-xxx（預留至 Stage 6）
- **Track 2: 限界上下文**：每個功能領域定義限界上下文、通用語言、上下文介面
- **Track 3: 領域事件**：每個跨聚合操作識別領域事件 → EVT-xxx

### S2C 增強：安全測試映射

- 每個 UC-xxx 映射至 OWASP Top 10 分類（A01-A10）
- 產出安全測試模板 → feed 子步驟 5b

### Agent β 收斂決策框架

> **核心心法**：如無必要，勿增實體（奧卡姆剃刀）。遇到 GoF 質疑，若無法提出強而有力的「Protected Variation」業務理由，必須勇敢**降級**。

#### Step β-1：變更防禦評估（GoF 存廢決策）
- 該模式保護了什麼變異？此變異發生的機率與不應對代價多高？
- **代價低 → 降級**（移除介面、退回普通類別或 Lambda）
- **代價高 → 保留並優化介面隔離（ISP）**，確保最小化介面

#### Step β-2：責任重新分配（GRASP 修正）
- 判斷邏輯是否能被某個 Entity 內部吸收（變成私有行為）→ **充血模型優先**
- 若涉及多個 Entity → 考慮引入 Domain Service 或 Application Controller
- 將 Service/Manager 邏輯強制收斂回 Domain Classes（Information Expert）

#### Step β-3：UML 語法與關係校正
- 確認 `<|--`、`<|..`、`*--`、`o--`、`-->`、`<..` 的精準使用
- 生命週期同生共死才能用 `*--`，否則降為 `o--` 或 `-->`
- 每次迭代輸出一份**架構決策紀錄（Iteration ADR）**，記錄：移除了哪些過度設計、重新分配了哪些職責、解決了哪些循環依賴

#### 不動點停機條件（精確定義）
> 當 Agent β 開始大量以 **YAGNI** 和 **SRP** 拒絕 Agent α 為防禦而新增介面的建議時，UML 類別圖即達到「**最小完備抽象**」不動點：
> - 無法再拔除任何介面而不破壞 OCP（強迫改核心代碼）
> - 無法再新增任何介面而不違反 YAGNI（無當下業務防禦理由）
> - Agent α 的質疑降級為「未來極端情況」級別 → β 以 YAGNI 拒絕 → **REACHED**

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

> 完整迭代協議定義見 `skills/workflow-skills/iter-loop.md`。以下為本 Stage 的具體化。

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 OA-OD 4 維度 + DDD 分析               │
│  → 產出：問題清單 + 方向建議（按嚴重度降序） │
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
│  → 全數通過才進入 Step F                     │
├──────────────────────────────────────────────┤
│  Step F: 不動點判定（AI 自主）               │
│  → 所有發現皆 YAGNI → REACHED → Step C      │
│  → CRITICAL+HIGH 未收斂 → DIVERGING → Step C │
│  → 否則 → NOT_REACHED → 回到 Step A         │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 收斂確認（僅不動點時觸發） │
│  → [1] 加入新需求後繼續 → 回到 Step A       │
│  → [2] 通過 ✅ → 執行子步驟 5b 安全審計     │
│      → 安全審計通過 → 出口閘門驗證          │
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
