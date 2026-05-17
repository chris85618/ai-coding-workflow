# ADR-STR-027: 程式碼品質與特例禁止規範 (型別忽略與省略號限制)

> **標準**: ISO 42010 / Code Quality Guidelines
> **狀態**: APPROVED (UPDATED: 100% ABSOLUTE BAN)
> **建立日期**: 2026-05-17
> **負責人**: HITL & AI Pair

---

## 1. 脈絡與背景 (Context)

在大型軟體專案的開發與演進過程中，為了維持最高品質與健全度，應盡可能避免使用帶有副作用或隱藏合約的特殊程式碼構造：

1. **`# type: ignore` 的濫用**：
   - 雖然 Mypy 在某些第三方庫沒有標註型別時需要透過 `# type: ignore` 繞過，但在生產環境程式碼（`src/`）中隨意使用 `# type: ignore` 會削弱靜態型別分析的保護，隱藏潛在的型別不對序與 Runtime 錯誤。
   - 應將 `# type: ignore` 視為極端情況下的妥協，非必要應完全禁用。若必須使用，應提供充分理由，且應儘量以具體的 type assertion（如 `cast`）、型別適配器、介面定義或定義 `.pyi` Stub 檔來取代。

2. **省略號 `...` 取代 `pass`**：
   - 在 Python 中，省略號 `...` 常在 stub 檔案（`.pyi`）或抽象基底類別（Protocols/Abstract Methods）中用於預留型別定義。
   - 然而，在具體實作類別的乾跑方法（dry run method/function）中，使用 `...` 會降低程式碼的可讀性，且容易與 stub 檔混淆。
   - 正常的具體實作或不需要操作的乾跑方法，必須嚴格且全面使用標準的 `pass` 關鍵字，不可使用 `...` 取代。

為了維持此一極致的高品質標準，我們需要制定明確的禁令，並將現有違規列為技術債務（Tech Debt）進行系統性修復。

## 2. 決策內容 (Decision)

1. **限制 `# type: ignore`**：
   - 生產環境程式碼（`src/`）中禁止隨意使用 `# type: ignore`。
   - **唯一容許的例外**：第三方庫（例如 `langgraph`、`sonarqube` 等）沒有提供完整型別註釋且無第三方 stub 可用，或需要動態載入外部非靜態連結模組時。
   - 即使在例外狀況下使用，也必須在同列加上具體的錯誤代碼，如 `# type: ignore[attr-defined]`，禁止使用無限制 Asserts。
   - 本身內圈（Domain、Application、Adapters）中應完全為 0 `# type: ignore`，以確保核心架構型別安全。

2. **禁止使用 `...` 代替 `pass`**：
   - 具體實作類別或函數的 dry run / empty 邏輯，禁止使用省略號 `...`，必須全面使用 `pass`。
   - `...` 僅被允許出現在 `typing.Protocol` 介面聲明或 `@abstractmethod` 抽象方法聲明中。

3. **落實為技術債務（Tech Debt）**：
   - 將「清理 src/ 下非必要的 `# type: ignore`」與「將 dry run 實作中的 `...` 替換為 `pass`」列入 `docs/tech-debt-register.md`。
   - 新實作（如內三層白名單擴展重構）在開發過程中應嚴格遵循本規範，禁止引入任何新的違規。

## 3. 預期後果與優點 (Consequences & Benefits)

- **100% 精確的靜態分析**：幾乎清空 `# type: ignore` 後，Mypy 能夠發揮最大安全網防護，杜絕 runtime 類型崩潰。
- **程式碼可讀性提昇**：區分了 Protocol/Abstract 方法（使用 `...`）與具體 Dry run 方法（使用 `pass`），代碼意圖更直觀、更具 builder-to-builder 專業風格。
- **高標準工程素養**：展現高階軟體工程師對細節與程式碼衛生的極致追求，符合全球一流 startup 團隊水準。
