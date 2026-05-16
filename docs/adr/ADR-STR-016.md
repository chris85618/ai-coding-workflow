# ADR-STR-016: 巨集驅動的配置與元資料同步

| 欄位 | 值 |
|------|-----|
| **ID** | ADR-STR-016 |
| **標題** | 巨集驅動的配置與元資料同步 |
| **狀態** | accepted |
| **類別** | STRATEGIC |
| **優先等級** | Medium |
| **背景** | 專案元資料（如名稱、版本）散落在多個設定檔（pyproject.toml, mkdocs.yml, sonar-project.properties）中，手動維護容易導致不一致。 |
| **決策** | 1. 使用 `mkdocs-macros-plugin` 作為元資料同步的橋樑。<br>2. 建立 `main.py` 讀取 `pyproject.toml` 作為 SSOT。<br>3. 在 `sonar-project.properties` 與 `config.yaml` 中使用 `${env:VAR}` 語法以支持環境變數置換。 |
| **後果** | 1. 提升配置的可維護性。<br>2. 建立 metadata 同步機制。<br>3. 增加對 `mkdocs-macros-plugin` 的依賴。 |
| **追溯** | FEA-017, FR-044 |
| **建立日期** | 2026-05-16T10:35+08:00 |
