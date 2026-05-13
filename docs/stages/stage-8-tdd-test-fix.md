# Stage 8：TDD 開發 → 執行自動化測試 → 調查修復

> **[雙 Agent 迭代]** 紅-綠-重構循環 + 自動化測試執行 + 失敗調查修復。
> 本 Stage 整合 SonarCloud 品質閘門作為必過門檻。

---

## 輸入

| 來源 | 內容 | ID 前綴 |
|------|------|---------|
| Stage 5 | 類別/聚合 | CLS-xxx |
| Stage 6 | 不變量/Contract | INV-xxx |
| Stage 7 | BDD 場景 | SC-xxx |
| Stage 7 | 測試結構 | — |

---

## 子步驟 8a：TDD 開發

### 審查維度（Agent α）

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| D1 | 紅-綠-重構紀律 | 是否先寫失敗測試，再寫最少程式碼通過？ |
| D2 | OOAD 一致性 | 實作是否忠實於 Stage 5 的類別圖？偏離處是否有理由？ |
| D3 | 演算法一致性 | 實作是否忠實於 Stage 4 的演算法規格？ |
| D4 | 防禦性程式設計 | 邊界檢查、null safety、error handling 是否系統性？ |
| D5 | 可測試性 | 是否有不可測試的程式碼？依賴注入是否到位？ |

### S2C 增強

- **元件測試**：每個 CLS-xxx 生成單元測試骨架 → TC-xxx，識別整合邊界，生成整合測試案例 → TC-xxx
- **基礎設施檢查**：實作前驗證環境配置、基礎設施需求、依賴版本，全部通過才開始

---

## 全程自動保障（ECC Hooks）

| Hook | 觸發時機 | 作用 |
|------|---------|------|
| `pre:bash:dispatcher` | 每次 Bash 執行前 | 品質/tmux/push 檢查 |
| `pre:edit-write:gateguard-fact-force` | 首次編輯某檔案 | 強制先調查再修改 |
| `pre:config-protection` | 編輯 linter 配置 | 阻止弱化配置 |
| `post:quality-gate` | 每次編輯後 | 品質門檻檢查 |
| `post:edit:design-quality-check` | 前端編輯後 | AI slop 偵測 |
| `post:edit:console-warn` | 編輯後 | console.log 警告 |
| `post:ecc-context-monitor` | 每次工具使用後 | Context/成本/範圍監控 |
| `stop:format-typecheck` | 回應結束 | 批次格式化 + 類型檢查 |
| `stop:check-console-log` | 回應結束 | console.log 掃描 |
| `stop:evaluate-session` | 回應結束 | 萃取可複用模式 |

gstack 持續 Checkpoint：

```bash
gstack-config set checkpoint_mode continuous   # 自動 WIP commit
```

Path B 專屬 — 增量更新知識圖譜：

```
/understand   # 大量修改後，增量更新知識圖譜
```

---

## 子步驟 8b：執行自動化測試

```bash
# 執行 Stage 7 寫的 BDD/ATDD 測試
# 執行 Stage 7 寫的 Property-based 測試
# 執行 TDD 單元測試
```

```
/qa https://your-staging-url.com     # gstack 瀏覽器 QA 測試
/qa-only https://your-staging-url.com # 僅報告不修復
/review                               # gstack 程式碼審查
/codex                                # 跨模型第二意見（可選）
/design-review                        # 設計審查（前端）
/devex-review                         # DX 審查（API/SDK）
```

---

## 子步驟 8c：SonarCloud 品質閘門

> 整合 SonarCloud 作為 Stage 8 強制品質門檻。

### 品質閘門門檻

| 維度 | 全局門檻 | 新程式碼門檻 |
|------|---------|------------|
| 覆蓋率 | ≥ 80% | ≥ 85% |
| 重複率 | ≤ 5% | ≤ 3% |
| 函式複雜度 | ≤ 15 | ≤ 15 |
| 認知複雜度 | ≤ 15 | ≤ 15 |
| 安全漏洞 (Critical/High) | 0 | 0 |
| Blocker/Critical Code Smells | 0 | 0 |
| Major Code Smells | ≤ 10 | ≤ 3 |
| 技術債比率 | ≤ 5% | ≤ 5% |
| 可靠性等級 | A | A |
| 可維護性等級 | A | A |

### SonarCloud 執行協議

```
1. 在所有測試通過後執行 SonarCloud 掃描
2. 品質閘門結果必須全部 PASS
3. 任何 FAIL → 自主修復 → 重新掃描
4. 自主修復 3 次仍 FAIL → 上報 HITL
5. 安全熱點審查率必須 100%
6. 所有 TODO/FIXME 必須轉為 DEBT-xxx 項目
```

### 新增 DEBT-xxx 來源

```
FROM sonarcloud_results:
  FOR each code_smell WHERE severity >= MAJOR:
    register_tech_debt(DEBT-xxx)
    link_to_source_file()
    calculate_rice_score()
  FOR each todo_comment:
    register_tech_debt(DEBT-xxx)
  → 寫入 docs/tech-debt-register.md
```

---

## 子步驟 8d：調查修復

測試失敗時，進入調查修復迴圈：

```
/investigate    # gstack 調查模式
```

- 自動凍結編輯範圍（`/freeze`），防止意外修改無關程式碼
- 鐵律：**先調查，再修復**
- 追蹤資料流、測試假設
- 3 次修復失敗後自動上報
- 修復後自動解凍（`/unfreeze`）
- 修復後回到子步驟 8b 重新執行測試

---

## 最終安全審計（Ship 前最後防線）

```bash
# Layer 1: 應用安全
/cso

# Layer 2: Agent 安全
npx ecc-agentshield scan --opus --stream

# Layer 3: 供應鏈安全
skillfortify scan . --format json --severity-threshold high
skillfortify lock . --output skill-lock.json
skillfortify sbom . --format cyclonedx
skillfortify dashboard --output security-report.html
```

---

## 迭代協議

```
┌──────────────────────────────────────────────┐
│  Step A: Agent α（破綻發掘者）               │
│  → 依 D1-D5 維度                             │
│  → 驗證實作與 Stage 4/5 設計一致性           │
│  → 產出：問題清單 + 方向建議                 │
├──────────────────────────────────────────────┤
│  Step B: Agent β（收斂整合者）               │
│  → 紅-綠-重構循環                            │
│  → 產出：通過測試的程式碼                    │
├──────────────────────────────────────────────┤
│  Step M: 微驗證迴圈                          │
│  → 觸發 skills/workflow-skills/micro-validation.md  │
│  → 觸發 skills/workflow-skills/impact-analysis-exec.md │
│  → TC-xxx 追溯至 SC-xxx/INV-xxx              │
│  → SonarCloud 品質閘門                       │
│  → 全數通過才進入 Step C                     │
├──────────────────────────────────────────────┤
│  Step C: 👤 HITL 迭代閘門                    │
│  → [1] 繼續迭代  [2] 加入新需求              │
│  → [3] 通過 ✅ → 最終安全審計 → 出口閘門    │
└──────────────────────────────────────────────┘
```

---

## 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 實作程式碼 | — | 專案目錄 |
| 單元測試 | `TC-xxx` | 測試目錄 |
| 整合測試 | `TC-xxx` | 測試目錄 |
| SonarCloud 報告 | — | `docs/sonarcloud-report.md` |
| 安全審計報告 | — | `docs/security-audit-stage8.md` |
| 技術債項目 | `DEBT-xxx` | `docs/tech-debt-register.md` |

---

## HITL 出口閘門

### 原有檢查
- [ ] 所有 TDD 單元測試通過
- [ ] 所有 BDD/ATDD 驗收測試通過
- [ ] 所有 Property-based 測試通過
- [ ] `/review` 程式碼審查通過
- [ ] `/qa` 瀏覽器 QA 通過（若有 UI）
- [ ] 三層安全審計全部 PASS
- [ ] SkillFortify 信任等級 ≥ COMMUNITY_VERIFIED

### SonarCloud 品質閘門
- [ ] 覆蓋率門檻通過
- [ ] 安全漏洞為零（Critical/High）
- [ ] Code Smells 在門檻內
- [ ] 技術債比率 ≤ 5%
- [ ] 安全熱點 100% 已審查
- [ ] TODO/FIXME 已轉為 DEBT-xxx

### 追溯矩陣驗證
- [ ] 所有 TC-xxx 可追溯至 SC-xxx 和/或 INV-xxx
- [ ] 正向追溯完整：BG → FEA → FR → UC → SC → TC（全鏈）
- [ ] 反向追溯完整：TC → SC → UC → FR → FEA → BG（全鏈）
- [ ] 零孤兒 ID（全專案範圍）
- [ ] 語意一致性通過（全專案範圍）
- [ ] 影響分析紀錄已完成
- [ ] 所有文件已寫入 `docs/`

### 完成檢查（觸發 `skills/workflow-skills/completion-check.md`）
- [ ] 每個 FR-xxx 至少有一個 TC-xxx 驗證
- [ ] 每個 UC-xxx 至少有一個 SC-xxx 涵蓋
- [ ] 每個 INV-xxx 至少有一個 TC-xxx 或 property test 驗證
- [ ] 追溯矩陣無斷裂鏈

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Phase 9
