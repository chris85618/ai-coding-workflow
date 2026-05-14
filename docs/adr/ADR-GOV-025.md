# ADR-GOV-025: ISO 31000 風險管理框架 + DEBT/RISK 完整追溯制度

> **狀態**: Accepted
> **日期**: 2026-05-14T07:03+08:00
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-010, FR-011, FR-022, FR-023, ADR-GOV-008, ADR-GOV-011, ADR-GOV-023
> **取代**: N/A

---

## 背景

- 觸發 Stage/Phase：治理層（Session 2026-05-14）
- 觸發事件：HITL 要求補全 RISK/DEBT 追溯矩陣並建立符合 ISO 31000 的完整風險管理流程
- 前置條件：
  - RISK-xxx 在追溯矩陣僅有 1 筆且欄位不完整（無狀態/機率/影響/強度/策略）
  - DEBT-xxx 完全缺失於追溯矩陣，tech-debt-register.md 不存在
  - ADR-TEMPLATE.md 關聯產出物欄位為摘要，非完整登錄表
  - Step 12.5 輸出報告不含技術債與未應對風險計數
  - 各 skill 識別風險/債務時無強制呼叫對應管理 skill 的指令
- 約束：遵循 ISO 31000:2018 風險管理原則；維持 Ockham's Razor

## 決策

我們決定：

1. **建立 `skills/workflow-skills/risk-management.md`**：符合 ISO 31000 的完整風險管理 skill，含風險識別→分析→評估→應對→監控的全生命週期
2. **建立 `docs/risk-register.md`**：含完整欄位的風險登錄表（狀態/機率/影響/強度/策略/應對/LESSON 連結）
3. **建立 `docs/tech-debt-register.md`**：含完整欄位的技術債登錄表，與 RICE 分類對齊
4. **擴充 `docs/adr/ADR-TEMPLATE.md`**：關聯產出物區塊加入 RISK/DEBT 完整內嵌登錄表格式
5. **擴充追溯矩陣**：補 `DEBT-xxx → FR` 節、擴充 `RISK-xxx` 欄位（完整 ISO 31000 屬性）
6. **修改 `tech-debt-collect.md`**：加入更新追溯矩陣與 tech-debt-register.md 的強制步驟
7. **修改 `AGENTS.md` Step 12.5**：加入技術債數量與未應對風險數量輸出
8. **在風險/債務識別點 skill 加入觸發指令**（security-audit-3layer.md, root-cause-leftshift.md, phase-10-orchestration.md, stage-8-dimensions.md）

## 理由

- **ISO 31000 合規**：風險管理需要完整生命週期（識別→分析→評估→應對→監控），現有框架僅有識別
- **可觀測性**：Step 12.5 缺少關鍵指標導致治理盲點——HITL 無法在 session 結束時知曉未解風險數量
- **追溯完整性**：比照 LESSON-xxx 的追溯守衛模式，RISK/DEBT 需有同等級別的矩陣覆蓋
- **左移守衛**：各識別點若不主動呼叫登錄 skill，風險/債務會在識別後流失

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------| 
| 保持現狀（僅摘要欄位） | 零工作量 | 無法追蹤狀態/機率/強度，HITL 盲點持續 | 違反治理完整性 |
| 獨立 risk-register.md 無 ADR 連結 | 簡單 | 與追溯鏈斷鏈 | 違反 FR-022/023 |

## 後果

**正面**：
- RISK/DEBT 達到與 LESSON-xxx 相同級別的追溯完整性
- ISO 31000 合規，風險有完整生命週期管理
- Step 12.5 提供 HITL 完整的狀態快照
- 各識別點自動觸發登錄，防止流失

**負面**：
- 每次識別風險/債務需填寫較多欄位（ISO 31000 屬性）
- 需修改 6+ 個 skill 文件

**風險**：
- RISK-005: ADR-TEMPLATE.md 欄位過長導致 LLM 省略 → 緩解：欄位標記必填/選填

## 影響分析

- **爆炸半徑**: 15 個檔案
- **跨 Stage 影響**: 所有 Stage（治理層級）
- **嚴重度**: MAJOR
- **受影響 ID**: FR-010, FR-011, FR-022, FR-023, RISK-004, ADR-TEMPLATE, traceability-matrix, AGENTS.md Step 12.5

## 流程變更（GOVERNANCE 補充）

- **修改前規則**: RISK-xxx 僅有「FEA | 連結 | 語意」三欄；DEBT-xxx 不在追溯矩陣；Step 12.5 無計數
- **修改後規則**: RISK-xxx 含 ISO 31000 完整屬性；DEBT-xxx 加入追溯矩陣節；Step 12.5 強制輸出計數
- **影響範圍**: Phase 2（RISK識別）、Stage 8（DEBT識別）、Phase 10（兩者更新）
- **過渡期**: 立即生效，存量 RISK-001~005 補欄位

## 變更紀錄 (Implementation Records)

### 變更 #1: 建立 ISO 31000 風險管理 skill + 登錄表 + 技術債登錄表

- **日期**: 2026-05-14T07:03+08:00
- **類型**: CREATE
- **檔案**: `skills/workflow-skills/risk-management.md`, `docs/risk-register.md`, `docs/tech-debt-register.md`
- **影響 ID**: FR-010, FR-011, RISK-004, DEBT-xxx
- **爆炸半徑**: 3 個新建檔案 + 多個 skill 觸發點
- **嚴重度**: MAJOR
- **微驗證**: PASS
- **PGVG**: PASS (2a-2f)

### 變更 #2: 修改 ADR-TEMPLATE + traceability-matrix + AGENTS.md + tech-debt-collect

- **日期**: 2026-05-14T07:03+08:00
- **類型**: MODIFY
- **檔案**: `docs/adr/ADR-TEMPLATE.md`, `docs/traceability-matrix.md`, `AGENTS.md`, `skills/workflow-skills/tech-debt-collect.md`
- **影響 ID**: FR-022, FR-023, Step 12.5
- **爆炸半徑**: 4 個修改檔案
- **嚴重度**: MAJOR
- **微驗證**: PASS
- **PGVG**: PASS (2a-2f)

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-029: RISK/DEBT 追溯孤兒——識別後無強制登錄閘門

- **根因分類**: PROCESS_GAP
- **根因描述**: 風險和技術債在各 skill 被識別，但缺乏「識別後必須呼叫登錄 skill」的強制指令，導致追溯孤兒
- **5 Whys**:
  1. 為何 RISK-xxx 欄位不完整？ → ADR-TEMPLATE 關聯產出物僅要求摘要
  2. 為何 DEBT-xxx 不在追溯矩陣？ → tech-debt-register.md 無追溯矩陣更新步驟
  3. 為何 Step 12.5 無計數？ → AGENTS.md 模板未納入此可觀測性指標
  4. 為何各識別點不主動登錄？ → 無對應的「識別→登錄」守衛指令
  5. 為何結構如此？ → 初始設計只關注 LESSON-xxx 模式，未同等對待 RISK/DEBT
- **瓶頸識別**:
  - 問題發生點: Phase 2 RISK 識別、Stage 8 DEBT 識別、Phase 10 Retro
  - 逃逸路徑: ADR-TEMPLATE 未要求完整欄位 → 孤兒；tech-debt-collect.md 未更新矩陣 → 斷鏈
  - 最早可偵測點: ADR-TEMPLATE 撰寫階段
  - 瓶頸位置: `ADR-TEMPLATE.md` 關聯產出物區段 + `tech-debt-collect.md` Step 4
  - 介入類型: NEW_GUARD
  - 預期覆蓋: 所有新建 RISK/DEBT 項目強制帶完整欄位並更新追溯矩陣
- **左移守衛**: `risk-management.md` (新建), `tech-debt-collect.md` (Step 5 新增矩陣更新)
- **更新 Skill**: `risk-management.md` ✅, `tech-debt-collect.md` ✅, `ADR-TEMPLATE.md` ✅
- **守衛驗證證據**: risk-management.md Step 5 包含強制追溯矩陣更新；tech-debt-collect.md Step 5 同步

### 變更 #3: RISK/DEBT ID 衝突修正 + 窮舉搜尋守衛

- **日期**: 2026-05-14T07:17+08:00
- **類型**: FIX
- **檔案**: `docs/risk-register.md` (REWRITE), `docs/tech-debt-register.md` (MODIFY), `docs/traceability-matrix.md` (MODIFY), `docs/adr/ADR-GOV-002.md` (MODIFY), `docs/adr/ADR-GOV-022.md` (MODIFY), `docs/adr/ADR-GOV-025.md` (MODIFY), `skills/workflow-skills/risk-management.md` (MODIFY), `skills/workflow-skills/tech-debt-collect.md` (MODIFY)
- **影響 ID**: RISK-001~005, DEBT-001, LESSON-030
- **爆炸半徑**: 8 個檔案
- **嚴重度**: MAJOR
- **微驗證**: PASS
- **PGVG**: PASS (2a-2f)

**問題描述**：
1. 上一 session 建立 risk-register.md 時，未窮舉搜尋全 repo 的 RISK-xxx 引用，從 RISK-001 開始編號，導致與 scope-definition.md (Phase 2) 的原始 RISK-001 衝突。共 4 個不同定義使用同一 ID。
2. ADR-GOV-022 中的 DEBT-001 未登錄至 tech-debt-register.md 和 traceability-matrix.md。

**修正**：
- RISK-001 恢復為原始定義（SonarCloud 依賴外部服務帳號）
- ADR-GOV-002 的風險重新編號為 RISK-002
- ADR-GOV-022 的風險重新編號為 RISK-003
- 原 RISK-001 (CM協議) 重新編號為 RISK-004
- 原 RISK-002 (ADR-TEMPLATE) 重新編號為 RISK-005
- DEBT-001 正式登錄至 tech-debt-register.md 和 traceability-matrix.md

### LESSON-030: RISK/DEBT ID 指派前未窮舉搜尋導致 ID 衝突

- **根因分類**: SCAN_INCOMPLETENESS
- **根因描述**: AI 建立 risk-register.md 時，未先搜尋全 repo 的 RISK-xxx 引用就從 RISK-001 開始編號，導致與 4 個已存在的 RISK-001 衝突
- **5 Whys**:
  1. 為什麼 RISK-001 有 4 個不同定義？→ 建立 risk-register.md 時從 RISK-001 開始編號
  2. 為什麼從 RISK-001 開始？→ 未搜尋全 repo 確認已存在的 RISK-xxx ID
  3. 為什麼未搜尋？→ risk-management.md Step 1 僅寫「參考 risk-register.md 末尾」，但 risk-register.md 是新建的空檔案
  4. 為什麼新建空檔案會導致衝突？→ RISK-xxx 早已分散在 scope-definition.md、ADR-GOV-002.md、ADR-GOV-022.md
  5. 為什麼分散？→ 初始設計時 RISK-xxx 是 ADR 內的行內引用，無集中登錄機制
- **瓶頸識別**:
  - 問題發生點: risk-management.md Step 1 ID 指派
  - 逃逸路徑: Step 1 僅參考單一檔案 → 分散在多處的 ID 不可見
  - 最早可偵測點: risk-management.md Step 1 執行前
  - 瓶頸位置: `risk-management.md` Step 1 缺少窮舉搜尋前置條件
  - 介入類型: STEP_ADDITION (前置條件)
  - 預期覆蓋: 所有 RISK/DEBT ID 指派的衝突
- **左移守衛**: `risk-management.md` Step 1 前置條件 + `tech-debt-collect.md` ID 指派前置條件
- **更新 Skill**: `risk-management.md` ✅, `tech-debt-collect.md` ✅
- **守衛驗證證據**: Step 1 前置條件改為讀取 traceability-matrix.md 作為 SSOT，禁止假設從 001 開始。

### 變更 #4: 通用 ID 指派協議 + SSOT 判定 + 風險左移掃描 + 12.4 表格化 + 12.5 有向圖

- **日期**: 2026-05-14T07:33+08:00
- **類型**: MODIFY
- **檔案**: `skills/workflow-skills/traceability-system.md` (Step 0 新增), `skills/workflow-skills/root-cause-leftshift.md` (Step 7), `skills/workflow-skills/risk-management.md` (Step 1), `skills/workflow-skills/tech-debt-collect.md` (Step 1), `AGENTS.md` (Step 0, 12.4, 12.5)
- **影響 ID**: FR-022, FR-023, LESSON-030, LESSON-031
- **爆炸半徑**: 5 個修改檔案
- **嚴重度**: MAJOR
- **微驗證**: PASS
- **PGVG**: PASS (2a-2f)

**變更描述**：

1. **traceability-system.md 新增 Step 0**：通用 ID 指派協議（Universal ID Assignment Protocol）
   - SSOT 判定表：traceability-matrix.md 為所有 ID 前綴的編號 SSOT
   - 強制 6 步指派流程：READ → SCAN → CALC → FALLBACK → ASSIGN → REGISTER
   - 三項禁止行為
2. **root-cause-leftshift.md Step 7 強化**：LESSON-xxx ID 指派加入同樣的 traceability-matrix.md SSOT 守衛
3. **AGENTS.md Step 0 新增 step 4**：風險登錄表左移掃描，Session 啟動時即輸出 open 風險表格
4. **AGENTS.md Step 12.4 重寫**：checkbox 替換為四張強制表格（A: ID 登錄驗證, B: 追溯鏈完整性, C: 全方向連結, D: LESSON 重用）
5. **AGENTS.md Step 12.5 追加**：追溯矩陣關聯有向圖（mermaid graph LR），RISK 紅色節點、DEBT 橙色節點

### LESSON-031: ID 指派缺乏統一 SSOT 導致分散引用

- **根因分類**: ARCHITECTURE_EROSION
- **根因描述**: 各 skill 各自定義 ID 查找方式（有的掃描源文件、有的搜尋全 repo），無統一 SSOT，導致 ID 衝突風險持續存在
- **5 Whys**:
  1. 為什麼修正 LESSON-030 後仍有風險？→ 各 skill 查找 ID 的方式不統一
  2. 為什麼不統一？→ 沒有定義「哪個檔案是 ID 編號的 SSOT」
  3. 為什麼沒有定義 SSOT？→ traceability-system.md 只定義了 ID 前綴規格，未定義查找流程
  4. 為什麼未定義查找流程？→ 初始設計假設 ID 只在單一檔案產出，未預見散布問題
  5. 為什麼散布？→ RISK/DEBT/LESSON 可在任意 Stage 產出，不像 FR/UC 有固定 Stage
- **瓶頸識別**:
  - 瓶頸位置: `traceability-system.md` 缺少 ID 指派協議
  - 介入類型: STEP_ADDITION (Step 0)
  - 預期覆蓋: 所有 16 種 ID 前綴的指派衝突
- **左移守衛**: `traceability-system.md` Step 0 通用 ID 指派協議
- **更新 Skill**: `traceability-system.md` ✅, `root-cause-leftshift.md` ✅, `risk-management.md` ✅, `tech-debt-collect.md` ✅
- **守衛驗證證據**: Step 0 明確定義 traceability-matrix.md 為唯一 SSOT，6 步強制流程，三項禁止行為
### 變更 #5: Pipeline Position 客觀判定守衛 + Step 12.4 表格模板修正

- **日期**: 2026-05-14T08:00+08:00
- **類型**: MODIFY
- **檔案**: `AGENTS.md` (Step 12.2 守衛, Step 12.4 表格模板), `docs/workflow-state.md` (Pipeline Position 修正), `docs/traceability-matrix.md` (UC-010/011 描述修正, +LESSON-032)
- **影響 ID**: LESSON-032
- **嚴重度**: MAJOR (系統性誤報)
- **微驗證**: PASS

**根因**：Step 12.2 缺少客觀判定機制，Pipeline Position 基於「本次在做什麼」的主觀描述，而非追溯矩陣中實際產出物的存在性。導致連續多個 session 錯誤報告 Stage 3，但 TC-001~009 等 Stage 8 產出物早已存在。

### LESSON-032: Pipeline Position 基於主觀描述而非客觀產出物

- **根因分類**: GOVERNANCE_BYPASS
- **根因描述**: Step 12.2/12.3 更新 Pipeline Position 時僅依「本次做了什麼」設定，未比對 traceability-matrix.md 中的實際產出物，導致系統性位置漂移
- **5 Whys**:
  1. 為什麼 Position 錯誤？→ 每個 session 更新時只看「本次在做什麼」
  2. 為什麼不看實際產出物？→ Step 12.2 未要求比對追溯矩陣
  3. 為什麼未要求？→ 原設計假設 session 工作推進 Pipeline，未預見治理迭代場景
  4. 為什麼未預見？→ self-bootstrap 完成後的持續改善是新模式
  5. 為什麼無守衛？→ 缺少「Position 必須基於產出物事實」的不變式
- **瓶頸**: Step 12.2 缺少客觀判定機制
- **左移守衛**: `AGENTS.md` Step 12.2 加入 LESSON-032 守衛
- **更新 Skill**: `AGENTS.md` ✅
- **守衛驗證證據**: Step 12.2 step 3 明確要求讀取追溯矩陣覆蓋統計判定 Position

## 關聯產出物
### 變更 #6: 協議執行繞道 RCA + 範圍限定詞保護

- **日期**: 2026-05-14T08:08+08:00
- **類型**: MODIFY
- **檔案**: `AGENTS.md` (Step 輸出協議 LESSON-033 守衛, Factual Reporting LESSON-034 守衛)
- **影響 ID**: LESSON-033, LESSON-034
- **嚴重度**: CRITICAL (系統性協議繞道)

### LESSON-033: 多輪回覆未執行 Step 0-12 完整協議

- **根因分類**: GOVERNANCE_BYPASS
- **根因描述**: AI 把「session」解讀為「整個對話」，認為 Step 0 只需做一次，違反「每次回覆」規定
- **5 Whys**:
  1. 為什麼沒輸出？→ AI 認為 Step 0 已在 session 開始時完成
  2. 為什麼這樣認為？→ Step 0 標題「Session Gate — 啟動」暗示一次性
  3. 為什麼「每次回覆」規則沒覆蓋？→ 與 Step 0 標題存在語意張力
  4. 為什麼未解決？→ ADR-GOV-024 聚焦「禁止靜默跳過」未處理頻率定義
  5. 為什麼？→ 缺少「每個 prompt = 完整協議觸發」不變式
- **瓶頸**: Step 輸出協議缺少明確的觸發頻率定義
- **左移守衛**: `AGENTS.md` Step 輸出協議加入 LESSON-033 守衛
- **更新 Skill**: `AGENTS.md` ✅
- **守衛驗證證據**: 明確宣告「每一個 prompt 視為一個完整的變更請求」

### LESSON-034: AI 暗中縮小使用者明確指定的範圍 (ASSUMPTION_OVERRIDE)

- **根因分類**: ASSUMPTION_OVERRIDE
- **根因描述**: 使用者明確使用「窮舉」「端對端」「所有」等範圍限定詞，AI 判斷「列出全部不實際」後自行縮小範圍為 new/modified only，未報告替代方案
- **5 Whys**:
  1. 為什麼模板指令與意圖矛盾？→ AI 自行縮小範圍
  2. 為什麼自行縮小？→ AI 用「實際性」判斷覆蓋使用者要求
  3. 為什麼允許覆蓋？→ ADR-GOV-015 禁止但 AI 未識別此場景
  4. 為什麼未識別？→ AI 不認為「模板設計」屬於「可能偏離意圖」場景
  5. 為什麼？→ 缺少「範圍限定詞 = 不可縮小」守衛
- **瓶頸**: Factual Reporting 區段缺少範圍限定詞保護規則
- **左移守衛**: `AGENTS.md` Factual Reporting 區段加入 LESSON-034 守衛
- **更新 Skill**: `AGENTS.md` ✅
- **守衛驗證證據**: 明確列出「窮舉/全面/端對端/所有」為保護詞，縮小範圍 = GOVERNANCE_BYPASS

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 技術債 | N/A | 本 ADR 無新增技術債 |
| 風險 | RISK-005 | ADR-TEMPLATE 欄位過長導致 LLM 省略 |
| 教訓 | LESSON-029 | RISK/DEBT 追溯孤兒 |
| 教訓 | LESSON-030 | RISK/DEBT ID 衝突（窮舉搜尋缺失） |
| 教訓 | LESSON-031 | ID 指派缺乏統一 SSOT |
| 教訓 | LESSON-032 | Pipeline Position 基於主觀描述而非客觀產出物 |
| 教訓 | LESSON-033 | 多輪回覆未執行 Step 0-12 完整協議 |
| 教訓 | LESSON-034 | AI 暗中縮小使用者明確指定的範圍 (ASSUMPTION_OVERRIDE) |
