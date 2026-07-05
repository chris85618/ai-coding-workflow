# ADR-STR-028: Design-by-Contract 庫由 icontract 遷移至 deal

## 狀態
Accepted (2026-07-06)

## 背景
既有 DbC 生態基於 icontract 四件套：`icontract`（runtime 合約）、`pyicontract-lint`（靜態 lint）、`icontract-hypothesis`（合約驅動模糊測試）、`sphinx-icontract`（文件渲染）。此生態存在多項維護風險：

- `pyicontract-lint` pin `astroid<3`，無法解析 Python 3.14 原始碼，需在 pyproject 中覆寫 stale pin 並全域忽略 astroid DeprecationWarning。
- `icontract-hypothesis` 1.1.7 hook 了 hypothesis 6.137 已移除的內部 API，被迫 pin `hypothesis<6.137`。
- icontract 的 `OLD` 保留字需要 ruff `pep8-naming` 的 `extend-ignore-names` 白名單特例。
- 四個套件分屬不同維護者，供應鏈面積大且更新停滯。

kanban 決策（TODO: 使用 deal 取代 icontract）指向 `deal`：單一套件覆蓋 runtime 合約、`deal lint`（靜態檢查）、`deal.cases`（hypothesis 模糊測試）、`deal.autodoc`（Sphinx 渲染），且 CrossHair 原生支援 `--analysis_kind deal`（Z3 SMT 符號執行）。

## 決策

1. **runtime 合約**：`icontract.require/ensure/invariant` → `deal.pre/ensure(post)/inv`。`deal` 加入 `ALLOWED_INNER_DEPENDENCIES` 白名單，`icontract` 移除。
2. **快照語義重設計**：deal 無 `OLD` snapshot。原 snapshot 合約重寫為：
   - `Stage.transition`：`deal.ensure`（後置狀態 = 請求狀態）+ `deal.raises(ValueError)` + `deal.reason`（迴歸轉換必為 ValueError 之因）— 比原合約更精確。
   - `Pipeline.advance`：後置條件改為「前一 slot 的 stage 必為 PASSED」，以建構保證取代 OLD 比較，語義等價於 INV-001 單調前進。
3. **不變量左移**：`deal.inv` 在每次屬性賦值即驗證（icontract 僅在 public method 呼叫後驗證）。`Pipeline.stages` 改用 `_default_stages` factory 直接生成完整映射，徹底消除「空 stages 過渡態」，INV-016 於任何可觀察時刻皆成立。
4. **驗證工具鏈**：
   - TC-CONTRACT-001: `pyicontract-lint` → `python -m deal lint src`
   - TC-CONTRACT-002/003: `icontract-hypothesis.infer_strategy` → `deal.cases`（classmethod 以 `kwargs={"cls": ...}` 固定）
   - TC-CONTRACT-004: `crosshair --analysis_kind icontract` → `--analysis_kind deal`
   - 文件渲染: `sphinx_icontract` extension → `docs/conf.py` 中 `setup(app)` 掛載 `deal.autodoc(app)`
5. **依賴清理**：移除 `icontract`、`sphinx-icontract`、`pyicontract-lint`、`icontract-hypothesis`、astroid pin 覆寫、hypothesis 上限 pin、ruff `OLD` 白名單、astroid filterwarnings。新增 `deal>=4.24.6`。

## 後果

### 正面
- 供應鏈由 4 套件收斂為 1，hypothesis/astroid 全數解除 pin。
- 合約違規例外階層更精確（`PreContractError`/`PostContractError`/`InvContractError`，皆為 `AssertionError` 子類）。
- `deal.reason` 讓「例外之因」成為可驗證合約（icontract 無此能力）。
- INV-016/INV-004 不變量強制左移至 setattr 時點，測試由「呼叫方法後才爆」改為「損毀當下即拒絕」。
- 為 TODO「Contract Coverage 檢查」「模糊測試導入」「Z3 形式化驗證」鋪平единая基座。

### 負面 / 風險
- `deal.inv` 包裝類別名帶 `Invarianted` 後綴（repr 可見），依 repr 斷言的測試需注意。
- deal 無 OLD 快照，後續若需真正 pre-state 比較合約，須以領域事件或回傳值設計繞行。

## 追溯
- 上游: kanban TODO「使用deal取代icontract」、DEBT 供應鏈風險
- 下游: TC-CONTRACT-001~004、INV-001..024、tests/test_contracts.py、docs/formal-verification-spec.md v4
- 取代: ADR-STR-026 中 `icontract` 白名單項（其餘內容仍有效）
