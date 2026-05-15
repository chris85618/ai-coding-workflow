# Skill: Phase 0 環境啟動編排

> **觸發條件**：AGENTS.md Step 1
> **輸入**：專案目錄路徑
> **輸出**：環境就緒 + Pipeline 完備度 + 路徑判定

---

## Step 1: gstack 首次引導

若 gstack 尚未初始化：

```bash
npx -y gstack@latest init
gstack-config set language zh-TW    # 繁體中文
gstack-config set checkpoint_mode continuous
```

## Step 2: 環境衛生與忽略清單驗證 (LESSON-048)

檢查專案根目錄 `.gitignore`，確保至少包含以下安全與二進位檔案排除項：
- `.coverage` (若使用 Python 測試覆蓋率)
- `.pytest_cache/`
- `.env`

若缺失，主動將其補入 `.gitignore`，以防止二進位或敏感資料進入 Git 追蹤。

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
