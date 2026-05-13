# Phase 1：程式碼理解

> **主角：Understand Anything**
> 在動手之前先徹底理解既有程式碼的架構、依賴關係和複雜度。
> Path A (Greenfield) 時跳過步驟 1.1-1.5，僅建立空白知識圖譜框架。

---

## 步驟 1.1：建立知識圖譜

```
/understand
```

| 條件 | 行為 |
|------|------|
| 首次分析（無 `knowledge-graph.json`） | 全量分析，5 個 agent pipeline |
| 圖譜存在但程式碼已變更 | 增量更新，僅分析變更檔案 |
| 圖譜存在且無變更 | 跳過，報告「已是最新」 |
| 需要強制重建 | `/understand --full` |

**產出：** `.understand-anything/knowledge-graph.json`

## 步驟 1.2：視覺化探索

```
/understand-dashboard
```

在瀏覽器中開啟互動式 Dashboard，查看：
- 架構分層（UI / API / Service / Data）
- 檔案/函式/類別的依賴關係圖
- 複雜度熱點
- 導覽路線（Tour）

## 步驟 1.3：針對性問答

```
/understand-chat <你的問題>
```

範例：
- `/understand-chat 認證流程是如何運作的？`
- `/understand-chat 資料庫 schema 在哪裡定義？`
- `/understand-chat 哪些模組依賴 payments service？`

## 步驟 1.4：深入特定元件（按需）

```
/understand-explain <路徑>
```

對需要深入了解的元件進行詳細解說，包括架構角色、內部結構、外部連接和資料流。

## 步驟 1.5：評估現有變更（若有 WIP 變更）

```
/understand-diff
```

如果 repo 上已有未提交的變更或正在進行的 feature branch，使用 diff 分析來理解：
- 哪些元件被修改
- 爆炸半徑（影響範圍）
- 跨層影響
- 風險評估

**產出：** `diff-overlay.json`（可在 Dashboard 上視覺化）

## Phase 1 產出物

| 產出 | 用途 |
|------|------|
| `knowledge-graph.json` | 程式碼庫結構化知識，供後續所有 Phase 參考 |
| Dashboard URL | 隨時可回來查閱的視覺化介面 |
| 理解筆記 | 記錄架構決策、技術債、複雜度熱點 |
| `diff-overlay.json`（可選） | 既有變更的影響分析 |

> Phase 1 的產出不只是一次性的。在後續所有 Stage 中，可以隨時回來用 `/understand-chat` 查詢，或用 `/understand-explain` 深入特定元件。
