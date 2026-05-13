# Skill: 全域窮舉搜尋協議

> **觸發條件**：任何涉及檔案系統層級掃描的任務（殘留清除、關鍵字審計、DbC 缺口盤點、引用完整性檢查等）
> **觸發關鍵字**：search, scan, find, grep, locate, audit, enumerate, 搜尋, 掃描, 尋找, 查找, 盤點, 審計, 窮舉*
> **輸入**：target_concept（要搜尋的概念）
> **輸出**：搜尋結果 + 證據記錄
> **ADR**: ADR-GOV-013（全域搜尋協議）
>
> *「窮舉」特殊處理：見 Step 0 適用性判定。

---

## Step 0: 適用性判定

1. 判斷當前任務是否涉及**檔案系統層級掃描**（即需要 grep/ripgrep 等工具在檔案中搜尋文字）
2. IF 任務僅為「窮舉式邏輯分析」（如窮舉所有可能的設計方案）且不涉及檔案搜尋 → **跳過本 skill**，回到原任務
3. IF 任務涉及以下任一情境 → **繼續 Step 1**：
   - 殘留清除（刪除/重命名後檢查引用）
   - 關鍵字審計（確認某概念是否仍存在於程式碼庫）
   - DbC 缺口盤點（搜尋缺少前/後置條件的位置）
   - 引用完整性檢查（確認所有 cross-reference 有效）
   - 任何需要「在整個 repository 中尋找所有出現位置」的任務

## Step 1: 最短共通子字串提取

1. 從 target_concept 提取最短核心詞素作為搜尋關鍵字
2. 使用最短子字串而非完整片語，以確保不遺漏變體
3. 範例：搜「FIX-only 逃生門」→ 用 `FIX` 而非 `若 FIX` 或 `僅 FIX`

## Step 2: 跨語言 Pattern 展開

1. 對每個關鍵字，展開為所有專案中出現過的語言版本：

```
patterns = [
  keyword_english,           # e.g., "FIX", "precondition"
  keyword_traditional_zh,    # e.g., "修復", "前置條件"
  keyword_simplified_zh,     # e.g., "修复", "前置条件"
  keyword_emoji_if_any,      # e.g., "🔧", "✅"
  keyword_abbreviation,      # e.g., "PRE", "POST", "INV"
]
```

2. 若專案使用其他語言（日文、韓文等），一併加入

## Step 3: 執行全域搜尋

1. 搜尋範圍 = 專案根目錄遞迴
2. 排除項僅限：`node_modules/`, `.git/`
3. 所有搜尋一律 **CaseInsensitive = true**
4. 對每個 pattern 分別執行搜尋

## Step 4: 人工過濾

1. 逐一判斷每個匹配是否為：
   - **(a) 合法用途**（如 CREATE/MODIFY/FIX 三選一列舉、定義性描述）→ 保留不動
   - **(b) 待處理的匹配**（實際需要修改/移除的）→ 標記
2. **禁止預先假設某些檔案「應該沒問題」而跳過**

## Step 5: 搜尋證據記錄

1. 記錄以下資訊（寫入當前回覆或 iteration-log）：
   - 使用的 patterns 列表
   - 每個 pattern 的匹配數
   - 排除的合法用途數
   - 最終需修正的匹配數
2. 此記錄作為微驗證的審計軌跡

---

## DbC

**前置條件**：已明確 target_concept；已通過 Step 0 適用性判定
**不變量**：搜尋必須 case-insensitive；搜尋範圍必須覆蓋專案根目錄全部檔案（排除項除外）
**後置條件**：所有 patterns 已搜尋；結果已記錄；合法用途已區分
