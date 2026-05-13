# ADR-STR-001: 三層分離架構（Docs / Skills / Tools）

> **狀態**: Accepted
> **日期**: 2026-05-13
> **類別**: STRUCTURAL
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-001, FR-002, FR-003
> **取代**: N/A
> **被取代**: N/A

---

## 背景

- **觸發 Stage/Phase**: Stage 3（技術規劃）
- **觸發事件**: 初始架構設計中，docs/ 文件同時包含文件（目的、維度、出口閘門）和可執行協議（迭代迴圈、S2C 分析步驟）
- **前置條件**: Phase 2 專案章程和範圍定義已完成；四個子模組（ECC、gstack、UA、SF）已整合
- **約束**: 純 Markdown 格式（NFR-001）；必須支援 LLM 自主執行

問題分析：

1. 職責不清：docs 既是文件又是技能定義
2. 複用困難：迭代迴圈在 6 個 stage docs 中重複定義
3. 維護風險：修改通用協議需同步更新 6 個文件

## 決策

我們決定採用三層分離架構：

```
Tier 1: docs/ (WHAT/WHY)
→ 目的、輸入、輸出、審查維度、出口閘門
→ 純敘述，不含可執行步驟

Tier 2: skills/workflow-skills/ (HOW)
→ 可執行協議、step-by-step 流程
→ 觸發條件、輸入/輸出規格

Tier 3: External Tools (WHO)
→ /autoplan, /cso, skillfortify, SonarCloud
→ 子模組: ECC, gstack, UA, SF
```

## 理由

- **支持證據**: 迭代迴圈在 6 個 Stage 文件中逐字重複，任何修改需同步 6 處
- **權衡取捨**: 增加一層引用（docs → skills → tools），換取單點維護和職責清晰
- **風險接受**: 新進人員需額外理解三層關係，但可透過 WORKFLOW.md 呼叫鏈圖緩解

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------|
| 全部放 docs/ | 單一位置，簡單 | 職責混淆，迭代協議重複 6 份 | 違反 SRP，維護成本 O(n) |
| 全部放 skills/ | 可執行性高 | 喪失文件/治理的清晰分類 | 品質規格和執行協議混淆 |
| 用 YAML/JSON 定義 | 機器可讀，可驗證 | 違反純 Markdown 約束（NFR-001） | 技術約束 |

## 後果

**正面**：
- 通用協議（iter-loop, micro-validation）只維護一份
- Docs 變為純粹的品質規格文件
- Skills 可獨立演進和測試

**負面**：
- 多一層引用（docs → skills → tools）
- 新進人員需理解三層關係

**風險**：
- N/A（風險已透過 WORKFLOW.md 呼叫鏈圖緩解）

## 影響分析

- **爆炸半徑**: 12 個文件（6 Stage docs + 6 Phase docs）
- **跨 Stage 影響**: 全部（跨切面架構變更）
- **嚴重度**: MAJOR
- **受影響 ID**: 所有 Stage/Phase 文件的結構
- **關聯 IMP-xxx**: 初始建立，無前序影響分析

## 架構影響

- **受影響模組/元件**: docs/, skills/workflow-skills/, 所有 Stage/Phase 文件
- **依賴方向變更**: 是。docs/ 從自包含改為引用 skills/；skills/ 從不存在改為中間層
- **API 變更**: 否
- **資料模型變更**: 否

## 驗證計畫

- 驗證方式：確認所有 Stage 文件不再包含可執行步驟；確認 skills/ 中的協議可被獨立引用
- 回滾計畫：將 skills/ 內容合併回各 Stage 文件（逆向操作）

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 影響分析 | N/A | 初始建立 |
| 技術債 | N/A | 無 |
| 變更紀錄 | N/A | 初始建立 |
| 風險 | N/A | 無 |
| 教訓 | N/A | 無 |
