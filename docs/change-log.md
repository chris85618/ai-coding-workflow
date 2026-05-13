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
