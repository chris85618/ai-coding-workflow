# ADR-STR-020: 領域驅動設計 (DDD) 實施準則

## 狀態
**Accepted**

## 背景
現有系統雖然採用了 Clean Architecture 的目錄結構，但在內部實作上仍偏向純物件導向分析與設計 (OOAD)，缺乏明確的領域驅動設計 (DDD) 概念。這導致 AI 在理解領域邏輯時容易產生偏差，且聚合根 (Aggregate Root) 的邊界不夠嚴謹，外部依賴可能直接指向內部實體。

## 決策
1. **聚合根優先原則**：
   - 識別 `Pipeline` 為核心聚合根，負責管理 `Stage` 實體。
   - 識別 `TraceabilityRegistry` 為追溯領域的聚合根，負責管理 `TraceableID` 實體。
2. **實體與值物件識別**：
   - 具備生命週期與唯一識別碼的物件定義為 **Entity**。
   - 僅用於描述屬性且具備不可變性的物件定義為 **Value Object**。
3. **通訊鏈約束**：
   - 外部適配器 (Adapters) 與應用層 (Application Use Cases) 僅能與聚合根進行通訊。
   - 聚合根內部的實體操作必須透過聚合根的方法進行。
4. **應用層與領域層分離**：
   - 將業務邏輯從框架層（如 LangGraph Nodes）與領域層（僅保留不變量驗證）分離至 `application/use_cases`。
5. **術語對齊**：
   - 程式碼註解、文件及變數命名應全面對齊 DDD 術語（Aggregate, Entity, VO, Repository, Domain Service, Application Service）。

## 影響
- **優點**：
  - 提高領域邏輯的凝聚力與可維護性。
  - 降低外部元件對內部實施細節的耦合。
  - 改善 AI 對業務領域的理解精度。
- **缺點**：
  - 重構工作量大，需確保 100% 測試覆蓋率不受影響。
  - 聚合根可能變得臃腫，需適度提取領域服務。

## 追溯
- **BG**: BG-005
- **FEA**: FEA-025
- **FR**: FR-051, FR-052, FR-053
- **UC**: UC-019, UC-020, UC-021
- **ADR**: ADR-STR-001 (Refinement)
