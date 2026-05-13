# ADR-GOV-023: Skill 追溯性擴充 + RCA 推論平準化

> **狀態**: Accepted
> **日期**: 2026-05-14
> **類別**: GOVERNANCE
> **決策者**: HITL
> **追溯**: FR-004, FR-005, FR-007, FR-022, FR-023

---

## 背景

- **觸發 Stage/Phase**: Stage 3（追溯缺口修補）
- **觸發事件**: 追溯矩陣止步於 ID 層級（BG→FEA→FR→UC→SC→TC），未延伸到實際實作的 Skill 檔案；root-cause-leftshift.md 的瓶頸定位依賴直覺而非系統推論
- **前置條件**: ADR-GOV-022 完成 docs/→skills/ 執行邏輯吸收；traceability-system.md 已定義 guards 連結類型但未定義 implemented-by/modified-by
- **約束**: 追溯矩陣必須覆蓋從需求到實作的完整鏈路

## 決策

1. **追溯系統擴充**: traceability-system.md 新增 `implemented-by`（FR→Skill）和 `modified-by`（ADR→Skill）連結類型
2. **追溯矩陣擴充**: 新增三個段落 — FR→Skill (25 條)、LESSON→Skill (20 條)、ADR→Skill (15 條)
3. **RCA 推論平準化**: root-cause-leftshift.md Step 3 拆為 3a(因果鏈建構)→3b(瓶頸識別/TOC)→3c(追溯矩陣交叉驗證)
4. **Step 1.5 改查追溯矩陣**: 從直接掃描 docs/adr/ 改為查追溯矩陣的 LESSON→Skill 段落
5. **ADR 範本更新**: LESSON 格式新增「瓶頸識別」欄位（問題發生點/逃逸路徑/最早可偵測點/瓶頸位置/介入類型/預期覆蓋）
6. **既有 ADR backfill**: 14 個 ADR 中 20 個 LESSON 全部補做瓶頸識別

## 理由

- **支持證據**: 追溯矩陣 137 ID 全部止步於文件 ID 層級，無法追溯至具體 Skill 實作檔案；RCA 瓶頸定位無標準化流程
- **權衡取捨**: 追溯矩陣複雜度增加（137→197 條），但實現需求→實作的完整追溯
- **風險接受**: 無

## 替代方案

| 方案 | 優點 | 缺點 | 拒絕理由 |
|------|------|------|----------|
| 僅在 LESSON 欄位記錄 Skill | 分散式，無額外文件 | 無法集中查詢 | 追溯效率低 |
| 建立獨立 Skill Registry 檔案 | 集中管理 | 額外維護成本 | 追溯矩陣已有此能力 |

## 後果

**正面**：需求→Skill 完整追溯；RCA 瓶頸定位標準化；LESSON 重用改查追溯矩陣
**負面**：追溯矩陣維護成本增加

## 影響分析

- **爆炸半徑**: 19 檔案（4 skill + 1 template + 14 ADR backfill）
- **嚴重度**: MAJOR
- **受影響 ID**: FR-004, FR-005, FR-007, FR-022, FR-023

## 流程變更

- **修改前規則**: 追溯矩陣止步於 ID 層級；RCA Step 3 為直覺式定位；Step 1.5 直接掃描 docs/adr/
- **修改後規則**: 追溯矩陣延伸至 Skill 檔案；RCA Step 3a/3b/3c 系統思考推論；Step 1.5 查追溯矩陣
- **影響範圍**: 全切面

## 變更紀錄 (Implementation Records)

### 變更 #1: 追溯基礎建設 + RCA 平準化 + ADR backfill

- **日期**: 2026-05-14T06:00+08:00
- **類型**: MODIFY (19 files)
- **嚴重度**: MAJOR
- **微驗證**: PASS

**P1 追溯基礎 (2 files)**:

| 檔案 | 變更 |
|------|------|
| traceability-system.md | +implemented-by, +modified-by 連結類型, +Skill 追溯出口閘門 |
| traceability-matrix.md | +FR→Skill (25), +LESSON→Skill (20), +ADR→Skill (15), 覆蓋統計 137→197 |

**P2 RCA 平準化 (3 files)**:

| 檔案 | 變更 |
|------|------|
| root-cause-leftshift.md | Step 3→3a/3b/3c, Step 1.5 改查追溯矩陣, LESSON 格式+瓶頸識別 |
| adr-governance.md | Step 6 +瓶頸識別要求, +Skill 追溯登記要求 |
| ADR-TEMPLATE.md | LESSON 格式+瓶頸識別欄位 |

**P3 ADR backfill (14 files, 20 LESSSONs)**:

| ADR | LESSON IDs |
|-----|-----------|
| ADR-GOV-003 | LESSON-001, LESSON-004 |
| ADR-GOV-004 | LESSON-002 |
| ADR-GOV-005 | LESSON-003 |
| ADR-GOV-006 | LESSON-005 |
| ADR-GOV-007 | LESSON-006 |
| ADR-GOV-008 | LESSON-007, LESSON-013 |
| ADR-GOV-009 | LESSON-008 |
| ADR-GOV-010 | LESSON-009 |
| ADR-GOV-011 | LESSON-010 |
| ADR-GOV-012 | LESSON-011 |
| ADR-GOV-013 | LESSON-012 |
| ADR-GOV-016 | LESSON-014 |
| ADR-GOV-020 | LESSON-020 |
| ADR-GOV-022 | LESSON-022~026 |

## 關聯產出物

| 類型 | ID | 說明 |
|------|----|------|
| 追溯擴充 | FR→Skill 25 條 | 需求到 Skill 實作映射 |
| 追溯擴充 | LESSON→Skill 20 條 | 教訓到 Skill 守衛映射 |
| 追溯擴充 | ADR→Skill 15 條 | 決策到 Skill 修改映射 |
