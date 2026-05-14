# Skill: 三層安全審計執行

> **觸發條件**：Stage 5 出口前、Stage 8 最終審計
> **輸入**：當前程式碼和設計產出物
> **輸出**：安全審計報告（三層全 PASS 才放行）

---

## Step 1: Layer 1 — 應用安全

1. 執行 `/cso` (gstack)
2. OWASP Top 10 逐項檢查
3. STRIDE 威脅建模
4. 產出：應用安全報告

## Step 2: Layer 2 — Agent 安全

1. 執行 `npx ecc-agentshield scan --opus --stream`
2. 紅藍隊 AI 審計
3. 提示注入防護驗證
4. 產出：Agent 安全報告

## Step 3: Layer 3 — 供應鏈安全

1. 執行 `skillfortify scan . --format json`
2. 執行 `skillfortify sbom . --format cyclonedx`
3. 執行 `skillfortify lock . --output skill-lock.json`
4. 執行 `skillfortify trust <module>`
5. 產出：供應鏈安全報告 + ASBOM + Lockfile

## Step 4: 判定

- 三層全 PASS → 放行
- 任一層有 HIGH+ 發現 → 回到設計/實作修改 → 重新審計
- CRITICAL 發現 → 阻塞，上報 HITL

## Step 5: 風險/技術債登錄（強制）

> 審計發現 HIGH+ 項目時，必須同步登錄：

1. **安全風險 → RISK-xxx**：
   - 每個 HIGH+ 安全發現 → 呼叫 `skills/workflow-skills/risk-management.md` Step 1-5
   - 類別固定為 `SECURITY`
   - 依 STRIDE 分類映射機率/影響

2. **安全債 → DEBT-xxx**：
   - 已知但暫未修復的安全問題 → 呼叫 `skills/workflow-skills/tech-debt-collect.md` Step 1-5
   - 來源固定為 `安全債`
   - P0 = CRITICAL 安全發現（不受容量限制）

3. 更新 `{target_repo}/docs/risk-register.md` 和 `{target_repo}/docs/tech-debt-register.md`
4. 更新追溯矩陣 RISK→FEA、DEBT→FR 節

