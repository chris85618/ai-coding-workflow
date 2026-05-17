# ADR-STR-026: 白名單全面擴展至內三層 (Domain/Application/Adapters)

> **標準**: ISO 42010 / Clean Architecture
> **狀態**: APPROVED
> **建立日期**: 2026-05-17
> **負責人**: HITL & AI Pair

---

## 1. 脈絡與背景 (Context)

本專案採用嚴格的 Clean Architecture 架構。先前我們實作了 `CleanArchitectureBoundaryScanner` 以透過 AST 靜態掃描程式碼庫，其中定義了 `ALLOWED_DOMAIN_DEPENDENCIES` 白名單，嚴格限制 `domain` 層僅能依賴 Python 最核心的內建庫與 `icontract`，完全阻絕與任何外層 framework 或具體第三方庫的耦合。

為了達到最極致的 Clean Architecture 架構，外層與 OS/第三方依賴相關的實作應完全收攏至最外層的 `frameworks`。而作為中間接頭的 `adapters` 層，應該同樣保持極高的「純粹度」：
1. **完全不依賴** 任何特定的第三方框架（如 `langgraph`、`langchain`、`sonarqube` 等）。
2. **完全不依賴** 與 OS 行為深度耦合的標準庫（如 `os`、`sys`、`subprocess`、`ast` 等，但可透過 Dependency Inversion 依賴由外層注入的 `FilesystemIO` 或 `SubprocessExecutor` 抽象介面）。
3. 確保 `domain`、`application`、`adapters` 這內三圈程式碼的 framework-independence。

因此，我們需要將白名單檢驗範圍自 `domain` 擴展至 `domain`、`application`、`adapters` 這內三圈（Rank <= 3），並且嚴格禁止在這些層中使用 any 非白名單的導入。

## 2. 決策內容 (Decision)

1. **擴展白名單範圍**：
   - 將 AST Scanner 中的 `ALLOWED_DOMAIN_DEPENDENCIES` 改名為 `ALLOWED_INNER_DEPENDENCIES`。
   - 將 AST 檢查範圍擴展至 `current_rank <= 3` (即 `domain`, `application`, `adapters` 皆套用白名單限制)。
   
2. **重塑 `adapters` 層**：
   - 原先在 `adapters` 中引入非白名單模組（例如 `json`、`pathlib`、`langgraph`、`langchain`、`sonarqube`）的具體實作，全面**移至 `frameworks` 層**。
   - `adapters` 層中僅保留純粹的介面、VO、資料轉換邏輯，以及委託 `frameworks` 註冊之全域委派的純粹委託器（例如 `filesystem.py` 及 `subprocess.py` 中被 `try...except` 改寫的委託介面）。
   
3. **具體遷移路徑**：
   - `adapters/langgraph/` $\rightarrow$ `frameworks/langgraph/` (LangGraph 本身即為特定的 Orchestrator 框架，其節點與 checkpointer 實作完全移至 frameworks)。
   - `adapters/llm/` $\rightarrow$ `frameworks/llm/` (LangChain-based LLM 實作與特定的 OpenAI/Anthropic 整合完全移至 frameworks)。
   - `adapters/sonarcloud/sonar_adapter.py` $\rightarrow$ `frameworks/sonarcloud/sonar_adapter.py` (sonarqube-api 客戶端實作完全移至 frameworks)。
   - `adapters/persistence/file_repository.py` $\rightarrow$ `frameworks/persistence/file_repository.py` (JSON 檔案儲存實作移至 frameworks)。
   - `adapters/persistence/checkpoint_repository.py` $\rightarrow$ `frameworks/persistence/checkpoint_repository.py` (JSON Checkpoint 儲存實作移至 frameworks)。
   - `adapters/persistence/hook_config_loader.py` $\rightarrow$ `frameworks/persistence/hook_config_loader.py` (JSON Hook 載入器移至 frameworks)。

4. **依賴注入容器對齊**：
   - 容器與 Bootstrap 完全定義在 `frameworks/` 層。它負責將位於 `frameworks/` 層的具體實作（例如 `FileTraceableIDRepository`）注入到 `application/` 層的 Use Case 埠（Ports）中。

## 3. 預期後果與優點 (Consequences & Benefits)

- **無框架耦合**：`domain`、`application`、`adapters` 不受特定第三方庫升級的破壞性影響。
- **易於單元測試**：內三層完全不受環境、外部 Socket 或硬碟 IO 影響，能保持 100.00% 潔淨的記憶體測試。
- **符合 Clean Architecture 經典設計**：內三層皆為外層（Frameworks & Drivers）的純粹介面轉接層與核，保證架構永續。
