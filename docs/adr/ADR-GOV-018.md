# ADR-GOV-018: 雙軸意圖框架 (DAIF) 整合

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-019
> **整合來源**: Omega v9.8 Foundry Generation (DAIF-M01)

---

## 背景

- **觸發 Stage/Phase**: 治理層（Omega v9.8 整合）
- **觸發事件**: 識別出 Session-Start Hook 缺少使用者意圖風險評估
- **前置條件**: Session-Start Hook 僅讀取狀態和恢復，無意圖評估

## 決策

我們決定在 Session-Start Hook Step 3 注入 DAIF 雙軸意圖評估：
1. 對使用者請求在「清晰度 (Clarity)」和「風險 (Risk)」兩個軸上評估
2. 若 risk > threshold AND clarity < threshold → 暫停並呈現 Advisory Briefing
3. 使用者確認後再繼續

## 理由

- **支持證據**: Omega 的 DAIF-M01 機制有效防止低清晰度高風險請求的盲目執行
- **權衡取捨**: 某些請求會被暫停詢問，增加互動次數

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 對所有請求直接執行 | 快速 | 高風險低清晰度請求可能造成損害 | 不安全 |
| 僅在 Stage 出口評估 | 減少互動 | 事後才發現意圖偏差 | 未左移 |

## 後果

**正面**：高風險模糊請求在執行前被攔截
**負面**：明確低風險請求也需經過評估（但應快速通過）

## 影響分析

- **爆炸半徑**: 1（AGENTS.md Session-Start Hook）
- **嚴重度**: MODERATE

## 流程變更

- **修改前規則**: Session-Start Hook 4 步（讀取、恢復、報告、Hard Gate）
- **修改後規則**: Session-Start Hook 5 步（+Step 3 DAIF 評估）
- **影響範圍**: 每個 session 的啟動評估

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 來源 | Omega v9.8 | DAIF-M01 雙軸意圖框架 |
