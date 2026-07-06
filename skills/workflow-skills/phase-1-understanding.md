# Skill: Phase 1 程式碼理解編排

> **觸發條件**：AGENTS.md Step 2（Path B 專用）
> **輸入**：專案目錄（含既有原始碼）
> **輸出**：知識圖譜、架構理解、元件關係
> **前提**：Phase 0 判定為 Path B

---

## Step 1: 核心分析

```
/understand                    # 生成知識圖譜
```

建立程式碼基座理解：
- 目錄結構分析
- 進入點識別
- 依賴關係圖
- 模組邊界識別

## Step 2: 視覺化

```
/understand-dashboard          # 互動式知識圖譜
```

## Step 3: 深入探究（按需）

```
/understand-explain <path>     # 特定元件深入
/understand-chat <question>    # 問答式理解
```

## Step 3.5: 領域知識萃取

```
/understand-domain             # 從知識圖譜衍生業務領域流程圖（低成本）
```

- 產出領域/業務流程/流程步驟，作為 Phase 2 專案分析與 Stage 5 DDD 領域建模（`s2c-domain-model.md`）的輸入
- 知識圖譜已存在時直接衍生，不重新掃描

## Step 4: 差異分析（若恢復 Session）

```
/understand-diff               # Git diff 影響分析
```

## Step 5: 輸出確認

- [ ] 知識圖譜已生成
- [ ] 架構理解文件已產出
- [ ] 關鍵元件關係已識別
- [ ] 領域流程圖已產出（供 Phase 2 / Stage 5 使用）
- [ ] 進入 Phase 2（專案分析）
