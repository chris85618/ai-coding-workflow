# ADR-STR-025: 多維度 Clean Architecture 邊界違規與越界注入防禦檢測設計

> **狀態**: Accepted
> **日期**: 2026-05-17T15:23:00+08:00
> **類別**: STRUCTURAL
> **決策者**: AI-Proposed+HITL
> **追溯**: FR-068, FR-069, FR-070, FR-071, FR-072, FR-073, FR-074, UC-020
> **取代**: N/A
> **被取代**: N/A

---

## 背景

在 Clean Architecture 中，依賴關係必須嚴格地由外向內（Dependencies point inwards）。
在當前專案中，我們有四層：
1. `domain`（最內層）
2. `application`
3. `adapters`
4. `frameworks`（最外層）

為了確保這四個層級完全遵循單向向下（外層依賴內層，內層決不可知曉外層）的依賴規則，傳統的靜態導入語法檢查（如只檢查 `import` 語句）是不夠的。開發人員或惡意代碼可能會利用動態導入、反射、全域 Service Locator 尋找、字串形式的型別標註、直接讀取環境變數或直接進行檔案 I/O 等方式繞過 Clean Architecture 的邊界約束。

為了系統性、全面性地防堵這些越界行為，我們需要建立一個**多維度的架構邊界安全掃描器 (Architectural Guardrail Scanner)**，作為持續整合 (CI) 與本地微驗證的核心防禦設施。

## 決策

我們決定設計並實作 `CleanArchitectureBoundaryScanner` 於 `frameworks/validation/clean_architecture_scanner.py` 中，該掃描器必須包含以下檢測維度與規則：

### 1. 檢測層級與合法邊界定義

- **`domain` 層級代碼**：
  - 禁止以任何形式存取 `application`、`adapters`、`frameworks`。
- **`application` 層級代碼**：
  - 禁止以 any 形式存取 `adapters`、`frameworks`。
- **`adapters` 層級代碼**：
  - 禁止以 any 形式存取 `frameworks`。
- **`frameworks` 層級代碼**：
  - 允許存取所有層級。

### 2. 八大越界檢測維度 (Detection Categories)

| 編號 | 維度名稱 | AST / 正則檢測機制 | 理由 |
|------|----------|-------------------|------|
| **1** | **靜態導入越界 (Static Imports)** | 掃描 `ast.Import` 與 `ast.ImportFrom` 的模組名稱。若其絕對路徑/模組名稱包含 outer layers，則判定違規。同時防範相對導入超出層級邊界。 | 阻斷靜態寫死的外層依賴。 |
| **2** | **動態導入越界 (Dynamic Imports)** | 掃描 `ast.Call` 中對 `importlib.import_module` 或 `__import__` 的調用。若傳入的字串常數包含外層模組，即屬違規。 | 阻斷藉由動態反射繞過編譯期檢查的行為。 |
| **3** | **代碼動態執行 (Exec & Eval)** | 阻斷在 `domain` 或 `application` 內使用 `exec` 或 `eval`。 | 防範利用代碼字串動態執行外層操作的惡意注入。 |
| **4** | **模組快取越界查詢 (sys.modules)** | 掃描對 `sys.modules` 的 subscript 存取。若 slice 中包含 outer layers，判定違規。 | 阻斷直接透過 sys.modules 的 dictionary 獲取外層模組實例。 |
| **5** | **全域 DI 容器與 Locator 濫用** | 阻斷內層 (`domain`, `application`) 直接導入或參照 `frameworks.dependency_container` 中的 `DependencyContainer`。 | 避免依賴注入容器被內層當作 Service Locator 使用，破壞依賴反轉。 |
| **6** | **字串型別標註越界 (String Annotations)** | 掃描型別註解（包括 `ast.AnnAssign` 與 `ast.arg` 中的 annotation）之字串常數。若包含外層類型的字串（例如 `"frameworks.graph.MasterGraph"`），判定違規。 | 避免字串標註產生的隱性依賴。 |
| **7** | **直接環境變數存取 (Environment Access)** | 阻斷內層直接讀取 `os.environ` 或 `os.getenv`。 | 環境配置必須經由外層統一解析後透過 Value Object 或 Port 注入，避免內層污染。 |
| **8** | **直接檔案 I/O 存取 (File I/O Bypass)** | 阻斷 `domain` 層級代碼直接調用全域 `open(...)` 或對 `Path` 物件進行讀寫操作（`read_text`, `write_text` 等）。 | 檔案讀寫屬於基礎設施關注點，必須經由 Repository Port 進行隔離。 |

## 理由

- **支持證據**: 過去的重構（如 `ADR-STR-024`）暴露出開發過程中容易因方便而引入 `importlib.import_module` 繞過依賴檢查的痛點。建立主動式的架構守護程序，可保證隨著時間的推移，代碼庫不會發生「架構腐化 (Architecture Erosion)」。
- **權衡取捨**: 嚴格的檔案 I/O 與環境變數限制可能會增加編寫極端邊界單元測試的 mock 負擔，但這極大提升了領域模型的純粹性與可測試性，為企業級應用的長遠維護奠定基礎。

## 後果

**正面**：
- (+) 實踐了「全防禦、全覆蓋」的 Clean Architecture 保護網。
- (+) 本地微驗證 `micro-validation.md` 與 CI 流程將能自動攔截任何越界代碼，防止架構設計隨意劣化。
- (+) 促使開發者遵循 Port & Adapter 與依賴反轉原則，編寫更高質量的模組化代碼。

**負面**：
- (-) 開發者在 `domain` 中若有臨時寫入檔案或調用環境變數的除錯代碼，將會被掃描器阻斷，必須使用規範的 Adapter/Port 模式。

---

## 影響分析

- **爆炸半徑**: 3 (validation sub-module, test files, workflow log)
- **跨 Stage 影響**: Stage 6 (形式化驗證) 與 Stage 8 (TDD)
- **嚴重度**: MINIMAL (僅新增檢測工具與測試)
- **受影響 ID**: CLS-028, INV-026

## 驗證計畫

- 撰寫 `test_clean_architecture_scanner.py` 單元測試，在其中建構臨時的 Python 違規檔案與合規檔案，驗證 8 種注入維度的攔截準確性。
- 將此掃描器集成至專案的測試運行中，對 `src/agentic_workflow/` 內的所有生產代碼進行全面掃描，確保當時代碼庫為 **0 違規**。
