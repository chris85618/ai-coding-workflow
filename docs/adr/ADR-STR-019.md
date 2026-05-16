# ADR-STR-019: Mypy 常用執行參數固化

## 狀態
Accepted

## 背景
在目前的開發流程中，執行 Mypy 靜態分析時需額外附加 `--ignore-missing-imports` 與 `--explicit-package-bases` 參數才能確保檢查範圍與行為符合預期。手動附加參數增加了開發者的認知負擔，且在 CI/CD 環境中若漏掉參數可能導致分析結果不一致。

## 決策
將以下參數固化至 `pyproject.toml` 的 `[tool.mypy]` 配置區塊中：
1. `ignore_missing_imports = true`: 忽略第三方庫缺失的類型定義，避免因依賴庫未提供型別檔而導致的報錯。
2. `explicit_package_bases = true`: 明確指定 package base，解決在複雜目錄結構（如 `src/` 佈局）下的模組解析問題。

## 後果
- **優點**:
    - 簡化 CLI 調用，開發者只需執行 `python -m mypy src` 即可獲得完整檢查。
    - 確保本地環境與 CI 環境的檢查行為完全一致。
    - 降低新進成員的環境設定難度。
- **缺點**:
    - 全域忽略缺失匯入可能會掩蓋某些真正需要型別定義的依賴項問題。

## 追溯
- **FR**: [FR-045](../traceability-matrix.md)
- **FEA**: [FEA-021](../traceability-matrix.md)
