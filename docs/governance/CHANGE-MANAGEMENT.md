# Change Management Protocol

> **治理層**：跨切面強制執行
> **觸發條件**：任何文件寫入操作（CREATE / MODIFY / FIX）

---

## 核心原則

**每一次寫入都是變更。** 無論是初次建立還是修正，所有文件操作必須通過完整變更管理流程。

---

## 變更管理流程

```
┌─────────────────────────────────────────────────────┐
│  Step 0: 變更分類                                    │
│  → 類型: CREATE | MODIFY | FIX                       │
│  → 若 FIX: 必須觸發 root-cause-leftshift.md          │
├─────────────────────────────────────────────────────┤
│  Step 1: 產出生成（S2C skill 或手動修改）             │
│  → 執行對應 S2C skill                                │
│  → 遵守 Post-Generation Validation Gate              │
├─────────────────────────────────────────────────────┤
│  Step 2: Post-Generation Validation Gate (PGVG)      │
│  → 2a: 格式驗證（markdown lint, backtick, 表格）     │
│  → 2b: 覆蓋斷言（輸入 ID ↔ 輸出 ID 交叉驗證）       │
│  → 2c: 計數驗證（從實際內容 grep 計數，非自我報告）   │
│  → 2d: 語意驗證（宣稱覆蓋 vs 實際覆蓋）             │
│  → 2e: 交叉引用掃描（rename/prefix 變更時強制）      │
│       對 docs/ + AGENTS.md 全域 grep               │
│       殘留舊 ID/前綴數量必須 = 0                     │
│  → 2f: FR/NFR 合規驗證（修改治理/流程文件時強制）   │
│       從追溯矩陣反向查找此文件實作的 FR/NFR        │
│       逐一驗證修改後的文件是否仍滿足每個 FR/NFR   │
│       若新增 FR/NFR 被此文件實作，追溯矩陣必須已更新 │
├─────────────────────────────────────────────────────┤
│  Step 3: 微驗證（Step 0-7 + Step 5.5/5.7）            │
│  → Step 0: 格式驗證                                  │
│  → Step 1-5: 結構/正向/反向/語意/孤兒                │
│  → Step 5.5: 全方向連結追溯（FR-022）              │
│  → Step 5.7: LESSON 重用檢查（FR-023，若 FIX）   │
│  → Step 6: 影響分析                                  │
│  → Step 7: 變更紀錄 → IMP-xxx 寫入 change-log.md     │
├─────────────────────────────────────────────────────┤
│  Step 4: 根因左移迴圈（強制執行條件見下方）        │
│  → 掃描完整對話歷程，窮舉所有疑慮/修正/Q&A       │
│  → 對每個識別出的問題執行 RCA                      │
│  → 產出 LESSON-xxx                                  │
│  → 更新觸發錯誤的 skill/prompt/governance 文件      │
│  → 驗證左移後的規則可防止重現                       │
│                                                      │
│  Step 4 觸發條件（滿足任一即觸發）：                │
│  → 對話中任何 user Q&A（非直接 approve）            │
│  → 對話中任何 mid-execution 修正                    │
│  → PGVG 發現任何需修復的不一致                      │
│  → 微驗證發現任何 FAIL                              │
│                                                      │
│  Step 4 唯一免除條件（必須全部滿足）：              │
│  → 完整對話歷程零疑慮                               │
│  → 完整對話歷程零 Q&A（全部直接 approve）           │
│  → PGVG + 微驗證一次通過無修復                      │
└─────────────────────────────────────────────────────┘

### Step 5: 跨切面一致性驗證（Cross-Cutting Consistency）

> 觸發條件：變更橫跨 2+ Stage/Phase 或變更 3+ 文件時強制執行。

```
cross_cutting_verify():
  # 1. 變更總覽
  all_changes = collect_all_session_changes()
  affected_files = unique(all_changes.files)
  affected_stages = unique(all_changes.stages)

  # 2. 全矩陣重驗證
  FOR each ID_prefix IN traceability-matrix:
    verify_forward_links()
    verify_backward_links()
    verify_orphan_free()
    verify_semantic_consistency()

  # 3. 跨文件交叉檢查
  FOR each file IN affected_files:
    cross_ref = grep_all_ids(file)
    FOR each id IN cross_ref:
      verify_id_exists_in_source_file(id)
      verify_id_description_consistent(id)

  # 4. 覆蓋統計重算
  recount_all_coverage_stats()
  compare_with_claimed_stats()
  IF mismatch: FIX + 記錄

  # 5. 過期引用掃描
  FOR each file IN affected_files:
    scan_stale_references():
      - 舊 ID 範圍（e.g. "FEA-001..FEA-009" 應為 FEA-010）
      - 舊計數（e.g. "8 步" 應為 "Step 0-7 + 5.5/5.7"）
      - 舊時間戳
    IF stale_found: FIX + 記錄
```

### Step 6: 收尾協議（Session-End Hook）

> 每次回覆使用者前強制執行。詳見 AGENTS.md「收尾協議」章節。

1. 讀取 `docs/workflow-state.md` 當前記錄狀態
2. 比對本次 session 實際工作 vs 記錄狀態
3. 更新 `docs/workflow-state.md`（Pipeline Position, WBS, Gates, Next Actions, Session Summary）
4. 在回覆末尾附加「📍 當前狀態 & 下一步」區塊

---

## IMP-xxx 變更紀錄格式

```
### IMP-xxx: [簡述]

- **類型**: CREATE | MODIFY | FIX
- **檔案**: [file path]
- **影響 ID**: [affected IDs]
- **爆炸半徑**: [blast_radius]
- **嚴重度**: COSMETIC | MINOR | MODERATE | MAJOR
- **微驗證**: PASS | FAIL (step N)
- **若 FIX**:
  - 根因分類: LLM_HALLUCINATION | PROCESS_GAP | COVERAGE_GAP | FORMAT_ERROR
  - 根因描述: [description]
  - 左移動作: [skill updated]
  - 守衛驗證證據: [guard_name] 能攔截 [scenario] 的證據（grep 結果/測試輸出/步驟引用）
  - LESSON-xxx: [reference]
```

---

## 根因分類法

| 類別 | 定義 | 左移策略 |
|------|------|---------|
| LLM_HALLUCINATION | LLM 機率型錯誤，輸出與輸入不一致 | Prompt 加入明確驗證指令 + 結構化輸出約束 |
| PROCESS_GAP | 流程缺漏，該做的步驟未執行 | 流程文件加入強制步驟 |
| COVERAGE_GAP | 覆蓋不完整，宣稱 N/N 但實際 < N | 自動化計數斷言替代自我報告 |
| FORMAT_ERROR | 格式錯誤（markdown, backtick, table） | Post-Gen Gate 加入格式 lint |
| SEMANTIC_DRIFT | 語意漂移，上下游 ID 描述不一致 | 微驗證 Step 4 強化交叉比對 |
| NAMING_INCONSISTENCY | 命名不一致，ID 格式規則有例外 | 零例外不變量 + PGVG 2e 全域掃描 |
| FIRST_PRINCIPLES_SKIP | 未從第一性原則推導，直接套用啟發法 | 強制「公理 → 定理 → 規則」推導鏈 |

---

## 結構不變量（跨切面強制）

> 以下不變量由 RCA 歷程推導，違反任一即觸發 PGVG 失敗。

### INV-CM-001：範本先行不變量

> 任何模板化產出物的實例，不得在範本完成且定稿之前建立或修改。若範本尚不存在，必須先建立範本、再建立實例。已存在的實例在範本建立後必須立即進行合規性追溯檢查。

**根因**: ADR-001 在 ADR-TEMPLATE.md 存在前已建立，導致缺少 9 個必填欄位。

### INV-CM-002：禁止推測性範例

> 所有治理/追溯文件中的範例，必須引用實際存在的實例。在實例尚不存在時，使用明確標記的佔位符號：`{PLACEHOLDER: ADR-GOV-xxx: 描述}`。禁止使用看似真實但實為虛構的範例。

**根因**: TRACEABILITY.md 中「ADR-GOV-001: 微驗證步數」範例在 ADR-GOV-001 實際建立前已寫入，建立後內容不符（實為 DU 理論），產生語意不一致。

### INV-CM-003：零例外命名不變量

> 任何命名、格式或結構規則一旦定義，適用於所有實例，無例外。「向下相容」不構成例外理由；應遷移所有既有實例至新規則。

**根因**: ADR-001 以「向下相容」豁免 `ADR-{CATEGORY}-{NNN}` 前綴規則，導致 STRUCTURAL 類別使用 `ADR-xxx` 而其他 5 類使用帶前綴格式，命名系統不一致。

### INV-CM-004：第一性原則推導不變量

> 新治理機制的決策準則，必須從第一性原則（公理 → 定理 → 規則）推導。禁止直接提出啟發法。啟發法僅作為推導結論的實務落地手段。

**根因**: ADR-GATE 頻率最初以「每個 Stage HITL 至少 1 個」的啟發法提出，未從 SOLID/SRP 原則推導。後由 HITL 修正為 Decision Unit 理論。

---

## LLM Hallucination Guard 模式

### Context Engineering 防護

```
1. 明確約束：在 prompt 中列出所有輸入 ID，要求逐一處理
   BAD:  "為所有 UC 建立 CLS"
   GOOD: "為 UC-001, UC-002, ..., UC-009 逐一建立對應 CLS，完成後逐一驗證"

2. 結構化輸出：要求以表格形式輸出覆蓋映射
   BAD:  自由文本描述覆蓋情況
   GOOD: "輸出 | UC-xxx | CLS-xxx | 連結類型 | 表格"

3. 二次驗證：生成後立即從輸出中 grep 回查
   "從你剛生成的內容中，列出所有 UC-xxx 出現次數"
```

### Harness Engineering 防護

```
1. 自動化斷言：用 PowerShell/grep 替代 LLM 自我報告
2. 逐項驗證：不接受 "N/N 通過" 的泛稱，要求列出每個 N
3. 交叉驗證：從多個文件交叉比對同一 ID 的一致性
```
