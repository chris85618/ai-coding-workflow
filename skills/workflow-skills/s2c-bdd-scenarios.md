# Skill: S2C BDD 場景生成

> **觸發條件**：Stage 7（BDD/ATDD）
> **輸入**：UC-xxx, INV-xxx
> **輸出**：SC-xxx → `docs/bdd-scenarios.md` + 測試檔案

---

## Step 1: 場景生成

1. FOR each UC-xxx → generate_happy_path_scenario() → SC-xxx
2. FOR each UC-xxx → generate_alternative_flow_scenarios() → SC-xxx
3. FOR each UC-xxx → generate_exception_flow_scenarios() → SC-xxx
4. FOR each UC-xxx → generate_boundary_scenarios() → SC-xxx

## Step 2: 格式化與連結

1. FOR each SC-xxx → format_given_when_then()
2. FOR each SC-xxx → link_to_uc(UC-xxx)
3. FOR each SC-xxx → link_to_inv(INV-xxx) IF applicable

## Step 3: 測試組織

| 目錄 | 內容 | 指派 Stage |
|------|------|-----------|
| unit/ | TC-xxx | Stage 8 |
| integration/ | TC-xxx | Stage 8 |
| e2e/ | TC-xxx | Stage 8 |
| bdd/ | SC-xxx | Stage 7 |
| property/ | SC-xxx | Stage 7 |

## Step 4: 產出

1. 寫入 `docs/bdd-scenarios.md`
2. 更新追溯矩陣

## Step 5: TC 斷言設計指引（LESSON-003）

1. **規則 1**：每個斷言測試一個關鍵字（BAD: ASSERT file contains "COSMETIC.*MINOR..." → GOOD: 分開 ASSERT）
2. **規則 2**：考慮多行佈局（enum 值可能分散在多行，不假設同行出現）
3. **規則 3**：生成後立即執行一遍（TC 生成完成後用 PowerShell/grep 執行所有 ASSERT，任一 FAIL → 修正後重新執行）
4. **規則 4**：CJK 編碼安全（PowerShell 搜尋含中文時使用 -Encoding utf8 或用 grep）

## Step 6: PGVG 驗證

1. **UC↔SC 覆蓋**：FOR each UC-xxx in input → ASSERT exists SC-xxx covering UC-xxx，逐一列出覆蓋映射
2. **INV↔SC 覆蓋**：FOR each INV-xxx → ASSERT at least one SC verifies INV-xxx，列出未被覆蓋的 INV
3. **Gherkin 格式**：FOR each scenario → ASSERT contains Given, When, Then
