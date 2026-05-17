# ADR-STR-024: 消除 Stage 6 Invariants Verifier 內部對 frameworks 之外層動態導入以遵循依賴反轉原則

> **狀態**: Proposed
> **日期**: 2026-05-17T15:20:00+08:00
> **類別**: STRUCTURAL
> **決策者**: AI-Proposed+HITL
> **追溯**: INV-001, INV-002-v2, INV-003, FR-054
> **取代**: N/A
> **被取代**: N/A

---

## 背景

- 觸發 Stage/Phase: Stage 6 (形式化驗證設計) Hardening
- 觸發事件: Clean Architecture 深度合規與依賴反轉原則 (DIP) 的嚴格審查
- 前置條件: 在 `src/agentic_workflow/domain/algorithms/invariants_verifier.py:48` 中，動態使用了 `importlib.import_module("agentic_workflow.frameworks.graph.master_graph_builder")` 來加載框架層的 Builder，建構圖並執行 invariants 驗證。
- 約束: 領域層 (Domain Layer) 必須保持 100% 的純粹性。它絕對不能靜態或動態地導入 any 外層（如 Frameworks, Adapters）的組件。

## 決策

我們決定：
1. **移除領域層對外層的任何引用**：從 `src/agentic_workflow/domain/algorithms/invariants_verifier.py` 中徹底刪除 `if __name__ == "__main__":` 執行區塊與 `importlib` 的動態導入。使領域層的 `DAGInvariantVerifier` 保持 100% 純粹，無外層依賴。
2. **建立專屬外層運行指令碼**：在框架層創建 `src/agentic_workflow/frameworks/graph/invariants_run.py`，作為獨立的 invariants 驗證運行指令碼。該指令碼負責導入 `MasterGraphBuilder` (同在框架層) 及 `DAGInvariantVerifier` (內層領域，合法的向下依賴)，建構圖並調用驗證器。
3. **遷移與重構單元測試**：將 `tests/domain/algorithms/invariants_verifier/test_invariants_verifier_main.py` 與 `test_main_block.py` 改為測試框架層的 `invariants_run` 運行指令碼，確保 100.00% 的單元測試覆蓋率與 100% 的測試通過率。

## 理由

- **支持證據**: 舊有的 `importlib.import_module` 雖規避了靜態語法檢查，但在執行期仍然發生了 Domain -> Framework 的非法逆向調用，破壞了 Clean Architecture 的依賴單向性（內層不知曉外層）。
- **權衡取捨**: 移除了領域層文件直接作為 main 腳本運行的能力，但換取了 100% 純粹、無污染的領域模型與完美的依賴反轉原則實現。用戶仍可通過 `python -m agentic_workflow.frameworks.graph.invariants_run` 執行相同的驗證。
- **風險接受**: 無。

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|---------|
| **方案 A**: 保持現狀（使用 importlib） | 簡單，無須搬移代碼，驗證代碼仍在原文件。 | 破壞依賴反轉與整潔架構，Domain 層在執行期加載 Framework 層，屬於非法越界。 | 無法容忍任何形式的 Clean Architecture 違反。 |
| **方案 B**: 透過環境變數動態傳遞 Builder 類 | 規避了寫死字串的 dynamic import。 | 增加了不必要的配置複雜度，架構上依然是運行期非法依賴。 | 不符合 Ockham's Razor（務實簡潔性）。 |

## 後果

**正面**：
- (+) 領域層代碼完全清空外層污染，符合依賴反轉原則。
- (+) 靜態分析與運行期依賴均完美遵循 Clean Architecture 單向向下原則。
- (+) 測試套件的職責更加清晰：領域測試專注於驗證邏輯，框架測試專注於建圖與運行。

**負面**：
- (-) Standalone invariants 驗證腳本入口從 `python -m agentic_workflow.domain.algorithms.invariants_verifier` 移至 `python -m agentic_workflow.frameworks.graph.invariants_run`。

**風險**：
- N/A

## 影響分析

- **爆炸半徑**: 5 個 ID
- **跨 Stage 影響**: 2 個 Stage (Stage 5 OOAD, Stage 6 Formal Verification)
- **嚴重度**: MODERATE
- **受影響 ID**: CLS-028, INV-001, TC-012, TC-013, TC-014

## 架構影響

- **受影響模組/元件**: `invariants_verifier.py`, `invariants_run.py`, `test_invariants_verifier_main.py`, `test_main_block.py`
- **依賴方向變更**: 徹底消除 Domain -> Framework 的隱式動態依賴。
- **API 變更**: 無 API 變更。
- **資料模型變更**: 無。

## 驗證計畫

- 運行整個 pytest 套件，確保 100.00% 覆蓋率（特別是 `invariants_run.py` 的 statement 與 branch 覆蓋率為 100.00%）。
- 執行 `python -m agentic_workflow.frameworks.graph.invariants_run` 驗證其輸出。

## 變更紀錄 (Implementation Records)

### 變更 #1: 依賴反轉重構

- **日期**: 2026-05-17T15:25:00+08:00
- **類型**: CREATE | MODIFY
- **檔案**:
  - `src/agentic_workflow/domain/algorithms/invariants_verifier.py`
  - `src/agentic_workflow/frameworks/graph/invariants_run.py`
  - `tests/domain/algorithms/invariants_verifier/test_invariants_verifier_main.py`
  - `tests/domain/algorithms/invariants_verifier/test_main_block.py`
- **影響 ID**: CLS-028, INV-001, TC-012, TC-013, TC-014
- **爆炸半淨**: 5
- **嚴重度**: MODERATE
- **微驗證**: PASS

## 根因分析與教訓 (Root Cause & Lessons)

### LESSON-075: 避免以動態導入繞過整潔架構依賴限制

- **根因分類**: ARCHITECTURE_EROSION
- **根因描述**: 使用者在 domain 層使用了動態 importlib 加載 frameworks 層來規避靜態依賴檢查，導致架構設計的依賴逆向。
- **5 Whys**:
  1. 為什麼 invariants_verifier.py 需要導入 frameworks 的 builder？ → 因為要讓 invariants_verifier.py 作為 standalone 腳本運行時能實時編譯並驗證真實的 master graph。
  2. 為什麼不直接 import master_graph_builder？ → 因為直接導入會被靜態依賴檢查工具攔截，這違反了 Domain -> Framework 的依賴規則。
  3. 為什麼要使用 `importlib.import_module` 動態導入？ → 為了以運行期動態加載的形式規避靜態依賴檢查，同時保有 standalone 腳本編譯圖的功能。
  4. 為什麼這不好？ → 因為這僅僅是掩耳盜鈴，在運行期依賴方向依然是逆向的，Domain 層被強耦合至特定的 Framework 圖結構，使領域層代碼變得不純粹。
  5. 為什麼沒有將 standalone 腳本與領域邏輯拆分？ → 因為在技術規劃時未嚴格執行依賴反轉，將「運行/展示」的外層關注點（腳本）與「驗證規則」的內層關注點混淆在同一個領域文件內。
- **瓶頸識別**:
  - 最早可偵測點: Stage 5 OOAD 設計審核。
  - 介入類型: GUARD_STRENGTHENING
- **左移守衛**: 強化 Clean Architecture 設計審查，所有 entry points / standalone 腳本一律必須置於外層 (frameworks/app)，嚴禁在內層 (domain) 出現任何 dynamic imports 外層組件之行為。

## 關聯產出物

### 技術債 (DEBT-xxx)
N/A

### 風險 (RISK-xxx)
N/A
