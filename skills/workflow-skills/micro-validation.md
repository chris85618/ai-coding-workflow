# Skill: 左移微驗證迴圈（Step 0-7 + Step 5.5/5.7）

> **觸發條件**：每次檔案寫入操作後自動執行（CREATE / MODIFY / FIX）
> **輸入**：變更的 ID 和內容 + 變更類型
> **輸出**：PASS / FAIL + IMP-xxx 紀錄 + LESSON-xxx（所有變更類型皆觸發）

---

## 微動作定義

**任何檔案寫入操作**都是微動作，包括：
- 新增 ID（CREATE）
- 修改 ID 的內容或描述（MODIFY）
- 刪除 ID（MODIFY）
- 新增或修改追溯連結（MODIFY）
- 修正錯誤（FIX）
- **初次建立文件內容（CREATE）— 亦視為變更**

---

## 執行協議（Step 0-7 + Step 5.5/5.7）

```
Step 0: 格式驗證（Post-Generation Validation Gate）
→ Markdown 格式正確？（backtick 配對、表格對齊、標題層級）
→ 路徑引用正確？（無硬編碼絕對路徑、無斷裂連結）
→ 無外來殘留內容？（grep "from vibe"、grep inline S2C code blocks）

Step 1: 結構完整性
→ ID 格式是否符合前綴規格？（BG/S/FEA/FR/NFR/UC/ADR/ALG/CLS/EVT/INV/SC/TC/DEBT/RISK/IMP/LESSON）
→ 序號是否連續且無重複？
→ **自動化計數**：從實際檔案 grep 計數，不接受 LLM 自我報告

Step 2: 正向追溯
→ 該 ID 是否有至少一條正向連結到下游？
→ 終端 ID（TC-xxx）免除
→ **覆蓋斷言**：宣稱 "N/N 覆蓋" 時必須逐一列出每個 N

Step 3: 反向追溯
→ 該 ID 是否有至少一條反向連結到上游？
→ 源頭 ID（BG-xxx）免除

Step 4: 語意一致性
→ 下游 ID 描述是否為上游 ID 描述的具體化？
→ 範圍是否收斂（每層向下 ≤ 上游）？
→ 修改後意圖是否偏離原始 BG-xxx？
→ 同一追溯鏈上是否有矛盾？
→ **交叉覆蓋驗證**：若此 Stage 宣稱覆蓋上游 ID（如 "9/9 UC"），
   從實際內容逐一 grep 每個上游 ID，確認實際出現

Step 5: 孤兒偵測
→ 是否有 ID 無上游也無下游？
→ 是否有斷裂追溯鏈？

Step 5.5: 全方向連結追溯（FR-022）
→ 從變更 ID 查找所有 justifies/constrains 關係的 ADR
→ 從變更 ID 查找所有 constrains 關係的 NFR
→ 從變更 ID 查找所有 mitigates 關係的 RISK
→ 從變更 ID 查找所有 formalizes/emitted-by/guards 關係
→ 對每個受影響 ID：讀取完整文件驗證語意一致性
→ ADR 不再成立 → 標記 SUPERSEDED
→ NFR 被違反 → 嚴重度升至 MAJOR

Step 5.7: LESSON 重用檢查（FR-023，所有變更類型皆執行）
→ 掃描已存在的 LESSON-xxx
→ 若有相同根因類別 → 左移守衛不足，強化既有守衛
→ 若無相同根因 → 標準 RCA 流程

Step 6: 影響分析觸發
→ 觸發 skills/workflow-skills/impact-analysis-exec.md
→ 標記受影響下游 ID

Step 7: 變更紀錄 + 根因左移（所有變更類型皆執行）
→ 寫入 IMP-xxx 至 docs/change-log.md
→ 觸發 skills/workflow-skills/root-cause-leftshift.md
→ 產出 LESSON-xxx
→ 更新觸發問題的 skill/prompt
→ 驗證更新後 skill 可防止重現
```

---

## LLM Hallucination Guard（內嵌）

```
在 Step 1 和 Step 4 中強制執行：

1. 不接受泛稱覆蓋：
   BAD:  "所有 UC 已被 CLS 覆蓋"
   GOOD: "UC-001→CLS-001, UC-002→CLS-012, ..., UC-009→CLS-011（9/9 逐一驗證）"

2. 計數必須自動化：
   BAD:  "traceability matrix 有 106 個 ID"
   GOOD: "grep -c 'XXX-\d{3}' traceability-matrix.md = 106"

3. 二次驗證模式：
   生成 → 從輸出 grep 回查 → 比對輸入 → 差異為 0 才 PASS
```

---

## 結果判定

```
Step 0-7 + 5.5/5.7 全數通過 ✅ → 繼續下一個微動作
任一失敗 ❌ → 自主修復 → 重新執行（從失敗步驟開始）
修復 3 次仍失敗 → 上報 HITL
所有變更類型 → 執行 Step 7 根因左移，產出 LESSON-xxx（無例外）
```
