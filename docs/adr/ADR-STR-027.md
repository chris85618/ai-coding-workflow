# ADR-STR-027: 架構邊界防護與註解封鎖硬化

## 狀態
Accepted

## 背景
先前系統在內三層（Domain/Application/Adapters）之內僅限制 `# type: ignore`，而對於其他的 `# type` 註解（例如類型註記 `# type: List[int]`）未進行封鎖。
此外，對於外部的 `# pragma: no cover` 雖然有封鎖，但未封鎖其他的 pragma 指令（例如 `# pragma: no branch`）。
為了提供最強健的 Clean Architecture 防護，必須對靜態掃描器（`CleanArchitectureBoundaryScanner`）進行硬化，以保證代碼的最高品質：
1. 在內三層（`rank <= 3`）中**絕對禁用所有 `# type` 註解**，任何 PEP 484 類型注釋均不被允許，以強制開發者使用標準 Python Type Hinting。
2. 在 python entrypoint 之外的任何地方**絕對禁用所有 `# pragma` 註解**，以防堵任何暗中規避測試覆蓋率或分支驗證之行為。

## 決策
1. **修改 `CleanArchitectureBoundaryScanner` 行解析邏輯**：
   - 提取每行代碼中的註解部分。
   - 若註解去空格後以 `type` 或 `pragma` 開頭，且其後緊鄰冒號（`:`）或空格，則視為命中對應之規則。
   - 此法可精準識別 PEP 484 註解及 pragma 宣告，同時防範正常詞語（如 `type of ...` 或 `pragmatic`）的誤判。
2. **硬化型別註解封鎖**：
   - 只要 `current_rank <= 3` 且命中上述 `type` 註解檢核，即拋出 `type_ignore_abuse` 違規，不論後綴為何。
3. **硬化 pragma 註解封鎖**：
   - 只要命中上述 `pragma` 註解檢核，且該行不包含 `if __name__ == '__main__':` 結構，即拋出 `pragma_no_cover_abuse` 違規，禁止規避。
4. **補齊全面覆蓋測試**：
   - 新增註解後綴 Permutations 的分支覆蓋測試，達成 100.00% statement 與 branch 測試覆蓋率。

## 後果
- **優點**：
  - 強制執行完全合規的 Python Type Hinting，杜絕 PEP 484 註解遺留。
  - 完全封堵規避 coverage 及分支測試之漏洞，防護層級達至最高境界。
  - 靜態掃描器核心代碼達成完美之 100.00% 覆蓋率，免除任何 pragma 逃生門。
- **缺點**：
  - 若有極端第三方庫必須在內層代碼以 PEP 484 注釋標記時，需引導重構或將適配層移出。
