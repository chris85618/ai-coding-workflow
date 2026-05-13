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
├─────────────────────────────────────────────────────┤
│  Step 3: 微驗證 8 步（原 6 步 + 新增 Step 0/7）      │
│  → Step 0: 格式驗證                                  │
│  → Step 1-5: 結構/正向/反向/語意/孤兒                │
│  → Step 6: 影響分析                                  │
│  → Step 7: 變更紀錄 → IMP-xxx 寫入 change-log.md     │
├─────────────────────────────────────────────────────┤
│  Step 4: 若 FIX → 根因左移迴圈                       │
│  → 觸發 root-cause-leftshift.md                      │
│  → 產出 LESSON-xxx                                   │
│  → 更新觸發錯誤的 skill/prompt                       │
│  → 驗證左移後的 skill 可防止重現                      │
└─────────────────────────────────────────────────────┘
```

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
