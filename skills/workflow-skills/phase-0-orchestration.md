# Skill: Phase 0 環境啟動編排

> **觸發條件**：AGENTS.md Step 1
> **輸入**：專案目錄路徑
> **輸出**：環境就緒 + Pipeline 完備度 + 路徑判定

---

## Step 1: 工具可用性檢查（優雅降級，ADR-GOV-017）

逐一檢查五套工具是否可用，記錄可用清單。缺任一工具不阻塞管線，該工具的步驟改走純 LLM 降級路徑並在報告中標注：

| 工具 | 檢查方式 | 降級路徑 |
|------|---------|---------|
| gstack | `~/.claude/skills/gstack/` 存在或 `/office-hours` 可路由 | 由 LLM 直接執行對應審查框架 |
| ECC | `/plan`、`tdd-workflow` skill 可路由 | Hooks 保障消失，改為每次編輯後手動 micro-validation |
| Understand Anything | `/understand` 可路由 | LLM 直接讀碼建立架構摘要 |
| SkillFortify | `skillfortify --version` | LLM 人工審查 skill/MCP 定義檔 |
| Ponytail | `/ponytail` 可路由 | LLM 直接套用 YAGNI/stdlib-first 心法（見 Operational Principle 10） |

若 gstack 已安裝但未設定持續 checkpoint：

```bash
gstack-config set checkpoint_mode continuous
```

若 gstack 未安裝，向使用者建議（不自動執行）：

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

## Step 2: 環境衛生與忽略清單驗證 (LESSON-048)

檢查專案根目錄 `.gitignore`，確保至少包含以下安全與二進位檔案排除項：
- `.coverage` (若使用 Python 測試覆蓋率)
- `.pytest_cache/`
- `.env`

若缺失，主動將其補入 `.gitignore`，以防止二進位或敏感資料進入 Git 追蹤。

## Step 2.5: Python 測試環境驗證 (LESSON-052)

檢查專案根目錄 `pytest.ini`，若專案採用 `src` 目錄結構，確保包含 `pythonpath = src`，以防 `ModuleNotFoundError`。若缺失則主動補入。

## Step 3: Pipeline 完備性檢查

觸發 `skills/workflow-skills/pipeline-completeness-check.md`。

取得 `completeness_score`。

## Step 4: 路徑判定

| 完備度 | 有原始碼 | 判定 |
|--------|---------|------|
| 100% | — | Resume（觸發 `workflow-resume.md`） |
| 60-99% | — | Resume from recorded position |
| 1-59% | 有（Path B） | Phase 1（程式碼理解） |
| 1-59% | 無（Path A） | Phase 2（專案分析） |
| 0% | 有（Path B） | Phase 1 |
| 0% | 無（Path A） | Phase 2 |

原始碼判定：掃描專案目錄，排除 docs/、node_modules/、.git/、dist/、build/ 後，是否有程式語言檔案（.ts/.js/.py/.java/.cs/.go/.rs 等）。

## Step 5: 工作流恢復

IF completeness_score >= 0.6 OR workflow-state.md 存在：
- 觸發 `skills/workflow-skills/workflow-resume.md`

## Step 6: 報告

輸出：
- completeness_score
- path_decision (A/B/Resume)
- next_action
