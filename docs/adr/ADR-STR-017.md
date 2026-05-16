# ADR-STR-017: 配置與文件巨集的生命週期隔離 (Lifecycle Isolation)

| 欄位 | 值 |
|------|-----|
| **ID** | ADR-STR-017 |
| **標題** | 配置與文件巨集的生命週期隔離 |
| **狀態** | accepted |
| **類別** | STRATEGIC |
| **優先等級** | High |
| **背景** | 隨著 `mkdocs-macros-plugin` 的引入，建置時 (Build-time) 的變數置換與應用程式運行時 (Run-time) 的變數插值可能產生權責模糊，甚至導致安全漏洞（如在文件中洩漏 API Key）。 |
| **決策** | 1. **生命週期隔離**：`mkdocs-macros` 僅限於處理文件顯示與專案元資料（Metadata）；應用程式配置仍由 `WorkflowConfigLoader` 於運行時處理。<br>2. **目錄定位**：文件巨集腳本必須放置於 `docs/macros.py`，而非專案根目錄。<br>3. **安全性黑名單**：巨集禁止讀取包含 `KEY`, `TOKEN`, `SECRET` 等字眼的環境變數。<br>4. **語法解碼規範**：運行時支援 `${VAR:-DEF}` (POSIX 標準)，建置時僅支援 `{{ macro() }}`，以防止語法衝突。 |
| **後果** | 1. 確保 API Key 等敏感資訊不會因文件建置而流向 HTML 靜態網頁。<br>2. 符合 Clean Architecture 的職責分離原則。<br>3. 保持根目錄整潔。 |
| **追溯** | FEA-018, FR-044 |
| **建立日期** | 2026-05-16T10:37+08:00 |
