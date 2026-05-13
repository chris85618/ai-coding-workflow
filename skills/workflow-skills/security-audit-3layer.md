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
