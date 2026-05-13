# ADR-GOV-020: AGENTS.md 結構化步驟協議重塑

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-001, FR-002, FR-003, NFR-001, FR-005, FR-019, FR-022, FR-023
> **取代**: N/A

---

## 背景

- **觸發 Stage/Phase**: Stage 3（治理架構自舉）
- **觸發事件**: HITL 主動發起 — AGENTS.md 已膨脹至 645 行 (~27KB)，其中約 40% 為非執行性參考內容（流程圖、工具矩陣、安裝步驟、資料夾結構）
- **前置條件**: ADR-GOV-001~019 已建立；Skill 體系已成熟；iter-loop.md 等 16 個 workflow-skills 已就位
- **約束**: AGENTS.md 經由 symlink 服務多個 repository，不可包含 ai_coding 專屬內容

## 決策

我們決定將 AGENTS.md 從「參考文件 + 執行協議混合體」重塑為「結構化步驟執行協議」：

1. **步驟化結構**: 全文以 Step 0-12 序列組織，每步附 `→ READ:` / `→ INVOKE:` / `→ NEXT:` hooks
2. **非執行內容遷移**: 流程圖、工具矩陣、安裝步驟、docs/ 結構移至 README.md
3. **全域搜尋協議抽取**: 移至 `skills/workflow-skills/exhaustive-search.md`，Skill Routing 新增觸發詞
4. **核心指令整合**: SSOT + Prompt Defense + 核心原則 + Voice & Style 合併為 `§ Core Directives`
5. **雙 docs/ 範圍規則**: 區分 `$FRAMEWORK_ROOT/docs/` (流程定義) 和 `{target_repo}/docs/` (專案產出物)
6. **安全審計三層縱深**: 移除獨立區段，整合至 Step 6 (Stage 5) 和 Step 9 (Stage 8) 的 `→ INVOKE:`
7. **ID 系統壓縮**: 完整表格保留於 TRACEABILITY.md，AGENTS.md 僅保留 prefix 快速索引

## 理由

- **支持證據**: 645 行中約 260 行為非執行性參考 (40%)；LLM 每次 session 載入完整 AGENTS.md 消耗大量 context window
- **權衡取捨**: 壓縮後 AI 需要 `→ READ:` 來取得完整定義，增加 1-2 次檔案讀取；但換取 ~38% token 節省和 ~95% 可執行指令密度
- **風險接受**: 若 step hooks 不完整，AI 可能迷失流程位置 → 緩解措施：每步強制 `→ ON COMPLETION` + `→ ON FAIL`

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------|
| 維持現狀（混合體） | 無遷移風險 | 40% 非執行 token 浪費；ai_coding 專屬內容污染通用協議 | 違反 Ockham's Razor (ADR-GOV-016) |
| 拆分為多個 AGENTS-*.md | 職責分離 | LLM 平台不支援多 AGENTS 檔案；載入順序不確定 | 技術約束不可行 |
| 僅移除流程圖保留其他 | 風險最小 | 僅解決部分問題；docs/ 範圍問題未解 | 不完整修復 |

## 後果

**正面**：
- AGENTS.md 從 ~645 行降至 ~400 行，token 成本減少 ~38%
- 可執行指令密度從 ~60% 提升至 ~95%
- 雙 docs/ 範圍規則消除跨 repository 干擾
- 每個步驟有明確 flow hooks，AI 不會迷失流程位置

**負面**：
- AI 需額外讀取 stage/phase docs（增加 1-2 次 view_file）
- README.md 需與 AGENTS.md 保持結構同步

## 影響分析

- **爆炸半徑**: 5 個檔案 (AGENTS.md, README.md, exhaustive-search.md, ADR-GOV-020, ADR-INDEX.md)
- **跨 Stage 影響**: 所有 Stage/Phase（結構性變更）
- **嚴重度**: MAJOR
- **受影響 ID**: FR-001, FR-002, FR-003, FR-005, FR-019, NFR-001

## 流程變更

- **修改前規則**: AGENTS.md 為混合參考文件 + 執行協議，含 inline 流程圖/矩陣/安裝步驟
- **修改後規則**: AGENTS.md 為純步驟執行協議 (Step 0-12)，參考內容移至 README.md 和獨立 skill
- **影響範圍**: 所有 Phase/Stage 的進入和退出方式
- **過渡期**: 無（一次性全量替換）

## 變更紀錄 (Implementation Records)

### 變更 #1: AGENTS.md 全文重寫 + 關聯檔案更新

- **日期**: 2026-05-14T04:52+08:00
- **類型**: MODIFY
- **檔案**: AGENTS.md, README.md, skills/workflow-skills/exhaustive-search.md, docs/adr/ADR-GOV-020.md, docs/adr/ADR-GOV-021.md, docs/adr/ADR-INDEX.md
- **影響 ID**: FR-001, FR-002, FR-003, FR-005, FR-019, NFR-001
- **爆炸半徑**: 5+
- **嚴重度**: MAJOR
- **微驗證**: PENDING
- **跨切面驗證**: PENDING

**變更明細**:

| # | 檔案 | 修正內容 | 根因類別 |
|---|------|----------|----------|
| 1 | AGENTS.md | 全文重寫為 Step 0-12 結構化協議 | ARCHITECTURE_EVOLUTION |
| 2 | README.md | 承接流程圖、工具矩陣、安裝步驟 | INFORMATION_RELOCATION |
| 3 | exhaustive-search.md | 從 AGENTS.md 抽取全域搜尋協議 | SKILL_EXTRACTION |
| 4 | ADR-GOV-020.md | 記錄本次決策 | GOVERNANCE |
| 5 | ADR-GOV-021.md | 記錄雙 Agent 迭代協議決策 | GOVERNANCE |
| 6 | ADR-INDEX.md | 新增 ADR-GOV-020, ADR-GOV-021 | INDEX_UPDATE |

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-020: AGENTS.md 膨脹模式

- **根因分類**: ARCHITECTURE_EROSION
- **根因描述**: 每次新增治理規則都 inline 至 AGENTS.md 而非抽取為獨立 skill/doc，導致檔案持續膨脹
- **5 Whys**:
  1. 為什麼 AGENTS.md 有 645 行？→ 包含大量非執行性參考內容
  2. 為什麼參考內容在 AGENTS.md？→ 初始設計時所有內容集中管理
  3. 為什麼沒有及時抽取？→ 缺乏「可執行指令密度」的衡量指標
  4. 為什麼沒有衡量指標？→ 未將 token 效率視為設計約束
  5. 結構性修正？→ 核心原則新增「token 效率」意識；所有新增內容先判定：是執行指令還是參考資料？
- **左移守衛**: AGENTS.md 核心原則新增「新增內容先判定執行性 vs 參考性」規則 ✅
- **更新 Skill**: N/A（新增至 Core Directives）
- **守衛驗證證據**: 後續新增內容必須通過「是否為 AI 執行時必須立即看到的指令？」判定

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 風險 | N/A | — |
| 技術債 | N/A | — |
