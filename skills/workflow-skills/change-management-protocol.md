# Skill: 變更管理協議

> **觸發條件**：任何檔案寫入操作（CREATE / MODIFY / FIX）
> **核心原則**：每一次寫入都是變更。所有操作必須通過完整變更管理流程。
> **依賴 skill**：`micro-validation.md`、`root-cause-leftshift.md`、`impact-analysis-exec.md`

---

## Step 0: 變更分類

- 類型：CREATE | MODIFY | FIX
- **所有類型皆觸發 root-cause-leftshift.md，無例外**

## Step 1: 產出生成

- 執行對應 S2C skill 或手動修改
- 遵守 Post-Generation Validation Gate（Step 2）

## Step 2: PGVG（Post-Generation Validation Gate）

1. **2a 格式驗證**：Markdown lint、backtick 配對、表格對齊、標題層級
2. **2b 覆蓋斷言**：輸入 ID ↔ 輸出 ID 交叉驗證
3. **2c 計數驗證**：從實際內容 grep 計數，非自我報告
4. **2d 語意驗證**：宣稱覆蓋 vs 實際覆蓋
5. **2e 交叉引用掃描**：rename/prefix 變更時強制全域 grep，殘留舊 ID/前綴數量必須 = 0
6. **2f FR/NFR 合規驗證**：修改治理/流程文件時，反向查找此文件實作的 FR/NFR，逐一驗證修改後仍滿足

## Step 3: 微驗證

觸發 `skills/workflow-skills/micro-validation.md`（完整 Step 0-7 + 5.5/5.7）。

## Step 4: 根因左移

觸發 `skills/workflow-skills/root-cause-leftshift.md`。
- **觸發條件**：所有變更，無例外
- 禁止 AI 以任何理由判定「不適用」
- 每次變更都有原因，找出「為什麼需要這個變更」本身就是左移核心

## Step 5: 跨切面一致性驗證

> 觸發條件：變更橫跨 2+ Stage/Phase 或變更 3+ 文件時強制執行。

```
cross_cutting_verify():
  1. 全矩陣重驗證（正向/反向/孤兒/語意）
  2. 跨文件交叉檢查（grep ID 一致性）
  3. 覆蓋統計重算（比對宣稱 vs 實際）
  4. 過期引用掃描（舊 ID/計數/時間戳）
```

## Step 6: 收尾協議

見 AGENTS.md Step 12。前置斷言：

```
FOR each change IN session_changes:
  ASSERT step_0_classified    = TRUE
  ASSERT step_1_generated     = TRUE
  ASSERT step_2_pgvg          = TRUE
  ASSERT step_3_micro_val     = TRUE
  ASSERT step_4_rca_done      = TRUE
  IF cross_cutting → ASSERT step_5_done = TRUE
```

若任一 ASSERT 失敗 → STOP → 完成缺失步驟 → 重試。

---

## Inline CM-GATE（寫入前強制宣告）

> **ADR**: ADR-GOV-022, LESSON-024
> **根因**: GOVERNANCE_BYPASS — AI 跳過 CM 因為 CM 是「寫完後才做」的後置步驟，容易被遺忘

**規則**：每次呼叫 write_to_file / replace_file_content / multi_replace_file_content **之前**，AI 必須先在回應中輸出 CM-GATE 宣告：

```
CM-GATE: [檔案名] | Type: [CREATE/MODIFY/FIX] | Class: [根因分類] | ADR: [ref or NEW]
```

- 若無 CM-GATE 宣告就寫入 → 構成 GOVERNANCE_BYPASS
- CM-GATE 宣告是寫入操作的前置條件，不是後置記錄
- 這創造了可觀測的紙面軌跡，使跳過行為在 Step 12 時可被偵測

## Batch Mode（批次模式）

> **觸發條件**：同一 session 中計畫寫入 3+ 個檔案

**規則**：進入批次模式前，AI 必須先輸出 Batch 範圍宣告：

```
BATCH-CM: [N] files | Unified ADR: [ref] | Classification: [category]
Files:
1. [path] — [CREATE/MODIFY]
2. [path] — [CREATE/MODIFY]
...
```

- 批次內每個檔案仍需個別 CM-GATE
- 但 PGVG 和微驗證可在批次結束後統一執行（而非逐一）
- RCA 統一一次（因為批次內檔案共享同一根因）
- Step 12 枚舉時必須與 Batch 宣告比對，確認無遺漏

## 宣告-實施缺口偵測（DECLARATION_IMPLEMENTATION_GAP Guard）

> **ADR**: LESSON-025
> **根因**: LESSON 宣稱「左移守衛已更新」但實際未修改任何 skill 檔案

**規則**：每個 LESSON-xxx 的「更新的 Skill」欄位必須包含：

1. **具體 diff**：skill 檔案的修改前/後對比（至少引用行號）
2. **若宣稱「已存在」**：必須引用該守衛的具體行號作為證據
3. **若宣稱 N/A**：必須提供第一性原則推導，解釋為什麼此類問題不需要 skill 更新

禁止以下模式：
- ❌ 「左移守衛: Step 12 CM 前置斷言確保此類遺漏會被攔截 ✅」（宣稱既有守衛有效，但該守衛明顯已失敗）
- ❌ 「更新 Skill: N/A」（沒有不需要更新的變更）
- ❌ 「守衛驗證證據: 後續新增內容必須通過判定」（未來式不是證據）

---

## 結構不變量

### INV-CM-001：範本先行
任何模板化產出物的實例，不得在範本完成前建立。

### INV-CM-002：禁止推測性範例
所有範例必須引用實際存在的實例。未建立的用 `{PLACEHOLDER: ID: 描述}` 標記。

### INV-CM-003：零例外命名
命名規則一旦定義，適用所有實例，無例外。遷移所有既有實例至新規則。

### INV-CM-004：第一性原則推導
新治理機制必須從公理 → 定理 → 規則推導，禁止直接提出啟發法。

### INV-CM-005：Session-End Hook 後置
Session-End Hook 必須後置於本 session 所有變更的 CM Steps 0-5 全數完成之後。

---

## 根因分類法

| 類別 | 定義 | 左移策略 |
|------|------|---------|
| LLM_HALLUCINATION | LLM 輸出與輸入不一致 | Prompt 加驗證指令 + 結構化約束 |
| PROCESS_GAP | 該做的步驟未執行 | 流程文件加強制步驟 |
| COVERAGE_GAP | 宣稱 N/N 但實際 < N | 自動化計數斷言 |
| FORMAT_ERROR | markdown/backtick/table 錯誤 | Post-Gen Gate 加格式 lint |
| SEMANTIC_DRIFT | 上下游 ID 描述不一致 | 微驗證 Step 4 強化交叉比對 |
| NAMING_INCONSISTENCY | 命名規則有例外 | 零例外不變量 + PGVG 2e |
| FIRST_PRINCIPLES_SKIP | 未從第一性原則推導 | 強制「公理→定理→規則」鏈 |
| GOVERNANCE_BYPASS | 跳過治理步驟 | 消除免除條件 + 強制前置斷言 |
| SCAN_INCOMPLETENESS | 掃描未窮盡 | 強制 Registry 列舉 + checklist |
| NEW_CAPABILITY | 新功能新增 | 記錄動機 + 確認非過度設計 |
| IMPROVEMENT | 改善既有產出物 | 記錄原先不完整原因 + 根因左移 |

---

## ADR 變更紀錄格式

```markdown
### 變更 #N: [簡述]
- **類型**: CREATE | MODIFY | FIX
- **日期**: [ISO 8601]
- **檔案**: [file path]
- **影響 ID**: [affected IDs]
- **爆炸半徑**: [blast_radius]
- **嚴重度**: COSMETIC | MINOR | MODERATE | MAJOR
- **微驗證**: PASS | FAIL (step N)
- **根因分類**: [強制填寫]
- **根因描述**: [為什麼需要這個變更？]
- **左移動作**: [skill updated 或理由]
- **LESSON-xxx**: [reference]
```

---

## LLM Hallucination Guard

### Context Engineering
1. 在 prompt 中列出所有輸入 ID，要求逐一處理
2. 要求以表格形式輸出覆蓋映射
3. 生成後立即從輸出 grep 回查

### Harness Engineering
1. 用 PowerShell/grep 替代 LLM 自我報告
2. 逐項驗證，不接受 "N/N 通過" 泛稱
3. 從多個文件交叉比對同一 ID 一致性
