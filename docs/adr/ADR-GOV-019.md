# ADR-GOV-019: 假設依賴圖 (ADG) + 門控思維鏈 (PAG) 驗證增強

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-005, FR-007
> **整合來源**: Omega v9.8 Foundry Generation (ADG-P01, PAG-P01)

---

## 背景

- **觸發 Stage/Phase**: 治理層（Omega v9.8 整合）
- **觸發事件**: 識別出迭代迴圈 Step M（微驗證）缺少假設矛盾檢測和步驟執行證明
- **前置條件**: Step M 僅觸發 micro-validation.md + impact-analysis-exec.md

## 決策

我們決定在雙 Agent 迭代協議 Step M（微驗證迴圈）中新增兩個檢查：
1. **ADG（假設依賴圖）檢查**：確認產出物中無 CONFLICTS_WITH 矛盾
2. **PAG（門控思維鏈）**：確保所有步驟執行皆有驗證證明

## 理由

- **支持證據**: Omega 的 ADG-P01 將散射約束轉為圖結構偵測矛盾；PAG-P01 消除「聲稱做了但實際沒做」的幻覺
- **權衡取捨**: 增加 Step M 驗證項，但邏輯一致性保障提升

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 僅依賴既有 micro-validation | 不增加步驟 | 無矛盾檢測、無執行證明 | 驗證不完整 |
| 完整實作 Omega 的形式化系統 | 最嚴謹 | 實作成本過高 | Ockham 剃刀 |

## 後果

**正面**：邏輯矛盾在迭代內被偵測；步驟執行有證明
**負面**：Step M 執行時間增加

## 影響分析

- **爆炸半徑**: 2（AGENTS.md 迭代協議 + iter-loop.md）
- **嚴重度**: MODERATE

## 流程變更

- **修改前規則**: Step M = micro-validation + impact-analysis
- **修改後規則**: Step M = micro-validation + impact-analysis + ADG check + PAG check
- **影響範圍**: Stage 3-8 迭代迴圈

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 來源 | Omega v9.8 | ADG-P01 + PAG-P01 |
