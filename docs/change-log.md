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
- **左移守衛**: 自我檢驗流程已驗證此模式；未來所有 FIX 類型變更需包含全庫 grep 驗證步驟
- **更新 Skill**: micro-validation.md Step 0 已涵蓋交叉覆蓋驗證 ✅
