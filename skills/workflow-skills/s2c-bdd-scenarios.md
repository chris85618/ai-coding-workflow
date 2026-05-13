# Skill: S2C BDD 場景生成

> **觸發條件**：Stage 7（BDD/ATDD）
> **輸入**：UC-xxx, INV-xxx
> **輸出**：SC-xxx → `docs/bdd-scenarios.md` + 測試檔案

---

## 執行協議

```
FOR each UC-xxx:
  generate_happy_path_scenario() → SC-xxx
  generate_alternative_flow_scenarios() → SC-xxx
  generate_exception_flow_scenarios() → SC-xxx
  generate_boundary_scenarios() → SC-xxx

FOR each SC-xxx:
  format_given_when_then()
  link_to_uc(UC-xxx)
  link_to_inv(INV-xxx) IF applicable

Test organization:
  unit/          → TC-xxx (Stage 8)
  integration/   → TC-xxx (Stage 8)
  e2e/           → TC-xxx (Stage 8)
  bdd/           → SC-xxx (this Stage)
  property/      → SC-xxx (this Stage)
```

產出 → `docs/bdd-scenarios.md` + 更新追溯矩陣

---

## TC 斷言設計指引 [LESSON-003]

```
規則 1: 每個斷言測試一個關鍵字
  BAD:  ASSERT file contains "COSMETIC.*MINOR.*MODERATE.*MAJOR"
  GOOD: ASSERT file contains "COSMETIC"
        ASSERT file contains "MINOR"
        ASSERT file contains "MODERATE"
        ASSERT file contains "MAJOR"

規則 2: 考慮多行佈局
  目標文件的 enum 值可能分散在多行（如 switch/case, IF/ELIF）
  不假設同行出現

規則 3: 生成後立即執行一遍
  TC 生成完成後，立即用 PowerShell/grep 執行所有 ASSERT
  任一 FAIL → 修正斷言或修正目標文件 → 重新執行

規則 4: CJK 編碼安全
  PowerShell 搜尋含中文內容時使用 -Encoding utf8
  或使用 grep 替代 Select-String
```

---

## Post-Generation Validation Gate (PGVG)

```
PGVG-1: UC↔SC 覆蓋
  FOR each UC-xxx in input: ASSERT exists SC-xxx covering UC-xxx
  逐一列出覆蓋映射

PGVG-2: INV↔SC 覆蓋
  FOR each INV-xxx: ASSERT at least one SC verifies INV-xxx
  列出未被覆蓋的 INV

PGVG-3: Gherkin 格式
  FOR each scenario: ASSERT contains Given, When, Then
```
