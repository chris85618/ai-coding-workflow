# Skill: 三層安全審計執行

> **觸發條件**：Stage 5 出口前、Stage 8 最終審計
> **輸入**：當前程式碼和設計產出物
> **輸出**：安全審計報告（三層全 PASS 才放行）

---

## 執行協議

```
Layer 1: 應用安全
→ /cso (gstack)
→ OWASP Top 10 逐項檢查
→ STRIDE 威脅建模
→ 產出：應用安全報告

Layer 2: Agent 安全
→ npx ecc-agentshield scan --opus --stream
→ 紅藍隊 AI 審計
→ 提示注入防護驗證
→ 產出：Agent 安全報告

Layer 3: 供應鏈安全
→ skillfortify scan . --format json
→ skillfortify sbom . --format cyclonedx
→ skillfortify lock . --output skill-lock.json
→ skillfortify trust <module>
→ 產出：供應鏈安全報告 + ASBOM + Lockfile
```

## 判定規則

```
三層全 PASS → 放行
任一層有 HIGH+ 發現 → 回到設計/實作修改 → 重新審計
CRITICAL 發現 → 阻塞，上報 HITL
```
