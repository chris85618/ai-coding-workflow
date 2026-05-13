# Skill: Stage 5 審查維度 + OOAD 方法論 + 安全審計

> **觸發條件**：Stage 5（OOAD + 安全審計）迭代迴圈中
> **輸入**：UC-xxx, ADR-STR-xxx (Stage 3), ALG-xxx (Stage 4)
> **輸出**：CLS-xxx, EVT-xxx, ADR-SEC-xxx → `{target_repo}/docs/`
> **依賴 skill**：`s2c-domain-model.md`、`security-audit-3layer.md`、`iter-loop.md`

---

## Step 1: 審查維度表（Agent α）— 4 維（擴充版）

### OA：GRASP 責任分配

- **Information Expert**：每個方法是否放在擁有最多相關資訊的類別中？是否有不合理的外部狀態讀取？
- **Creator**：A 建立 B 的理由是否滿足 Creator 規範（A 包含 B / A 頻繁使用 B / A 擁有 B 的初始化資料）？是否需要提煉為 Factory？
- **Low Coupling / High Cohesion**：哪個類別的依賴度（出度/入度）過高？哪個類別承擔了不相干的職責？
- **貧血模型獵殺**：Domain 物件是否淪為只有 Getter/Setter 的資料結構？邏輯是否全部集中在 `Manager`/`Service`/`Controller` 這種上帝類別？

### OB：GoF 必要性證偽

> 所有 GoF 設計模式預設「有罪推定」。除非能具體指出應對哪種「Protected Variation」，否則一律建議降級。

針對每一個使用中的 GoF 模式，逐一追問：
- 這裡真的**確定**會發生擴充嗎？發生機率與代價多高？
- 如果只有一種實作，這個介面是否為**冗餘抽象**？
- Strategy 是否只需 Enum 或 Higher-order Function？
- Observer 是否導致邏輯碎裂與追蹤困難（Callback Hell）？
- Abstract Factory 是否只是 `new` 的複雜化？
- Decorator 是否只需一個 `if` 條件？

### OC：封裝漏洞（Encapsulation Leaks）

- **集合暴露**：集合是否被直接 expose（回傳 `List<T>` 而非 `IReadOnlyList<T>` 或業務方法）？
- **不變量可繞過**：類別內部狀態是否能被外部繞過不變量直接修改？
- **非法狀態可建構**：建構子是否允許建立出不合法的非穩態物件？
- **DIP 所有權**：介面所有權是否屬於**呼叫端**（高階策略）而非實作端？

### OD：UML 語意與依賴合理性

- **生命週期綁定**：組合（`*--`）與聚合（`o--`）是否精確？真的「同生共死」才能用 `*--`？
- **循環依賴**：是否存在 A→B→C→A 環形依賴？如何透過 DIP 或 Mediator 打破？
- **LSP 違反**：繼承（`<|--`）是否違反 Liskov 替換原則？是否可「組合優於繼承」取代？
- **依賴方向**：箭頭是否指向核心穩定層？

## Step 2: Agent β 收斂決策框架

> **核心心法**：如無必要，勿增實體（奧卡姆剃刀）。

### β-1：變更防禦評估（GoF 存廢決策）
- 該模式保護了什麼變異？此變異發生的機率與不應對代價多高？
- **代價低 → 降級**（移除介面、退回普通類別或 Lambda）
- **代價高 → 保留並優化介面隔離（ISP）**

### β-2：責任重新分配（GRASP 修正）
- 判斷邏輯是否能被某個 Entity 內部吸收 → **充血模型優先**
- 若涉及多個 Entity → 考慮 Domain Service 或 Application Controller
- 將 Service/Manager 邏輯強制收斂回 Domain Classes（Information Expert）

### β-3：UML 語法與關係校正
- 確認 `<|--`、`<|..`、`*--`、`o--`、`-->`、`<..` 的精準使用
- 生命週期同生共死才能用 `*--`，否則降為 `o--` 或 `-->`
- 每次迭代輸出 Iteration ADR：移除了哪些過度設計、重新分配了哪些職責

### 不動點停機條件
> 當 Agent β 開始大量以 YAGNI 和 SRP 拒絕 Agent α 為防禦而新增介面的建議時，UML 達到「最小完備抽象」不動點：
> - 無法再拔除任何介面而不破壞 OCP
> - 無法再新增任何介面而不違反 YAGNI
> - Agent α 質疑降級為「未來極端情況」級別 → β 以 YAGNI 拒絕 → REACHED

## Step 3: DDD 領域建模

觸發 `skills/workflow-skills/s2c-domain-model.md`：
- 輸入：UC-xxx, ALG-xxx
- 輸出：CLS-xxx, EVT-xxx → `docs/domain-model.md`

## Step 4: 安全測試映射

- 每個 UC-xxx 映射至 OWASP Top 10 分類（A01-A10）
- 產出安全測試模板

## Step 5: 子步驟 5b — 三層安全審計

觸發 `skills/workflow-skills/security-audit-3layer.md`：
- 三層全 PASS → 放行
- 任一層 HIGH+ → 回到 Step 1 修改設計

## Step 6: 產出物格式

PlantUML Design Class Diagram，必須：
- 標示 `<<interface>>`、`<<abstract>>`、可見性（`+`, `-`, `#`）
- 嚴格使用正確 UML 關係箭頭
- 大量使用 `note` 標注 GRASP/SOLID 設計意圖

## Step 7: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| PlantUML 類別圖 | `CLS-xxx` | `docs/class-diagram.puml` |
| DDD 領域模型 | `CLS-xxx`, `EVT-xxx` | `docs/domain-model.md` |
| OWASP 映射表 | — | `docs/security-mapping.md` |
| 安全審計報告 | — | `docs/security-audit-stage5.md` |
| ASBOM | — | `docs/asbom.json` |

## Step 8: HITL 出口閘門

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
- [ ] 所有文件已寫入 `docs/`

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Stage 6
