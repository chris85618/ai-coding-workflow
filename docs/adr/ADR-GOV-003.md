# ADR-GOV-003: 格式驗證閘門 (Step 0) 與外來殘留掃描

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-005, FR-007

---

## 背景

- **觸發 Stage/Phase**: Stage 5 入口自驗 + 初始整合階段
- **觸發事件**: project-charter.md 的 backtick 格式錯誤被發現；Stage 文件中殘留 inline S2C code blocks
- **前置條件**: 微驗證迴圈尚未包含格式檢查步驟（Step 0 不存在）
- **約束**: LLM 生成內容時機率性遺漏格式元素；外部整合時直接複製未經掃描

## 決策

我們決定在微驗證迴圈中引入 Step 0（格式驗證閘門），包含：
1. Markdown 格式正確性檢查（backtick 配對、表格對齊、標題層級）
2. 路徑引用正確性檢查（無硬編碼絕對路徑、無斷裂連結）
3. 外來殘留內容掃描（grep inline S2C code blocks、非本專案來源的內容）

## 理由

- **支持證據**: 變更 #1 發現 LLM 機率性遺漏 backtick；變更 #2 發現外部整合直接複製未掃描
- **權衡取捨**: 增加每次微動作的驗證成本，但消除格式類錯誤向下游傳播
- **風險接受**: 無

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 僅在 Stage 出口做格式檢查 | 執行次數少 | 錯誤累積到出口才發現，修復成本高 | 違反左移原則 |
| 依賴 LLM 自我檢查 | 零成本 | LESSON-001 已證明 LLM 自我報告不可靠 | 根因未消除 |

## 後果

**正面**：
- 格式錯誤在產生點立即被攔截
- 外來內容不再汙染專案文件

**負面**：
- 每次微動作增加 Step 0 驗證開銷

## 影響分析

- **爆炸半徑**: 0（變更 #1）+ 4 files（變更 #2）
- **跨 Stage 影響**: 全切面（Step 0 適用所有 Stage）
- **嚴重度**: COSMETIC (變更 #1) + MODERATE (變更 #2)
- **受影響 ID**: 無直接 ID

## 流程變更

- **修改前規則**: 微驗證從 Step 1（結構完整性）開始
- **修改後規則**: 微驗證從 Step 0（格式驗證 + 外來殘留掃描）開始
- **影響範圍**: 所有 Stage/Phase
- **過渡期**: 即時生效

## 變更紀錄 (Implementation Records)

### 變更 #1: project-charter.md backtick 修復

- **日期**: 2026-05-13（Stage 5 入口自驗）
- **類型**: FIX
- **檔案**: docs/project-charter.md (line 5)
- **影響 ID**: 無 ID 受影響（格式問題）
- **爆炸半徑**: 0
- **嚴重度**: COSMETIC
- **微驗證**: 未執行（當時 8 步協議尚未建立）

### 變更 #2: inline S2C code blocks 殘留清除

- **日期**: 2026-05-13（初始整合階段）
- **類型**: FIX
- **檔案**: docs/stages/stage-4,5,7,8
- **影響 ID**: 無直接 ID（結構問題）
- **爆炸半徑**: 4 files
- **嚴重度**: MODERATE
- **微驗證**: 未執行

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-001: LLM 格式遺漏

- **根因分類**: FORMAT_ERROR + LLM_HALLUCINATION
- **根因描述**: LLM 生成 markdown 時機率性遺漏開頭 backtick，且微驗證無格式檢查步驟
- **5 Whys**:
  1. 為什麼 backtick 格式錯誤？→ LLM 生成時機率性遺漏開頭 backtick
  2. 為什麼沒被阻止？→ s2c-charter.md 無格式驗證步驟
  3. 為什麼驗證沒偵測？→ 微驗證無 Step 0 格式驗證
  4. 為什麼流程允許？→ 初次建立不被視為「變更」
  5. 結構性修正？→ **每次寫入（含 CREATE）觸發格式 lint**
- **左移守衛**: micro-validation.md 新增 Step 0（格式驗證）
- **更新 Skill**: micro-validation.md ✅

### LESSON-004: 外來內容掃描缺失

- **根因分類**: PROCESS_GAP
- **根因描述**: 整合 vibe-coding 時直接複製內容，無外來殘留掃描步驟
- **5 Whys**:
  1. 為什麼有殘留？→ 整合 vibe-coding 時直接複製內容
  2. 為什麼沒被阻止？→ 無「外來內容掃描」步驟
  3. 為什麼驗證沒偵測？→ 微驗證不檢查 inline code 的來源
  4. 為什麼流程允許？→ 整合作業未經 Stage 3-8 管線
  5. 結構性修正？→ **micro-validation Step 0 加入外來殘留掃描（grep "from vibe", inline code blocks）**
- **左移守衛**: micro-validation.md Step 0 已更新 ✅
- **更新 Skill**: micro-validation.md ✅

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 教訓 | LESSON-001 | LLM 格式遺漏 |
| 教訓 | LESSON-004 | 外來內容掃描缺失 |
