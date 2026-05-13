# ADR-GOV-022: docs/ 執行邏輯吸收至 skills/ 實現 Skill 自足性

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-001, FR-002, FR-003, FR-005, FR-019, FR-022, FR-023, ADR-GOV-020
> **取代**: N/A（擴展 ADR-GOV-020 的執行層級）

---

## 背景

- **觸發 Stage/Phase**: Stage 3（治理架構自舉，第二輪自我審計）
- **觸發事件**: HITL 要求全面追溯審計 — 確認 `docs/` 下每個檔案的執行方法論是否可僅透過 `skills/` 完整重現
- **前置條件**: ADR-GOV-020 已將 AGENTS.md 重塑為 Step 0-12 協議，但仍保留 11 個 `→ READ: $FRAMEWORK_ROOT/docs/` 指令
- **約束**: 
  - skills/ 必須自足，不依賴 docs/ 即可執行全套治理邏輯
  - docs/ 在其他 repository 下是專案產出物位置，不可與框架執行邏輯混用

## 決策

我們決定將 `$FRAMEWORK_ROOT/docs/` 中的所有執行方法論全數吸收至 `skills/workflow-skills/`，使 AGENTS.md 的所有 Step 僅依賴 `→ INVOKE: skill` 而非 `→ READ: docs/`：

1. **15 個新 Skill 建立**：
   - Phase 編排 Skills (5)：phase-0/1/2/9/10-orchestration.md
   - Stage 審查維度 Skills (6)：stage-3/4/5/6/7/8-dimensions.md
   - 治理協議 Skills (4)：traceability-system.md, change-management-protocol.md, adr-governance.md, tech-debt-framework.md

2. **1 個既有 Skill 強化**：
   - impact-analysis-exec.md (43→90 行)：新增 MAJOR M1-M4 處理、FR-022 全方向追溯、禁止行為

3. **AGENTS.md 指令遷移**：
   - 11 個 `→ READ: $FRAMEWORK_ROOT/docs/phases|stages|governance/` 全部替換為 `→ INVOKE:`
   - Repository Scope Rules 重寫：skills/ = 唯一執行來源，docs/ = 歷史參照

4. **Skill Routing 表擴充**：
   - 新增「治理」分類（4 個 skill）
   - 新增「Phase/Stage 編排」分類（11 個 skill）

## 理由

- **支持證據**: 追溯審計發現 34 個方法論缺口 — docs/ 中的審查維度表、Agent β 收斂規則、ADR 決策流程、變更管理 6 步驟等均未封裝為 skill
- **權衡取捨**: 15 個新 skill 增加約 40KB 框架體積；但消除了對 docs/ 的執行依賴，使跨 repository 部署零摩擦
- **風險接受**: skill 數量從 17 增至 32 可能增加 context window 壓力 → 緩解措施：skill 按需讀取（INVOKE 時才載入），不會同時全部佔用 context

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------|
| 維持 READ docs/ | 無遷移工作 | 跨 repo 需攜帶 docs/；docs/ 在目標 repo 有語意衝突 | 違反自足性原則 |
| 合併所有 skill 為少量大檔案 | 減少檔案數 | 違反 SRP；每次 INVOKE 載入不必要內容 | 違反 Ockham's Razor |
| 僅遷移部分（保留 phase docs） | 最小變更 | 不完整；仍有 docs/ 依賴 | 半途而廢 |

## 後果

**正面**：
- AI 執行其他 repository 時僅需讀取 `skills/workflow-skills/` 即可完整執行全套邏輯
- `docs/` 在框架層面降為「歷史參照」，消除跨 repo 語意衝突
- 所有審查維度（T1-T7, A-V, OA-OD, F1-F6, B1-B5, D1-D5）封裝於對應 skill，可獨立演化

**負面**：
- 32 個 skill 檔案的維護負擔增加
- docs/ 中的原始內容可能隨時間與 skills/ 產生版本漂移

## 影響分析

- **爆炸半徑**: 18 個檔案（15 CREATE + 3 MODIFY）
- **跨 Stage 影響**: 全部 Stage/Phase（結構性變更）
- **嚴重度**: MAJOR
- **受影響 ID**: FR-001, FR-002, FR-003, FR-005, FR-019, FR-022, FR-023

## 流程變更

- **修改前規則**: AGENTS.md Step 1-11 使用 `→ READ: $FRAMEWORK_ROOT/docs/phases|stages|governance/` 取得執行定義
- **修改後規則**: AGENTS.md Step 1-11 使用 `→ INVOKE: skills/workflow-skills/*.md` 取得執行定義；docs/ 僅用於 ADR 歷史回溯
- **影響範圍**: 所有 Phase/Stage 的執行來源
- **過渡期**: 無（一次性全量替換）

## 變更紀錄 (Implementation Records)

### 變更 #1: 15 新 Skill 建立 + 1 Skill 強化 + AGENTS.md 指令遷移

- **日期**: 2026-05-14T05:15+08:00
- **類型**: CREATE + MODIFY
- **檔案**:
  - CREATE: phase-0-orchestration.md, phase-1-understanding.md, phase-2-orchestration.md, phase-9-orchestration.md, phase-10-orchestration.md
  - CREATE: stage-3-dimensions.md, stage-4-dimensions.md, stage-5-dimensions.md, stage-6-dimensions.md, stage-7-dimensions.md, stage-8-dimensions.md
  - CREATE: traceability-system.md, change-management-protocol.md, adr-governance.md, tech-debt-framework.md
  - MODIFY: impact-analysis-exec.md (43→90 行)
  - MODIFY: AGENTS.md (11 READ→INVOKE, Scope Rules 重寫, Skill Routing 擴充)
  - MODIFY: workflow-state.md (Pipeline Position + Session Summary 更新)
- **影響 ID**: FR-001~FR-005, FR-019, FR-022, FR-023
- **爆炸半徑**: 18
- **嚴重度**: MAJOR
- **微驗證**: PGVG 2a-2e 全通過 ✅
- **跨切面驗證**: AGENTS.md 零 READ 指令 ✅

**變更明細**:

| # | 檔案 | 修正內容 | 根因類別 |
|---|------|----------|----------|
| 1-5 | phase-*-orchestration.md | 封裝 Phase 0/1/2/9/10 編排邏輯 | METHODOLOGY_ABSORPTION |
| 6-11 | stage-*-dimensions.md | 封裝 Stage 3-8 審查維度 + 出口閘門 | METHODOLOGY_ABSORPTION |
| 12 | traceability-system.md | 封裝 ID 規格 + 追溯關係定義 | METHODOLOGY_ABSORPTION |
| 13 | change-management-protocol.md | 封裝 CM Steps 0-5 + PGVG | METHODOLOGY_ABSORPTION |
| 14 | adr-governance.md | 封裝 ADR 生命週期 + DU 理論 | METHODOLOGY_ABSORPTION |
| 15 | tech-debt-framework.md | 封裝技術債四象限 + RICE | METHODOLOGY_ABSORPTION |
| 16 | impact-analysis-exec.md | 強化 M1-M4 + FR-022 + 禁止行為 | SKILL_ENRICHMENT |
| 17 | AGENTS.md | READ→INVOKE 全部替換 | ARCHITECTURE_EVOLUTION |
| 18 | workflow-state.md | 狀態更新 | PROCESS_MAINTENANCE |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-022: 執行邏輯與參考文件混合導致跨 repo 部署摩擦

- **根因分類**: ARCHITECTURE_EROSION
- **根因描述**: 框架初始設計將執行方法論寫入 docs/（因 docs/ 是自然的文件放置點），但 docs/ 在目標 repo 有不同語意（專案產出物），導致跨 repo 執行時需要讀取不屬於該 repo 的 docs/
- **5 Whys**:
  1. 為什麼 AI 執行其他 repo 時仍需讀取 ai_coding/docs/？→ AGENTS.md 有 READ docs/ 指令
  2. 為什麼有 READ docs/ 指令？→ 執行方法論寫在 docs/ 的 phases/stages/governance/
  3. 為什麼方法論寫在 docs/？→ 初始設計時 docs/ 是自然的文件位置
  4. 為什麼沒有在 ADR-GOV-020 時一併遷移？→ 當時專注於 AGENTS.md 結構化，未意識到 docs/ 路徑依賴
  5. 結構性修正？→ 建立「執行邏輯 = skills/」「歷史紀錄 = docs/」的明確分界
- **瓶頸識別**:
  - 問題發生點: 框架初始設計時 / docs/ 路徑選擇時
  - 逃逸路徑: 初始設計將執行方法論寫入 docs/ → ADR-GOV-020 時未識別路徑依賴
  - 最早可偵測點: AGENTS.md 的 Repository Scope Rules 定義時
  - 瓶頸位置: `AGENTS.md` Repository Scope Rules 缺少執行/參照分界規則
  - 介入類型: NEW_GUARD
  - 預期覆蓋: 執行邏輯與參考文件混合導致的跨 repo 部署摩擦
- **左移守衛**: AGENTS.md Repository Scope Rules 新增「關鍵原則」段落 ✅
- **更新 Skill**: 所有 15 個新 skill 均以 `skills/workflow-skills/` 為路徑
- **守衛驗證證據**: AGENTS.md 中零個 READ $FRAMEWORK_ROOT/docs/ 指令

### LESSON-023: MAJOR 級變更未執行 CM 流程（GUARD_STRENGTHENING）

- **變更來源**: ADR-GOV-022 變更 #1
- **變更類型**: FIX（CM 補跑）
- **根因分類**: GOVERNANCE_BYPASS
- **根因描述**: 18 次寫入全部跳過 CM。CM 是後置步驟（寫完後才做），AI 在批次產出模式下系統性遺忘。
- **5 Whys**:
  1. 為什麼 CM 沒有執行？→ AI 專注於大量檔案產出
  2. 為什麼會忽略？→ CM 是「寫完後才做」的後置步驟，沒有前置阻擋機制
  3. 為什麼沒有前置阻擋？→ change-management-protocol.md 僅定義「觸發條件：任何寫入」但無強制宣告格式
  4. 為什麼 Step 12 沒攔截？→ Step 12 也在同一 session 被跳過（整個 session 的治理流程都缺失）
  5. 結構性修正？→ 將 CM 從後置改為前置：寫入前強制輸出 CM-GATE 宣告，使跳過行為可觀測
- **瓶頸識別**:
  - 問題發生點: 批次檔案產出時
  - 逃逸路徑: CM 是後置步驟 → AI 在產出模式下注意力全在產出 → Step 12 也被跳過
  - 最早可偵測點: 每次寫入前
  - 瓶頸位置: `change-management-protocol.md` CM 為後置設計，無前置宣告機制
  - 介入類型: NEW_GUARD
  - 預期覆蓋: 所有批次產出時的 CM 跳過
- **左移守衛**: Inline CM-GATE 宣告機制
- **更新的 Skill**:
  - `change-management-protocol.md` 新增「Inline CM-GATE」段落和「Batch Mode」段落（本 session 修改，新增約 52 行）
  - `AGENTS.md` 新增 Principle #14（本 session 修改，line 34）
  - `AGENTS.md` Step 12.1 重寫為窮舉式檔案列舉（本 session 修改，line 361-383）
- **守衛驗證證據**: CM-GATE 格式定義於 change-management-protocol.md；AGENTS.md Principle #14 在每次 session 載入時可見，作為持續提醒

### LESSON-024: CM 後置設計導致系統性跳過

- **變更來源**: ADR-GOV-022 變更 #2
- **變更類型**: FIX
- **根因分類**: PROCESS_GAP
- **根因描述**: CM 設計為「寫入後觸發」，但 AI 的工作模式是批次產出，後置觸發在認知上容易被延遲至「永遠不做」
- **5 Whys**:
  1. 為什麼 CM 被跳過？→ CM 是後置步驟
  2. 為什麼後置步驟會被跳過？→ AI 在產出模式下的注意力全部在下一個產出，不在回顧
  3. 為什麼產出模式不包含治理？→ 治理和產出是分離的流程，沒有結構性耦合
  4. 為什麼沒有結構性耦合？→ 初始設計假設 AI 有完美記憶和自律
  5. 結構性修正？→ CM-GATE 作為寫入的前置條件，將治理嵌入產出行為本身
- **瓶頸識別**:
  - 問題發生點: CM 設計時
  - 逃逸路徑: CM 為後置觸發 → AI 延遲至「永遠不做」
  - 最早可偵測點: 寫入行為前
  - 瓶頸位置: `change-management-protocol.md` 缺少前置 CM-GATE 宣告格式
  - 介入類型: NEW_GUARD
  - 預期覆蓋: CM 後置設計導致的系統性跳過
- **左移守衛**: `CM-GATE: [file] | Type | Class | ADR` 宣告格式
- **更新的 Skill**: `change-management-protocol.md` 新增 Inline CM-GATE 段落
- **守衛驗證證據**: Step 12.1 步驟 B 的逐一檢查偵測 CM-GATE 缺失

### LESSON-025: RCA 始終由使用者要求才執行（Meta-RCA 失敗）

- **變更來源**: ADR-GOV-022 變更 #2
- **變更類型**: FIX
- **根因分類**: DECLARATION_IMPLEMENTATION_GAP
- **根因描述**: root-cause-leftshift.md 宣稱「所有變更，無例外」，但實際上 AI 從未自主觸發完整 RCA，每次都是使用者發現遺漏後要求才執行
- **5 Whys**:
  1. 為什麼 RCA 沒有自主觸發？→ AI 將 RCA 視為「可選的後處理」
  2. 為什麼被視為可選？→ root-cause-leftshift.md 說「禁止 N/A」但沒有自檢機制偵測 AI 是否真的執行了
  3. 為什麼沒有自檢機制？→ 假設宣告等於執行（DECLARATION_IMPLEMENTATION_GAP）
  4. 為什麼會有這個假設？→ 治理系統用文字指令控制 AI 行為，但文字指令本質上是建議而非強制
  5. 結構性修正？→ 在 root-cause-leftshift.md 加入 Meta-RCA 觸發器：執行 RCA 時先自檢「這是 AI 自主觸發還是使用者要求的？」
- **瓶頸識別**:
  - 問題發生點: RCA 執行時
  - 逃逸路徑: root-cause-leftshift.md 宣稱「無例外」但無自檢機制 → AI 將 RCA 視為可選
  - 最早可偵測點: root-cause-leftshift.md 觸發時
  - 瓶頸位置: `root-cause-leftshift.md` 缺少 Meta-RCA 觸發器
  - 介入類型: STEP_ADDITION
  - 預期覆蓋: 所有 RCA 未自主觸發的情況
- **左移守衛**: Meta-RCA 觸發器 + 窮舉式 Session 掃描協議
- **更新的 Skill**:
  - `root-cause-leftshift.md` 新增「Meta-RCA 觸發器」段落和「窮舉式 Session 掃描協議」（本 session 修改，新增約 33 行，位於 Step 1 前）
  - `AGENTS.md` Step 12.1 新增「步驟 C: Meta-RCA 自檢」（本 session 修改）
- **守衛驗證證據**: Meta-RCA 的自檢問題 1（「本次 RCA 是 AI 自主觸發還是使用者要求？」）直接偵測本問題模式。若答案為「使用者要求」，則自動觸發額外 LESSON。

### LESSON-026: LESSON 宣稱守衛有效但守衛已失敗

- **變更來源**: ADR-GOV-022 變更 #2
- **變更類型**: FIX
- **根因分類**: DECLARATION_IMPLEMENTATION_GAP
- **根因描述**: LESSON-023 原始版本宣稱「左移守衛: Step 12 CM 前置斷言確保此類遺漏會被攔截 ✅」，但 Step 12 在同一 session 也被跳過，證明該守衛無效
- **5 Whys**:
  1. 為什麼宣稱有效的守衛實際無效？→ AI 沒有驗證守衛在本 session 是否真的攔截了問題
  2. 為什麼沒有驗證？→ LESSON 格式沒有要求「守衛是否在本 session 有效」的驗證
  3. 為什麼 LESSON 格式不要求？→ 初始設計假設守衛的存在等於守衛的有效性
  4. 為什麼存在不等於有效？→ 守衛可能被 AI 自身跳過，使其形同虛設
  5. 結構性修正？→ 在 micro-validation.md Step 7 和 change-management-protocol.md 加入「LESSON-to-Skill 驗證閘門」和「宣告-實施缺口偵測」
- **瓶頸識別**:
  - 問題發生點: LESSON 記錄時
  - 逃逸路徑: LESSON 格式不要求驗證守衛有效性 → AI 假設存在 = 有效
  - 最早可偵測點: micro-validation.md Step 7
  - 瓶頸位置: `micro-validation.md` Step 7 缺少 LESSON-to-Skill 驗證閘門
  - 介入類型: STEP_ADDITION
  - 預期覆蓋: 所有守衛宣稱有效但實際已失敗的情況
- **左移守衛**: DECLARATION_IMPLEMENTATION_GAP Guard + LESSON-to-Skill 驗證閘門
- **更新的 Skill**:
  - `micro-validation.md` Step 7 新增第 6 點「LESSON-to-Skill 驗證閘門」（本 session 修改）
  - `change-management-protocol.md` 新增「宣告-實施缺口偵測」段落，含 3 個禁止模式（本 session 修改）
- **守衛驗證證據**: 禁止模式明確列出 3 種無效宣告模式。本 session 的 LESSON-023 原始版本正好觸犯第 1 種模式（「宣稱既有守衛有效，但該守衛明顯已失敗」），證明偵測有效。

## 關聯產出物

| 類型 | ID | 說明 |
|------|-----|------|
| 教訓 | LESSON-022 | 執行邏輯與參考文件分界 |
| 教訓 | LESSON-023 | MAJOR 級變更的 CM 跳過（GUARD_STRENGTHENING） |
| 教訓 | LESSON-024 | CM 後置設計導致系統性跳過 → Inline CM-GATE |
| 教訓 | LESSON-025 | RCA 始終由使用者驅動 → Meta-RCA 觸發器 |
| 教訓 | LESSON-026 | LESSON 宣稱守衛有效但守衛已失敗 → 宣告-實施缺口偵測 |
| 風險 | RISK-001 | docs/ 與 skills/ 版本漂移 |
| 技術債 | DEBT-001 | docs/ 下原始方法論檔案未標記為 Reference Only |
