# ADR-STR-027: 架構邊界防護與全層 pragma/type 封鎖硬化

## 狀態
Accepted (2026-05-17 修訂 — 擴大至 frameworks 層)

## 背景
### 第一版 (v1) 問題
先前系統在內三層（Domain/Application/Adapters）之內僅限制 `# type` 與 `# pragma` 系列的違規。
`frameworks` 層（rank 4）因為被視為「最外層享有最高特權」而被排除在 pragma 和 type 封鎖規則之外。

這是**嚴重的架構承諾違背**：
- `# pragma: no branch`, `# pragma: no cover` 等規避測試覆蓋率或分支驗證之行為在 frameworks 層依然合法。
- 這讓 frameworks 層的程式碼成為 coverage 規避的安全地帶，破壞了整個防護體系的完整性。
- 已發現 20+ 個現有 frameworks 層違規（`iteration_nodes.py`, `master_pipeline_nodes.py`, `micro_validation_nodes.py`, `main.py`, `invariants_run.py`）。

### 第二版 (v2) 決策
**所有四層一律平等**：pragma 和 type 封鎖適用於整個 codebase，無層級例外。
唯一例外為 **`if __name__ == '__main__':` 所在行**的 pragma 標記（保留 entry point 本身的可測試性）。

## 決策

1. **全層 pragma 封鎖**：
   - 移除 `current_rank <= 3` 的 pragma 封鎖限制條件。
   - 所有四層（domain/application/adapters/frameworks）中，任何 `# pragma` 系列的標記，只要不在 `if __name__ == '__main__':` 行上，一律觸發 `pragma_no_cover_abuse` 違規。
   - `# pragma: no branch`, `# pragma: no cover`, `# pragma: whatever` 全面禁止。

2. **全層 type 封鎖**（維持既有決策）：
   - 在內三層（`rank <= 3`）中絕對禁用所有 `# type` 系列的 PEP 484 類型注釋。
   - frameworks 層因為是最外層，`# type` 原本不受限制 — 此政策繼續適用（`# type` 僅限內三層禁止）。

3. **Static Scanner 實作更新**：
   - `CleanArchitectureBoundaryScanner.scan_file` 中的 pragma 檢查必須移除 `if self.current_rank <= 3:` 條件守衛。
   - tokenize 路徑與 fallback regex 路徑均需同步更新。

4. **測試先行（Red-Green 流程）**：
   - 必須先以新的測試案例確認 frameworks 層既有違規被掃描器正確偵測出（測試紅燈）。
   - 修正掃描器邏輯後確認測試轉為綠燈。
   - 修正生產程式碼中的違規是**下一個獨立步驟**。

## 後果

- **優點**：
  - 整個 codebase 的 coverage 規避防護完整統一，無一例外。
  - 測試覆蓋率報告的真實性有保障 — 不存在任何可藉由 pragma 偽裝的虛假覆蓋率數字。
  - 架構承諾 (ADR-STR-027 v2) 完整落地。

- **缺點**：
  - 現有 frameworks 層中所有 `# pragma: no branch` 使用均成為違規，須逐一重構。
  - `main.py` 與 `invariants_run.py` 中的 `if __name__ == '__main__':  # pragma: no cover` 在 entry point 行上，屬於合法例外，不受影響。

## 涉及檔案（需修正的違規）

| 檔案 | 違規行 | 種類 |
|------|--------|------|
| `frameworks/graph/iteration_nodes.py` | L13, L19, L24, L29, L35 | `# pragma: no branch` |
| `frameworks/graph/master_pipeline_nodes.py` | L13, L18, L23, L28, L33, L38, L43, L48, L53, L58, L63 | `# pragma: no branch` |
| `frameworks/graph/micro_validation_nodes.py` | L13, L18, L23, L28, L33, L38, L43, L48, L53, L58 | `# pragma: no branch` |
| `frameworks/main.py` | L27 | `# pragma: no cover` — **例外合法** (entry point 行) |
| `frameworks/graph/invariants_run.py` | L26 | `# pragma: no cover` — **例外合法** (entry point 行) |
| `frameworks/validation/clean_architecture_scanner.py` | L170, L206 | `# pragma: no branch` — 掃描器本身的 message 字串（非 comment），無違規 |


## 變更紀錄 (Implementation Records)

### 變更 #1: 品質守衛硬化 - 限制 frameworks 模組層級函數

- **類型**: MODIFY
- **日期**: 2026-05-18T01:26:00+08:00
- **檔案**:
  - `tests/test_code_quality.py`
  - `docs/traceability-matrix.md`
- **影響 ID**: TC-QUALITY-011, FR-QUALITY-010
- **爆炸半徑**: 2
- **嚴重度**: COSMETIC
- **微驗證**: PASS
- **根因分類**: NEW_CAPABILITY
- **根因描述**: 實作 frameworks 層中禁止存在模組層級的 function 或 async function 定義，以防止領域邏輯外溢，並進一步完備與硬化 pytest 靜態 AST 檢查套件。
- **左移動作**: 新增 AST 模組層級檢查並更新 Traceability Matrix 與 ADR。
- **LESSON-076**: [LESSON-076](file:///c:/Users/chris/Desktop/ai-coding-workflow/docs/traceability-matrix.md#L455)

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-076: 限制外層模組層級函數定義防止領域與應用邏輯外溢

- **根因分類**: NEW_CAPABILITY
- **根因描述**: frameworks 層作為最外層，易因開發便利性將輔助函數隨意定義於 class 之外，從而導致未經架構約束的領域邏輯或應用邏輯外溢、混亂並散落於模組層級。
- **5 Whys**:
  1. 為什麼 frameworks 層會有 module-level 函數定義的風險？ → 因為有些開發者在編寫輔助邏輯或執行入口時，習慣直接在 module 層級寫 `def helper_func():`。
  2. 為什麼這不好？ → 因為這會使得該函數無法被 class 的架構不變量約束，且可能繞過領域層與應用層的介面直接處理資料，形成灰色地帶。
  3. 為什麼需要硬性 pytest AST 檢測？ → 為了以 100% 自動化、靜態分析的手段在 CI/CD 階段硬性攔截此類定義，確保外層程式碼完全由 classes (符合 DIP 與介面約定) 組成。
  4. 最早可偵測點在哪？ → Stage 8 品質守衛與 TDD 驗證點。
  5. 什麼結構性改變可以消除它？ → 於 `test_code_quality.py` 實作 AST `ModuleLevelFunctionVisitor` 靜態掃描，完全封鎖 top-level / branch-nested 的 function 與 async function 定義。
- **瓶頸識別**:
  - 問題發生點: Stage 8 TDD & Quality Rules
  - 逃逸路徑: 無（此為新增品質不變量守衛）
  - 最早可偵測點: tests/test_code_quality.py
  - 瓶頸位置: tests/test_code_quality.py
  - 介入類型: NEW_GUARD
  - 預期覆蓋: 阻擋任何在 frameworks Python 檔案中 class 之外定義的 function 或 async function。
- **左移守衛**: 實作 `test_frameworks_no_module_level_functions()` AST 走訪檢驗，無任何免除條件。
- **更新的 Skill**: N/A (此變更直接硬化專案級測試 `test_code_quality.py`，不影響框架級 skill)。

## 關聯產出物

### 技術債 (DEBT-xxx)
- N/A

### 風險 (RISK-xxx)
- N/A


