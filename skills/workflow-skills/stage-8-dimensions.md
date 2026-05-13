# Skill: Stage 8 審查維度 + TDD + 品質閘門

> **觸發條件**：Stage 8（TDD + 測試 + 修復）迭代迴圈中
> **輸入**：CLS-xxx (Stage 5), INV-xxx (Stage 6), SC-xxx (Stage 7), 測試結構
> **輸出**：TC-xxx, 實作程式碼, DEBT-xxx → `{target_repo}/`
> **依賴 skill**：`iter-loop.md`、`sonarcloud-gate.md`、`security-audit-3layer.md`、`tech-debt-collect.md`

---

## Step 1: 審查維度表（Agent α）— 5 維

| 代號 | 維度 | 核心問題 |
|------|------|---------|
| D1 | 紅-綠-重構紀律 | 是否先寫失敗測試，再寫最少程式碼通過？ |
| D2 | OOAD 一致性 | 實作是否忠實於 Stage 5 的類別圖？偏離處是否有理由？ |
| D3 | 演算法一致性 | 實作是否忠實於 Stage 4 的演算法規格？ |
| D4 | 防禦性程式設計 | 邊界檢查、null safety、error handling 是否系統性？ |
| D5 | 可測試性 | 是否有不可測試的程式碼？依賴注入是否到位？ |

## Step 2: S2C 增強

- **元件測試**：每個 CLS-xxx 生成單元測試骨架 → TC-xxx
- **整合邊界**：識別整合邊界，生成整合測試案例 → TC-xxx
- **基礎設施檢查**：實作前驗證環境配置、依賴版本，全部通過才開始

## Step 3: ECC Hooks（全程自動保障）

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

gstack 持續 Checkpoint：`gstack-config set checkpoint_mode continuous`

Path B 專屬：大量修改後 `/understand` 增量更新知識圖譜。

## Step 4: 子步驟 8b — 執行自動化測試

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

## Step 5: 子步驟 8c — SonarCloud 品質閘門

觸發 `skills/workflow-skills/sonarcloud-gate.md`。

## Step 6: 子步驟 8d — 調查修復迴圈

測試失敗時：

```
/investigate    # gstack 調查模式
```

- 自動凍結編輯範圍（`/freeze`），防止意外修改無關程式碼
- 鐵律：**先調查，再修復**
- 追蹤資料流、測試假設
- 3 次修復失敗後自動上報
- 修復後自動解凍（`/unfreeze`）
- 修復後回到 Step 4 重新執行測試

## Step 7: 最終安全審計

觸發 `skills/workflow-skills/security-audit-3layer.md`（Ship 前最後防線）。

## Step 8: 產出物

| 產出 | ID 前綴 | 寫入位置 |
|------|---------|---------|
| 實作程式碼 | — | 專案目錄 |
| 單元測試 | `TC-xxx` | 測試目錄 |
| 整合測試 | `TC-xxx` | 測試目錄 |
| SonarCloud 報告 | — | `docs/sonarcloud-report.md` |
| 安全審計報告 | — | `docs/security-audit-stage8.md` |
| 技術債項目 | `DEBT-xxx` | `docs/tech-debt-register.md` |

## Step 9: HITL 出口閘門

### 原有檢查
- [ ] 所有 TDD 單元測試通過
- [ ] 所有 BDD/ATDD 驗收測試通過
- [ ] 所有 Property-based 測試通過
- [ ] `/review` 程式碼審查通過
- [ ] `/qa` 瀏覽器 QA 通過（若有 UI）
- [ ] 三層安全審計全部 PASS

### SonarCloud 品質閘門
- [ ] 覆蓋率門檻通過
- [ ] 安全漏洞為零（Critical/High）
- [ ] Code Smells 在門檻內
- [ ] 技術債比率 ≤ 5%
- [ ] TODO/FIXME 已轉為 DEBT-xxx

### 追溯矩陣驗證
- [ ] 所有 TC-xxx 可追溯至 SC-xxx 和/或 INV-xxx
- [ ] 正向追溯完整：BG → FEA → FR → UC → SC → TC（全鏈）
- [ ] 反向追溯完整：TC → SC → UC → FR → FEA → BG（全鏈）
- [ ] 零孤兒 ID（全專案範圍）

### 完成檢查
觸發 `skills/workflow-skills/completion-check.md`。

### 使用者確認
- [ ] 使用者確認 ✅ → 進入 Phase 9
