# Retro Log — Unified Agentic Workflow

## [0.1.3] — 2026-05-16

### 成功事項
1. **測試架構重構 (FEA-024)**: 成功將測試套件細粒度化，解決了大規模測試集的維護性與導引問題。
2. **SSOT 配置整合**: 成功將所有工具配置固化至 `pyproject.toml`，消除了配置漂移風險。
3. **品質閘門自動化**: `SonarCloudAdapter` 的實作使品質監控從「手動查閱」變為「系統整合」，提昇了治理強度。
4. **100% 覆蓋率持績**: 在大規模重構後依然維持 100.00% 覆蓋率，證明了 BDD + TDD 的穩健性。

### 挑戰與學習
1. **BDD `@staticmethod` 陷阱**: 在類別化 BDD 測試時，若不使用 `@staticmethod`，`pytest` 會因無法為 `self` 提供 fixture 而失敗。這是一個關鍵的 LESSON-045。
2. **命名空間衝突**: 在重構目錄結構時，必須同步移除 legacy 檔案，否則 `pytest` 的 import 機制會因同名模組而崩潰。
3. **PowerShell 腳本解析**: PowerShell 對變數與引號的解析較為敏感，在編寫自動化指令時應優先考慮簡單性或使用 `.ps1` 檔案。

### 技術債 (P3)
- **DEBT-008**: SonarCloud 異步邏輯優化。目前的同步實作在 Web API 響應慢時會阻塞管線，未來應改為 async/await 模式。

### 下一步建議
- 探索代碼生成 AI 的「預編譯」模式，以減少大型測試集的收集時間。
- 加強對複雜度指標的精確過濾，避免因第三方套件導致的 False Positive。
