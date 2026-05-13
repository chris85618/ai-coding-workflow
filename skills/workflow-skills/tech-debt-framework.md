# Skill: 技術債管理框架

> **觸發條件**：Phase 10 回顧 + Stage 8 SonarCloud 後
> **輸入**：SonarCloud 報告、測試覆蓋、Agent α 審查、安全審計、追溯矩陣
> **輸出**：DEBT-xxx → `{target_repo}/docs/tech-debt-register.md`
> **依賴 skill**：`tech-debt-collect.md`（執行層）

---

## Step 1: 收集

觸發 `skills/workflow-skills/tech-debt-collect.md`：
- 7 個來源（程式碼品質、測試缺口、架構債、效能債、安全債、文件債、流程債）
- RICE 計算
- P0-P3 排序

## Step 2: 技術債登記格式

```markdown
# Tech Debt Register - [專案名稱]

**Last Updated**: [ISO 8601]
**Total Active Items**: [N]
**Sprint Allocation**: 20% capacity

## Active Debt

### DEBT-001: [標題]
- **來源**: [SonarCloud / 測試 / 架構 / 效能 / 安全 / 文件 / 流程]
- **影響元件**: [CLS-xxx / 模組名]
- **優先等級**: P0 | P1 | P2 | P3
- **RICE Score**: [score]
  - Reach: [1-100]
  - Impact: [0.5/1.0/2.0/3.0]
  - Confidence: [0.5-1.0]
  - Effort: [person-days]
- **象限**: Quick Win | Major Project | Fill In | Thankless Task
- **ADR 追溯**: ADR-xxx
- **建立日期**: [ISO 8601]
- **預計處理 Sprint**: [Sprint N / Backlog]
```

## Step 3: 四象限分類

| 象限 | Impact | Effort | 策略 |
|------|--------|--------|------|
| Quick Win | HIGH | LOW | 立即處理 |
| Major Project | HIGH | HIGH | 排入 Sprint |
| Fill In | LOW | LOW | 閒置時處理 |
| Thankless Task | LOW | HIGH | 暫緩（每 3 Sprint 重評） |

## Step 4: Sprint 容量規則

1. 每個 Sprint 分配 20% 容量給技術債償還
2. 從 RICE 分數最高的 DEBT-xxx 開始貪心選取
3. P0（Critical）不受容量限制，立即處理
4. 每季度全面重新評估 RICE 分數
