# ADR-STR-018: 強制 Git Hook 整合 Ruff Format

## 狀態
- **ID**: ADR-STR-018
- **標題**: 強制 Git Hook 整合 Ruff Format
- **日期**: 2026-05-16
- **狀態**: PROPOSED
- **決策者**: Antigravity, USER

## 背景
專案使用 Ruff 作為主要格式化與靜態分析工具。為了確保所有提交的程式碼均符合規範，需要一個自動化機制在開發者 commit 前強制執行格式化，避免因格式問題導致 CI 失敗。

## 決策
1. 修改 `scripts/install_hooks.py`，在生成的 `pre-commit` 鉤子中加入 `python -m ruff format src tests`。
2. 該指令將優先於現有的 `sync_sonar_props.py` 執行。
3. 格式化後，若檔案發生變動，開發者需自行 `git add`（或在未來考慮自動 add，但目前傾向維持開發者顯式確認）。

## 後果
- **優點**: 
    - 程式碼風格 100% 一致。
    - 消除 CI 中格式化檢查的失敗風險。
- **缺點**: 
    - Commit 速度略微下降（Ruff 極快，影響微小）。
    - 開發者若在 commit 時檔案被修改，可能需要再次 stage。

## 追溯
- **需求**: FR-044, FR-045
