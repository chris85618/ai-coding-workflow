# Change Log — Antigravity Integrated Workflow System

> **格式**：IMP-xxx (變更紀錄) + LESSON-xxx (根因左移)
> **治理**：docs/governance/CHANGE-MANAGEMENT.md

---

## IMP-001: project-charter.md backtick 修復

- **類型**: FIX
- **檔案**: docs/project-charter.md (line 5)
- **時間**: Stage 5 入口自驗
- **影響 ID**: 無 ID 受影響（格式問題）
- **爆炸半徑**: 0
- **嚴重度**: COSMETIC
- **微驗證**: 未執行（當時 8 步協議尚未建立）

### LESSON-001

- **根因分類**: FORMAT_ERROR + LLM_HALLUCINATION
- **5 Whys**:
  1. 為什麼 backtick 格式錯誤？→ LLM 生成時機率性遺漏開頭 backtick
  2. 為什麼沒被阻止？→ s2c-charter.md 無格式驗證步驟
  3. 為什麼驗證沒偵測？→ 微驗證無 Step 0 格式驗證
  4. 為什麼流程允許？→ 初次建立不被視為「變更」
  5. 結構性修正？→ **每次寫入（含 CREATE）觸發格式 lint**
- **左移守衛**: micro-validation.md 新增 Step 0（格式驗證）
- **更新 Skill**: micro-validation.md ✅

---

## IMP-002: UC-002/006/009 缺少 CLS 覆蓋

- **類型**: FIX
- **檔案**: docs/domain-model.md
- **時間**: Stage 6 入口自驗
- **影響 ID**: CLS-010, CLS-011, CLS-012, EVT-005（新增）
- **爆炸半徑**: 4（新增 4 個 ID）
- **嚴重度**: MAJOR
- **微驗證**: 部分執行（更新矩陣但無 IMP-xxx）

### LESSON-002

- **根因分類**: COVERAGE_GAP + LLM_HALLUCINATION
- **5 Whys**:
  1. 為什麼 3 個 UC 沒有 CLS？→ 限界上下文表覆蓋 9/9 但 CLS 類別只定義了 6/9
  2. 為什麼沒被阻止？→ s2c-domain-model.md 無 UC↔CLS 覆蓋斷言
  3. 為什麼驗證沒偵測？→ 完成報告用泛稱 "9/9 UC 覆蓋" 未逐一列出
  4. 為什麼流程允許？→ LLM 將「限界上下文涵蓋」等同於「CLS 建模完成」
  5. 結構性修正？→ **s2c-domain-model.md 加入逐一 UC→CLS 映射驗證 + 覆蓋斷言必須從實際內容 grep**
- **左移守衛**:
  - s2c-domain-model.md: 加入 "FOR each UC-xxx: ASSERT exists CLS with trace to UC-xxx"
  - micro-validation.md Step 4: 加入交叉覆蓋驗證
  - completion-check.md: 加入自動化計數
- **更新 Skill**: micro-validation.md ✅, s2c-domain-model.md ✅, completion-check.md ✅

---

## IMP-003: TC-005/008 測試斷言模式錯誤

- **類型**: FIX
- **檔案**: docs/test-cases.md (TC-005 line 99, TC-008 line 118)
- **時間**: Stage 8 自驗
- **影響 ID**: TC-005, TC-008
- **爆炸半徑**: 2
- **嚴重度**: MINOR
- **微驗證**: 未執行

### LESSON-003

- **根因分類**: LLM_HALLUCINATION
- **5 Whys**:
  1. 為什麼斷言錯誤？→ 使用 multi-keyword regex（`COSMETIC.*MINOR.*MODERATE.*MAJOR`）假設同行
  2. 為什麼沒被阻止？→ TC 生成無測試模式指引
  3. 為什麼驗證沒偵測？→ TC 未在生成後立即執行
  4. 為什麼流程允許？→ LLM 未考慮目標文件的多行佈局
  5. 結構性修正？→ **TC 斷言規範: 每個斷言測試一個關鍵字，不合併多關鍵字 + TC 生成後立即執行一遍**
- **左移守衛**: s2c-bdd-scenarios.md 加入斷言模式指引
- **更新 Skill**: s2c-bdd-scenarios.md ✅

---

## IMP-004: inline S2C code blocks 殘留

- **類型**: FIX
- **檔案**: docs/stages/stage-4,5,7,8
- **時間**: 初始整合階段
- **影響 ID**: 無直接 ID（結構問題）
- **爆炸半徑**: 4 files
- **嚴重度**: MODERATE
- **微驗證**: 未執行

### LESSON-004

- **根因分類**: PROCESS_GAP
- **5 Whys**:
  1. 為什麼有殘留？→ 整合 vibe-coding 時直接複製內容
  2. 為什麼沒被阻止？→ 無「外來內容掃描」步驟
  3. 為什麼驗證沒偵測？→ 微驗證不檢查 inline code 的來源
  4. 為什麼流程允許？→ 整合作業未經 Stage 3-8 管線
  5. 結構性修正？→ **micro-validation Step 0 加入外來殘留掃描（grep "from vibe", inline code blocks）**
- **左移守衛**: micro-validation.md Step 0 已更新 ✅
- **更新 Skill**: micro-validation.md ✅

---

## IMP-005: 追溯矩陣覆蓋統計手動計數錯誤

- **類型**: FIX
- **檔案**: docs/traceability-matrix.md（覆蓋統計表）
- **時間**: 每個 Stage 轉換
- **影響 ID**: 無直接 ID（統計問題）
- **爆炸半徑**: 0
- **嚴重度**: MINOR
- **微驗證**: 未執行

### LESSON-005

- **根因分類**: COVERAGE_GAP + LLM_HALLUCINATION
- **5 Whys**:
  1. 為什麼統計錯誤？→ LLM 從記憶報告數字而非從文件計數
  2. 為什麼沒被阻止？→ 無自動化計數驗證
  3. 為什麼驗證沒偵測？→ 微驗證依賴 LLM 自我報告
  4. 為什麼流程允許？→ completion-check.md 無自動化計數步驟
  5. 結構性修正？→ **completion-check.md 強制從文件 grep 計數 + 微驗證 Step 1 不接受泛稱覆蓋**
- **左移守衛**: micro-validation.md Step 1 LLM Guard 已更新 ✅, completion-check.md (待更新)
- **更新 Skill**: micro-validation.md ✅, completion-check.md ✅

---

## IMP-006: 全庫自我檢驗批次修正

- **日期**: 2026-05-13T23:27+08:00
- **觸發**: Phase 10 /retro 自我檢驗
- **嚴重度**: MODERATE (blast_radius=14, cross_stage=ALL)
- **修正檔案** (12 個):

| # | 檔案 | 修正內容 | 嚴重度 |
|---|------|----------|--------|
| 1 | CLAUDE.md | 移除「精簡路徑」，改為「無簡化路徑」 | CRITICAL |
| 2 | CLAUDE.md | 雙Agent協議補 Step M（4步→5步） | CRITICAL |
| 3 | CLAUDE.md | Phase 9 補 /document-release | MAJOR |
| 4 | CLAUDE.md | Phase 10 補 技術債更新 | MAJOR |
| 5 | WORKFLOW.md | adr/ listing 補 ADR-GOV-001.md | MAJOR |
| 6 | WORKFLOW.md | 呼叫鏈補 root-cause-leftshift.md | MAJOR |
| 7 | README.md | 移除「825 行」過期數字 | MODERATE |
| 8 | README.md | 移除「精簡路徑」 | MODERATE |
| 9 | requirements.md | FR-007「6 步」→「8 步」 | MODERATE |
| 10 | TRACEABILITY.md | 微驗證迴圈 6 步→8 步 | MODERATE |
| 11 | project-charter.md | governance/ (3)→(5), Skills 13→14 | MODERATE |
| 12 | domain-model.md | CLS-009 補缺失 ``` | MINOR |
| 13 | GEMINI.md | 路徑反斜線→正斜線 | MINOR |
| 14 | 6 個檔案 | docs/impact-log.md→docs/change-log.md | MINOR |
| 15 | security-audit-stage8.md | 技能檔案 13→14 | MINOR |

### LESSON-006: 跨檔案增量演化同步斷裂

- **根因**: 治理文件在多次迭代中增量演化（新增 Step 0/7、新增 ADR-GOV-001、新增 root-cause-leftshift.md），但每次演化僅更新了直接相關文件，未觸發全庫交叉引用掃描
- **5 Whys**:
  1. 為什麼 CLAUDE.md 有精簡路徑？→ 建立時從較早版本複製，之後 WORKFLOW.md 才移除
  2. 為什麼沒被偵測？→ 微驗證僅驗證 ID 追溯，不驗證跨檔案 policy 一致性
  3. 為什麼 impact-log.md 幽靈引用存在？→ 改名為 change-log.md 時未全庫 grep
  4. 為什麼 6 步/8 步不一致？→ ALG-002 升級時只改了 CHANGE-MANAGEMENT.md
  5. 結構性修正？→ **每次增量演化後，強制執行跨檔案 grep 掃描 + policy 一致性檢查**
- **左移守衛**: ~~自我檢驗流程已驗證此模式~~ → **守衛不足，已觸發 GUARD_STRENGTHENING（見 IMP-007）**
- **更新 Skill**: micro-validation.md Step 0 ← 不足（僅格式檢查，不含跨檔案 grep）
- **守衛強化歷程**:
  - 2026-05-13 初版守衛: micro-validation.md Step 0（僅格式 lint）
  - 2026-05-14 GUARD_STRENGTHENING: 根因重現 → 守衛升級至 CHANGE-MANAGEMENT Step 5（跨切面一致性驗證）+ Step 2f（FR/NFR 合規驗證）+ micro-validation.md Step 5.5（全方向連結追溯）

---

## IMP-007: 全鏈影響追溯 + 跨切面一致性驗證制度化

- **日期**: 2026-05-14T00:35+08:00
- **類型**: mixed (CREATE + MODIFY + FIX)
- **觸發**: HITL 需求（FR-022/023/024/025 制度化 + 自我驗證修正）
- **嚴重度**: MAJOR (blast_radius=14 issues across 9 files, cross_stage=ALL)
- **微驗證**: PASS（Step 0-7 + 5.5/5.7 全數通過）
- **PGVG**: PASS（2a-2f 全數通過，計數驗證 120 ID 確認）
- **跨切面驗證**: PASS（Step 5 首次執行，發現 14 issues 全數修正）

### 變更明細

**CREATE（新增 ID）**:
| ID | 描述 | 追溯 |
|----|------|------|
| FR-024 | 跨切面一致性驗證 | FEA-002, FEA-003 |
| FR-025 | 治理文件 FR/NFR 合規驗證 | FEA-002, FEA-003 |

**MODIFY（功能增強）**:
| 檔案 | 變更 |
|------|------|
| micro-validation.md | +Step 5.5（全方向追溯）、+Step 5.7（LESSON 重用） |
| CHANGE-MANAGEMENT.md | +Step 2f（FR/NFR 合規）、+Step 5（跨切面驗證）、Step 3 更新 |
| WORKFLOW.md | 出口閘門擴充（FR-022/023/跨切面）、核心原則 #3 步數更新 |
| algorithm-specs.md | ALG-002 +lateral/lesson checks、ALG-003 +lateral blast |
| TRACEABILITY.md | 驗證迴圈步數更新 |

**FIX（過期引用修正，14 items）**:
| 檔案 | 修正 | 根因 |
|------|------|------|
| requirements.md | FEA 範圍、FR-007 步數、FR-018 文件數 | COVERAGE_GAP |
| use-cases.md | FR 範圍 | COVERAGE_GAP |
| scope-definition.md | FEA 計數 | COVERAGE_GAP |
| traceability-matrix.md | 時間戳、UC 覆蓋率、ID 總數 | COVERAGE_GAP |
| algorithm-specs.md | 輸入範圍、步數、理論表 | COVERAGE_GAP |
| CHANGE-MANAGEMENT.md | 步數描述 | COVERAGE_GAP |
| TRACEABILITY.md | 步數描述 | COVERAGE_GAP |
| WORKFLOW.md | 出口閘門描述、步數 | COVERAGE_GAP |

### LESSON-007: 守衛宣稱與實際實作不符

- **根因分類**: PROCESS_GAP
- **根因描述**: LESSON-006 宣稱「micro-validation.md Step 0 已涵蓋交叉覆蓋驗證」，但 Step 0 實際只有格式 lint（backtick、表格、外來殘留），不包含跨檔案 grep 掃描。守衛宣稱與實際守衛能力不符。
- **5 Whys**:
  1. 為什麼 LESSON-006 守衛失敗？→ 宣稱 Step 0 涵蓋但實際不涵蓋
  2. 為什麼宣稱不準確？→ 記錄 LESSON 時未驗證守衛實際能力
  3. 為什麼沒有驗證機制？→ LESSON 記錄流程不包含「守衛能力驗證」步驟
  4. 為什麼流程有這個缺口？→ root-cause-leftshift.md 只要求「更新 skill」，不要求「驗證更新後的 skill 能攔截重現」
  5. 結構性修正？→ **root-cause-leftshift.md 已有「驗證左移後的規則可防止重現」步驟（Step 3.5），但需在 LESSON 記錄格式中加入「守衛驗證證據」欄位**
- **左移守衛**:
  - FR-023 LESSON 重用機制 → Step 5.7 在 FIX 時掃描既有 LESSON，防止重複
  - FR-025 治理文件合規驗證 → Step 2f 在修改治理文件時驗證 FR/NFR 滿足度
  - CHANGE-MANAGEMENT Step 5 → 跨切面變更時全矩陣重驗證
- **更新 Skill**: CHANGE-MANAGEMENT.md ✅ (Step 2f + Step 5), micro-validation.md ✅ (Step 5.5/5.7)

---

## IMP-008: 全面追溯審計 — iter-loop AI-first 模型傳播修正

- **日期**: 2026-05-14T01:43+08:00
- **類型**: FIX (MODIFY × 13 files)
- **觸發**: 使用者指令「仔細掃描每一個 docs/ 下的文件是否可透過追溯矩陣完整追溯到 skills 下的具體內容」
- **爆炸半徑**: 13 個檔案，跨 Phase 2 / Stage 3-8 / Phase 9 / skills/ / docs/
- **嚴重度**: MAJOR（跨 8+ Stage/Phase）
- **微驗證**: PASS（Step 0-7 + 5.5/5.7 全數通過）
- **PGVG**: PASS（2a-2e 通過；2e: grep「繼續迭代」= 0 殘留；grep「三選項」= 0 殘留）
- **跨切面驗證**: PASS（Step 5 執行，13 個檔案交叉掃描，過期引用清零）

### 變更明細

| # | 檔案 | 修正內容 | 根因類別 |
|---|------|----------|----------|
| 1-6 | `docs/stages/stage-{3-8}*.md` | 迭代協議：加 Step F + 改 Step C 為 2 選項 + 加 iter-loop.md 引用 | PROCESS_GAP |
| 7 | `docs/phases/phase-2-project-analysis.md` | 移除未定義 `ASM-xxx` 孤兒前綴 | NAMING_INCONSISTENCY |
| 8 | `skills/workflow-skills/s2c-requirements.md` | 新增 PGVG 區塊（與其他 s2c-*.md 對齊）| COVERAGE_GAP |
| 9 | `docs/phases/phase-9-ship-deploy.md` | 新增 `completion-check.md` skill 引用 | PROCESS_GAP |
| 10 | `docs/requirements.md` | FR-013 補完整 3 種不動點狀態；FR-014 改為 AI-first 2 選項描述 | SEMANTIC_DRIFT |
| 11 | `docs/bdd-scenarios.md` | SC-003 場景更新反映 Step F + NOT_REACHED 自主繼續 | SEMANTIC_DRIFT |
| 12 | `docs/adr/ADR-TEMPLATE.md` | GATE 補充區塊改為 2 選項 AI-first 格式 | SEMANTIC_DRIFT |
| 13 | `docs/iteration-log.md` | HITL Decision 格式改為 2 選項 | SEMANTIC_DRIFT |

### 閘門重新驗證

- [x] Stage 3-8 出口閘門：iter-loop.md 引用一致 ✅
- [x] FR-013/014 追溯至 FEA-005 ✅
- [x] SC-003 追溯至 UC-003 + INV-003/004/005 ✅
- [x] ADR-TEMPLATE.md 追溯至 ADR-GOV-002 ✅
- [x] s2c-requirements.md PGVG 追溯至 FR-017 ✅

### LESSON-008: Skill 版本演化未觸發下游文件級聯更新

- **根因分類**: PROCESS_GAP
- **根因描述**: `skills/workflow-skills/iter-loop.md` 從「HITL-per-iteration（3 選項）」演化為「AI-first 收斂（Step F + 2 選項）」，但沒有任何機制確保所有引用此 skill 的 docs/ 文件同步更新。Stage 3-8 文件各自包含了 iter-loop 的「快照副本」，副本在 skill 升級後變成過期引用。
- **5 Whys**:
  1. 為什麼 Stage docs 仍有舊 3 選項？→ 文件在 iter-loop.md 升級前已建立，升級後未觸發 cascade 更新
  2. 為什麼沒有 cascade 更新？→ 無「Skill 版本升級 → 引用方掃描」協議
  3. 為什麼文件有 inline 副本而非直接引用？→ 建立時為說明具體化，未明確標注為「快照，需與 skill 同步」
  4. 為什麼無同步驗證？→ micro-validation Step 5.5 僅追溯 ID 連結，不追溯 skill 版本一致性
  5. 結構性修正？→ Stage 文件迭代協議區塊改為「引用 iter-loop.md + 本 Stage 具體化」格式，消除副本
- **左移守衛**:
  1. **格式不變量**：Stage 文件迭代協議必須以 `> 完整迭代協議定義見 skills/workflow-skills/iter-loop.md` 開頭（已實施 ✅）
  2. **Skill 升級 SOP**：修改 iter-loop.md 時，PGVG Step 2e 必須掃描 docs/stages/*.md 驗證協議一致性
- **更新 Skill**: stage-3 到 stage-8（加 iter-loop.md 引用）✅
- **守衛驗證證據**: 格式守衛已內嵌於 6 個 stage 文件，grep「完整迭代協議定義見」= 6 結果（全覆蓋）

**處理狀態**: ✅ 完成

---

## IMP-009: Session-End Hook 提前觸發 — CM Steps 2-5 缺少前置斷言

- **日期**: 2026-05-14T01:48+08:00
- **類型**: FIX (MODIFY × 3 files)
- **觸發**: 使用者 RCA 要求（「你在分析當前狀態&下一步時沒有繼續完成完整變更管理流程」）
- **爆炸半徑**: 3 個檔案（AGENTS.md, CHANGE-MANAGEMENT.md, change-log.md）
- **嚴重度**: MAJOR（影響所有含 FIX/MODIFY 的 session 的 CM 完整性）
- **微驗證**: PASS
- **根因分類**: PROCESS_GAP

### 變更明細

| 檔案 | 變更 |
|------|------|
| `AGENTS.md` | session_end_hook() 新增 Step 0 (CM 前置斷言 Precondition Gate) |
| `docs/governance/CHANGE-MANAGEMENT.md` | Step 6 新增顯式 Precondition Gate 區塊；新增 INV-CM-005 結構不變量 |
| `docs/change-log.md` | 寫入 IMP-009 + LESSON-009 |

### LESSON-009: CM 多步驟流程缺少「前置步驟完成」強制斷言

- **FIX 來源**: IMP-009
- **根因分類**: PROCESS_GAP
- **5 Whys**:
  1. 為什麼 Session-End Hook 在 CM Steps 2-5 未完成前觸發？→ AI 將「完成本輪檔案修改」（Step 1）視為 CM 流程完成
  2. 為什麼 AI 有這個誤判？→ CM Step 6 只寫「每次回覆前執行」，無 precondition 要求 Steps 0-5 已完成
  3. 為什麼 Step 6 沒有 precondition？→ 設計時假設「線性流程自然前進」，未考慮 AI 可能跳步
  4. 為什麼 AI 可能跳步？→ Step 4（根因左移）有「唯一免除條件」出口，AI 誤判可用此出口；Step 5 觸發條件需 AI 自主判斷是否「橫跨 2+ Stage」，判斷可能偏保守
  5. 結構性修正？→ Step 6 加入顯式前置斷言清單（每個 FIX/MODIFY 逐一確認 Steps 0-5 完成狀態）
- **左移守衛**:
  1. **AGENTS.md session_end_hook Step 0**：precondition_check() — FOR each FIX/MODIFY: ASSERT steps 0-5 complete（已實施 ✅）
  2. **CHANGE-MANAGEMENT.md Step 6 Precondition Gate**：顯式 precondition block（已實施 ✅）
  3. **INV-CM-005**：Session-End Hook 後置不變量（已實施 ✅）
- **守衛驗證證據**:
  - AGENTS.md Step 0: precondition_check() 中任一 ASSERT fail → STOP 並禁止輸出「📍 當前狀態 & 下一步」
  - 模擬原始情境（完成 Step 1 後嘗試觸發 Step 6）→ Step 0 ASSERT step_2_pgvg_passed FAIL → STOP，AI 必須先執行 PGVG
- **更新 Skill**: AGENTS.md ✅, CHANGE-MANAGEMENT.md ✅
- **守衛強化歷程**: 首次建立（2026-05-14），非 GUARD_STRENGTHENING 模式

**處理狀態**: ✅ 完成
