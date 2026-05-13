# ADR-GOV-008: 全鏈影響追溯制度化 (FR-022/023/024/025)

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-022, FR-023, FR-024, FR-025, FEA-002, FEA-003

---

## 背景

- **觸發 Stage/Phase**: HITL 需求（FR-022/023/024/025 制度化）
- **觸發事件**: LESSON-006 的守衛宣稱與實際實作不符（Step 0 宣稱涵蓋但實際不涵蓋跨檔案 grep）
- **前置條件**: 微驗證僅有 Step 0-7，無全方向追溯、LESSON 重用、跨切面驗證
- **約束**: 14 個跨 9 檔案的不一致需一次性修正

## 決策

我們決定制度化以下機制：
1. **FR-022**: micro-validation Step 5.5（全方向連結追溯）
2. **FR-023**: micro-validation Step 5.7（LESSON 重用檢查）
3. **FR-024**: CHANGE-MANAGEMENT Step 5（跨切面一致性驗證）
4. **FR-025**: CHANGE-MANAGEMENT Step 2f（FR/NFR 合規驗證）

## 理由

- **支持證據**: 變更 #1 的 14 issues 證明現有驗證不足；LESSON-007 發現守衛宣稱與能力不符
- **權衡取捨**: 顯著增加 CM 流程步驟數（從 4 步到 6 步），但實現系統性完整驗證

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 僅修正 14 個具體問題 | 最快 | 根因未消除，未來重現 | 未左移 |
| 僅加 Step 5.5 不加 Step 2f | 減少步驟 | FR/NFR 合規無強制驗證 | 部分修正 |

## 後果

**正面**：全鏈雙向驗證 + 守衛驗證證據欄位 + LESSON 重用檢查
**負面**：CM 流程複雜度增加

## 影響分析

- **爆炸半徑**: 14 issues across 9 files
- **嚴重度**: MAJOR
- **受影響 ID**: FR-024, FR-025（新增）

## 流程變更

- **修改前規則**: 微驗證 Step 0-7；CM Steps 0-4
- **修改後規則**: 微驗證 Step 0-7 + 5.5 + 5.7；CM Steps 0-5 + 2f
- **影響範圍**: 全切面

## 變更紀錄 (Implementation Records)

### 變更 #1: 全鏈影響追溯 + 跨切面一致性驗證制度化

- **日期**: 2026-05-14T00:35+08:00
- **類型**: mixed (CREATE + MODIFY + FIX)
- **嚴重度**: MAJOR (blast_radius=14 issues across 9 files, cross_stage=ALL)
- **微驗證**: PASS（Step 0-7 + 5.5/5.7 全數通過）
- **PGVG**: PASS（2a-2f 全數通過，計數驗證 120 ID 確認）
- **跨切面驗證**: PASS（Step 5 首次執行，發現 14 issues 全數修正）

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

### 變更 #2: ADR 治理債務清還 — 17 ADRs 還原

- **日期**: 2026-05-14T03:40+08:00
- **類型**: CREATE (17 ADR files) + MODIFY (5 files)
- **爆炸半徑**: 24（17 新建 + 5 更新 + 2 新增欄位）
- **嚴重度**: MAJOR（系統性治理債務清還）
- **微驗證**: PASS（grep 驗證 11 entries 有授權 ADR ✅; 19 ADR-GOV files exist ✅; 追溯矩陣 137 IDs ✅）

**變更明細**:
1. 17 ADRs 從 change-log 還原（ADR-GOV-003..019 ✅）
2. ADR-INDEX.md 完整更新 ✅
3. 追溯矩陣更新（120→137 IDs ✅）

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-007: 守衛宣稱與實際實作不符

- **根因分類**: PROCESS_GAP
- **根因描述**: LESSON-006 宣稱「micro-validation.md Step 0 已涵蓋交叉覆蓋驗證」，但 Step 0 實際只有格式 lint，不包含跨檔案 grep 掃描
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

### LESSON-013: 宣告-實施斷裂（Declaration-Implementation Gap）

- **根因分類**: DECLARATION_IMPLEMENTATION_GAP
- **根因描述**: ADR-GOVERNANCE.md Rule 1 宣告「每個變更必須追溯至一個 ADR」，但格式模板中不含對應欄位，CM 流程寫入外部 change-log 而非 ADR
- **5 Whys**:
  1. 為什麼 11 個變更紀錄沒有追溯至 ADR？→ 格式模板中無「授權 ADR」欄位
  2. 為什麼格式沒有此欄位？→ CHANGE-MANAGEMENT.md 建立早於 ADR-GOVERNANCE.md
  3. 為什麼 ADR-GOV-002 建立後未級聯更新 CM 格式？→ LESSON-008 已識別此模式但未擴展檢查至 ADR 連結
  4. 為什麼宣告性規則無對應強制閘門？→ 系統設計偏重「宣告規則」而非「嵌入強制驗證」
  5. 結構性修正？→ **每個宣告性規則必須有對應的格式欄位 + 驗證步驟（DECLARE-ENFORCE pairing）**
- **左移守衛**: ADR 變更紀錄區段必填（已實施 ✅）
- **更新 Skill**: CHANGE-MANAGEMENT.md ✅
- **守衛驗證證據**: ADR TEMPLATE 「變更紀錄」區段為必填 ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-007 | 守衛宣稱與實際實作不符 |
| 教訓 | LESSON-013 | 宣告-實施斷裂 |
