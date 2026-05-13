# Skill: S2C 需求分解

> **觸發條件**：Stage 3（技術規劃）
> **輸入**：FEA-xxx（In-Scope）
> **輸出**：FR-xxx, NFR-xxx, UC-xxx → `docs/requirements.md`, `docs/use-cases.md`

---

## Step 1: 功能需求分解

1. FOR each FEA-xxx IN in_scope → decompose → FR-xxx
2. FR TYPE: FUNCTIONAL | INTERFACE | DATA | SECURITY | PERFORMANCE
3. FR FORMAT: "系統必須 [動詞] [受詞]，以 [目的]"

## Step 2: 非功能需求萃取

1. FOR each FEA-xxx → extract_nfr → NFR-xxx
2. NFR TYPES: PERFORMANCE | SECURITY | SCALABILITY | RELIABILITY | USABILITY

## Step 3: 使用案例識別

1. FOR each FEA-xxx → identify_use_cases → UC-xxx
2. UC FORMAT: "作為 [角色]，我想 [動作]，以便 [目的]"

## Step 4: 使用案例 DbC 定義

1. FOR each UC-xxx → define_preconditions()（系統狀態要求）
2. FOR each UC-xxx → define_invariants()（執行期間必須恆真的命題；引用相關 INV-xxx）
3. FOR each UC-xxx → define_postconditions()（成功/失敗後系統狀態）
4. FOR each UC-xxx → define_main_flow() + define_alternative_flows() + define_exception_flows()

## Step 5: 風險評估

1. FOR each UC-xxx → risk_score = impact × probability (1-5 × 1-5 = 1-25)
2. IF risk_score >= 15 → classify_as_critical()
3. enumerate_edge_cases() + identify_failure_modes()

## Step 6: 產出

1. 寫入 `docs/requirements.md` + `docs/use-cases.md`
2. 更新追溯矩陣

## Step 7: PGVG 驗證

1. **2a 格式驗證**：所有 FR-xxx 格式符合 "系統必須 [動詞]..."；所有 NFR-xxx 有明確度量標準；所有 UC-xxx 有完整 5 個組成部分
2. **2b 覆蓋斷言**：每個 in_scope FEA-xxx 至少有 1 個 FR-xxx 和 1 個 UC-xxx；verify count(FR-xxx) >= count(FEA-xxx)
3. **2c 計數驗證**（grep 實際計數，非自我報告）：fr_count = grep "^| FR-" docs/requirements.md | wc -l；uc_count = grep "^| UC-" docs/use-cases.md | wc -l；ASSERT fr_count >= fea_count AND uc_count >= fea_count
4. **2d 語意驗證**：FOR each FR-xxx → verify 可測試性；FOR each NFR-xxx → verify 有量化標準
5. **2e 追溯驗證**：FOR each FR-xxx → verify link_to(FEA-xxx) exists；FOR each UC-xxx → verify link_to(FEA-xxx) AND link_to(FR-xxx) exists

> **LESSON-001**：計數必須用 grep 實際驗算，禁止 LLM 自我報告。
