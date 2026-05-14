# ADR-GOV-002: ADR 治理框架 — 全決策記錄制度

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-001, FR-002, FR-003, NFR-001
> **取代**: 無（新增制度）

---

## 背景

- **觸發 Stage/Phase**: 跨切面治理層
- **觸發事件**: 既有 workflow 中決策散落於多個治理文件（CHANGE-MANAGEMENT.md、IMPACT-ANALYSIS.md、TECH-DEBT.md），缺少統一的決策登記機制。人類 HITL 輸入和 AI 自主決策未被系統性記錄，導致決策可追溯性不足。
- **前置條件**: ADR-STR-001 已建立三層分離架構；四個治理文件已獨立運作
- **約束**: 純 Markdown 格式（NFR-001）；LLM 必須能自主撰寫

## 決策

我們決定建立全決策記錄制度：

1. **所有決策以 ADR 形式記錄**，分為 6 個類別（STRUCTURAL / GOVERNANCE / SECURITY / SCOPE / GATE / OPERATIONAL）
2. **ADR 為決策的單一事實來源**，CHANGE-MANAGEMENT、IMPACT-ANALYSIS、TECH-DEBT 為 ADR 的關聯產出物
3. **每個 HITL 閘門決策產出 ADR-GATE-xxx**，含人類 prompt 原文
4. **提供標準化範本**（ADR-TEMPLATE.md）供 LLM 撰寫
5. **統一命名前綴**：所有 ADR 類別皆使用 `ADR-{CATEGORY}-{NNN}` 格式，無例外

## 理由

- 35 個 HITL 進入點的決策目前無統一記錄機制
- 變更紀錄和技術債（DEBT-xxx）缺少決策授權追溯
- ADR 是業界成熟的架構決策記錄格式，擴展其範圍至流程/範圍/閘門決策符合精神

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------|
| 維持現狀（分散治理文件） | 無遷移成本 | 決策不可追溯、無法回溯人類輸入 | 違反全追溯原則 |
| 使用 Decision Log（扁平列表） | 簡單 | 無分類、無結構化後果分析 | 不符合 ADR 架構決策原意 |
| 使用 YAML/JSON 結構化記錄 | 機器可讀 | 違反 NFR-001 純 Markdown 約束 | 技術約束 |

## 後果

**正面**：
- 所有決策（人類 + AI）皆可追溯至具體 ADR
- 變更紀錄、DEBT-xxx、RISK-xxx 皆有授權 ADR 連結
- HITL 閘門的人類輸入被完整保存
- LLM 可依範本自主產出一致性高的 ADR

**負面**：
- ADR 數量會顯著增加（每個 Stage HITL 至少 1 個 ADR-GATE）
- 需要維護 ADR-INDEX.md 索引
- 撰寫成本增加（每個決策點多 1 個文件操作）

**風險**：
- RISK-002: ADR 數量膨脹導致管理困難 → 以追溯矩陣統一管理 ADR 登記簿緩解

## 影響分析

- **爆炸半徑**: 4 個治理文件 + 12 個 Stage/Phase 文件的出口閘門描述
- **跨 Stage 影響**: 全部（跨切面）
- **嚴重度**: MAJOR（跨切面治理變更）
- **受影響 ID**: TRACEABILITY.md ID 前綴表、AGENTS.md ID 系統概要、所有 Stage 出口閘門的 ADR 追溯欄位


## 流程變更

- **修改前規則**: 決策分散記錄於 CHANGE-MANAGEMENT.md、IMPACT-ANALYSIS.md、TECH-DEBT.md，無統一格式
- **修改後規則**: 所有決策以 ADR 形式記錄，6 個類別分層，標準化範本；IMP/DEBT/RISK 追溯至授權 ADR；所有類別統一使用 `ADR-{CATEGORY}-{NNN}` 前綴
- **影響範圍**: 所有 Phase/Stage（跨切面）
- **過渡期**: 立即生效

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 治理文件 | N/A | docs/governance/ADR-GOVERNANCE.md（新增） |
| 範本 | N/A | docs/adr/ADR-TEMPLATE.md（新增） |
| 索引 | N/A | docs/adr/ADR-INDEX.md（新增） |
| 影響分析 | N/A | 初始建立 |
| 技術債 | N/A | 無 |
| 風險 | RISK-002 | ADR 數量膨脹導致管理困難 |
| 教訓 | N/A | 無 |
