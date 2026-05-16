# ADR-GOV-027: 以 pyproject.toml 為全域配置唯一事實來源 (SSOT)

| 欄位 | 值 |
|------|-----|
| **ID** | ADR-GOV-027 |
| **標題** | 以 pyproject.toml 為全域配置唯一事實來源 |
| **狀態** | accepted |
| **類別** | GOVERNANCE |
| **優先等級** | Critical |
| **背景** | 專案配置散落在 `sonar-project.properties`, `mkdocs.yml`, `.safety-policy.yml` 等多個檔案中，增加了維護成本與資訊不一致的風險。 |
| **決議** | 1. **集中化**：所有工具鏈（Safety, SonarCloud, MkDocs）的靜態配置必須優先定義於 `pyproject.toml`。<br>2. **同步機制**：<br>   - **Safety**：直接使用內建的 `[tool.safety]`。<br>   - **MkDocs**：透過 `docs/macros.py` 動態注入 `[tool.mkdocs]` 配置。<br>   - **SonarCloud**：透過 `scripts/sync_sonar_props.py` 從 `[tool.sonar]` 自動生成屬性檔。<br>3. **自動化 (Automation)**：實施 Git `pre-commit` Hook，確保每次提交前自動執行 `sync_sonar_props.py`，消除人為錯誤。<br>4. **禁止手動編輯**：被同步的次要設定檔（如 `sonar-project.properties`）禁止手動編輯。 |
| **後果** | 1. 實現單點管理 (Single Point of Management)。<br>2. 簡化新環境的配置流程。<br>3. 雖然增加了同步腳本的維護，但降低了配置漂移的風險。 |
| **追溯** | FEA-019, FR-043, FR-044 |
| **建立日期** | 2026-05-16T10:46+08:00 |
