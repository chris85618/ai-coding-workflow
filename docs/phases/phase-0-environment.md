# Phase 0：環境啟動

> 每次 Session 開始時自動執行，不需手動介入。

---

## 自動觸發

| 工具 | 自動行為 | 說明 |
|------|---------|------|
| **ECC** | `SessionStart` hook | 載入前次 context、偵測 package manager、啟動觀察器 |
| **gstack** | SKILL.md Preamble | 版本檢查、session 追蹤、learnings 載入、GBrain 連接、artifacts sync |

## 首次使用引導（僅首次）

gstack 首次使用會依序詢問：
1. Boil the Lake 理念介紹
2. Telemetry 偏好（community / anonymous / off）
3. Proactive 建議開關
4. CLAUDE.md 路由規則注入
5. 寫作風格選擇

> 這些引導只出現一次，之後的 session 會直接跳過。

## 決策閘門：判斷路徑

```
Q: 是否有需要修改或理解的既有程式碼庫？

├─ 否 → Path A (Greenfield) → 直接進入 Phase 1 (跳過 /understand)
│                              → 然後進入 Phase 2
└─ 是 → Path B (Existing)   → 進入 Phase 1 (完整執行)
                              → 然後進入 Phase 2
```

## 產出物

| 產出 | 說明 |
|------|------|
| Session context | 前次工作狀態還原 |
| 路徑決策 | Path A 或 Path B |
