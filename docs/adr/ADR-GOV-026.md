# ADR-GOV-026: 五工具管線整合修正（Ponytail 接線 + 過期指令修正）

**狀態**: Accepted
**日期**: 2026-07-06
**決策者**: 人類 HITL（要求全面調查與修正）
**追溯**: RISK-003（docs/ 與 skills/ 版本漂移）

---

## 背景

全面調查 33 個 workflow-skills 與五個 submodule 的實際能力後發現：

1. **Ponytail 零整合**：commit 40d1c0c 加入 ponytail submodule 與 AGENTS.md 路由表，但 33 個 workflow-skills 引用數為零。Execution Protocol 的 TOOLS 行也未含任何 ponytail 指令。
2. **phase-0 安裝指令錯誤**：`npx -y gstack@latest init` 不存在（gstack 實際以 `git clone` + `./setup` 安裝）；`gstack-config set language zh-TW` 的 `language` 不是有效 key（有效 key 為 proactive/checkpoint_mode 等 14 個）。
3. **phase-10 工具歸屬錯誤**：`/evolve` 標為 gstack，實為 ECC command。
4. **AGENTS.md `/tdd` 過期**：ECC 已將 `/tdd` 退役為 legacy shim（legacy-command-shims/），正式入口為 `tdd-workflow` skill。
5. **stage-4 SkillFortify 措辭錯誤**：「數學庫經 SkillFortify 驗證」— SkillFortify 是 agent skill 供應鏈掃描器（22 框架），不驗證一般數學庫。
6. **README 漂移**：缺 ponytail（目錄樹/矩陣/安裝）、「四個 submodule」實為五個、維度代號過期（A1-A22/O1-O4/V1-V6/B1-B9 vs 實際 A-V/OA-OD/F1-F6/B1-B5+V1-V4）、workflow-skills 數量 17 實為 33、ADR 範圍 ..023 實為 ..026。
7. **Phase 9 Lockfile 缺口**：README 矩陣宣稱 Phase 9 有 SkillFortify Lockfile 驗證，但 phase-9-orchestration.md 未實作。
8. **Phase 0 無工具可用性檢查**：ADR-GOV-017 要求優雅降級，但管線起點從未確認五工具哪些可用。

## 決策

1. **Ponytail 接線**（依其 YAGNI/stdlib-first 定位，對齊 Operational Principle 10）：
   - Stage 5 β-1（GoF 存廢決策）：`/ponytail-review` 作為收斂加速器
   - Stage 8 新增 Step 2.5：實作全程 `/ponytail` 懶人模式，邊界為不得剃除 Stage 5 已定案介面（D2）與 D4 防禦性設計；`ponytail:` 註解 → Step 5.5 經 `/ponytail-debt` 收債
   - tech-debt-collect 來源 #8：`ponytail:` 註解（降級路徑 `grep -rn "ponytail:"`）
   - Phase 10 新增 Step 2.5：`/ponytail-audit` + `/ponytail-gain` 全庫審計，餵入技術債收集
2. **Phase 0 Step 1 改為工具可用性檢查**：五工具逐一檢查 + 各自純 LLM 降級路徑（實作 ADR-GOV-017）；gstack 安裝指令修正為 git clone + ./setup（建議而非自動執行）；移除無效 `language` key。
3. **修正歸屬與措辭**：`/evolve`、`/learn` 標為 ECC；stage-4 供應鏈審計限定於 agent skill / MCP / 工具定義，數學庫穩定性歸 Stage 3 T6。
4. **Understand Anything 補強**：路由表加 `/understand-domain`、`/understand-knowledge`；Phase 1 新增 Step 3.5 領域知識萃取，產出餵入 Phase 2 與 Stage 5 DDD。
5. **Phase 9 Step 1 補 Lockfile 新鮮度驗證**：`skillfortify lock` 重生成比對，有 diff 回 Stage 8。
6. **AGENTS.md TOOLS 行同步**：Step 4 加 `/plan-devex-review`；Step 6 加 `/ponytail-review`；Step 9 加 `/ponytail`、`/ponytail-review`、`/ponytail-debt`；Step 11 加 `/learn`、`/ponytail-audit`、`/ponytail-gain`。
7. **README 同步**：ponytail 全面補入、五 submodule、維度代號、矩陣加 Ponytail 欄、安裝步驟 #6。

## 後果

### 正面
- 五工具在管線中每個適用點都有明確接線，且全部附純 LLM 降級路徑（ADR-GOV-017 合規）
- 消除 8 項會導致執行期錯誤或誤導的過期內容
- Ponytail 的 YAGNI 執法與 Agent β 奧卡姆剃刀、Stage 5 不動點判定形成工具鏈閉環

### 負面
- Stage 8 新增 Step 2.5 使該 skill 變長；緩解：邊界條款防止懶人模式與 D2/D4 衝突

### 風險
- RISK-003（版本漂移）依然 open：submodule 更新後指令可能再度過期 → 緩解方向：Phase 10 /retro 時抽查 TOOLS 行有效性

---

## LESSON

**LESSON-053**: 新 submodule 只加路由表不接線至 workflow-skills，等於未整合。工具整合的完成定義（DoD）必須包含：(1) AGENTS.md 路由表 (2) 對應 Step 的 TOOLS 行 (3) 相關 workflow-skills 的執行步驟 (4) 降級路徑 (5) README 目錄樹/矩陣/安裝。

- **根因分類**: DECLARATION_IMPLEMENTATION_GAP
- **瓶頸識別**: 無「工具整合 DoD」清單，加 submodule 的變更未觸發跨文件一致性驗證（CM Step 5 門檻為 3+ 檔案，單檔加路由表不觸發）
- **左移守衛**: 本 ADR 的 DoD 五項清單；未來新增 submodule 時以此為 CM Step 2b 覆蓋斷言的檢查表

**LESSON-054**: 引用外部工具 CLI 指令時必須對照該工具當前原始碼驗證（bin/、pyproject scripts、README install 節），禁止憑記憶或舊文件寫入。`npx -y gstack@latest init` 與 `gstack-config set language` 均為未經驗證的臆造指令。

- **根因分類**: ASSUMPTION_OVERRIDE
- **瓶頸識別**: workflow-skills 中的外部指令無驗證機制
- **左移守衛**: Phase 0 Step 1 工具可用性檢查以實際檢測取代假設；Phase 10 /retro 抽查 TOOLS 行

---

## 變更紀錄

| # | 檔案 | 變更內容 | 分類 |
|---|------|---------|------|
| 1 | AGENTS.md | /tdd 退役標注、UA 路由 +2、TOOLS 行 ×4 更新 | FIX + GOVERNANCE_RULE |
| 2 | skills/workflow-skills/phase-0-orchestration.md | Step 1 改為五工具可用性檢查、修正 gstack 安裝指令、移除無效 config key | FIX |
| 3 | skills/workflow-skills/phase-1-understanding.md | Step 3.5 /understand-domain 新增 | MODIFY |
| 4 | skills/workflow-skills/stage-4-dimensions.md | 供應鏈審計措辭修正 | FIX |
| 5 | skills/workflow-skills/stage-5-dimensions.md | β-1 加 /ponytail-review、DDD 輸入加 domain 流程圖 | MODIFY |
| 6 | skills/workflow-skills/stage-8-dimensions.md | Step 2.5 懶人模式、審查清單 + /ponytail-review、Step 5.5 + /ponytail-debt | MODIFY |
| 7 | skills/workflow-skills/phase-9-orchestration.md | Step 1 加 Lockfile 新鮮度驗證 | MODIFY |
| 8 | skills/workflow-skills/phase-10-orchestration.md | /evolve 歸屬修正、Step 2.5 ponytail 審計、/learn 補入 | FIX + MODIFY |
| 9 | skills/workflow-skills/tech-debt-collect.md | 來源 #8 ponytail: 註解 | MODIFY |
| 10 | README.md | ponytail 補入（樹/矩陣/安裝）、五 submodule、維度代號、計數修正 | FIX |
| 11 | docs/adr/ADR-GOV-026.md | 本檔案建立 | ADR_CREATE |
| 12 | docs/workflow-state.md | Session 收尾更新 | STATE |
