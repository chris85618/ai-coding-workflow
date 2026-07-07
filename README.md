# AI Coding Workflow — Agentic Pipeline

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=chris85618_ai-coding-workflow&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)
[![Build & Analyze](https://github.com/chris85618/ai-coding-workflow/actions/workflows/build.yml/badge.svg)](https://github.com/chris85618/ai-coding-workflow/actions/workflows/build.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=chris85618_ai-coding-workflow&metric=coverage)](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=chris85618_ai-coding-workflow&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=chris85618_ai-coding-workflow&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)
[![Dependabot](https://img.shields.io/badge/dependabot-enabled-blue.svg?logo=dependabot)](https://github.com/chris85618/ai-coding-workflow/network/updates)

一套基於 **LangGraph** 與 **Clean Architecture / DDD** 的自動化代理編程工作流系統。將統一工作流 12-Step 協議具象化為可執行的導向無環圖 (DAG)，實現 100% 追溯與治理：1169 個測試、100.00% statement 與 branch 覆蓋率、Design-by-Contract（deal）、TLA+/Z3/Coq 形式化驗證閘門。

---

## 🚀 快速上手 (Quick Start)

### 1. 複製專案 (Clone)

```bash
git clone https://github.com/chris85618/ai-coding-workflow.git
cd ai-coding-workflow
```

### 2. 環境建置 (Environment)

建議使用 Python 3.12+ 虛擬環境：

```bash
# 安裝依賴 (包含開發工具)
pip install -e ".[dev]"

# 安裝 Git 自動化鉤子 (必做！)
# 這會確保每次 commit 前自動從 pyproject.toml 同步配置，消除人為錯誤
python scripts/install_hooks.py
```

### 3. 配置 API Key

建立 `.env` 檔案並填入您的 Key（範本見 `.env.example`；`config.yaml` 僅引用環境變數，絕不直接存放 Key）：

```dotenv
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
SONAR_TOKEN=your_sonar_token
```

自定義 Endpoint（如 OpenRouter）可透過 `config.yaml` 各模型的 `base_url` 欄位注入。

### 4. 執行自舉管線 (Self-Bootstrap)

以真實 adapters 端對端執行 master graph（無 API key 時自動降級為 `OfflineReasoner`）：

```bash
python scripts/self_bootstrap.py
```

> ⚠️ rollback 預設為唯讀防護（`ReadOnlyVersionControl`）；`--allow-rollback` 會啟用 `git reset --hard`，請只在隔離副本中使用。

---

## 🧩 選用整合 (Optional Integrations)

兩個外部加速器皆為**選裝**；未安裝時管線自動走純 Python 降級路徑（ADR-GOV-017），`config.yaml` 無需任何額外配置。

### DSPy — Prompt 最佳化 (ADR-STR-031)

```bash
pip install -e ".[dspy]"
```

- 安裝後 `DSPyPromptOptimizer` 經 `importlib` 自動偵測 dspy，few-shot 範例改經 `dspy.Example` 正規化。
- 未安裝時自動降級為純 Python 的 `FewShotPromptOptimizer`（行為等價，無需改任何設定）。
- α/β 節點的 prompt 統一經 optimizer 注入（掛載點：`metadata.prompt_examples`）。

### Archon — 外部 Agent 編排 (ADR-STR-030)

```bash
curl -fsSL https://archon.diy/install | bash
```

- `ArchonOrchestrator` 會將管線匯出為 `.archon/agentic-workflow.yaml`（已列入 `.gitignore`）並以 `archon run` 派發。
- 未安裝 archon CLI 時 `dispatch()` 回傳 `False` 優雅降級，LangGraph 主管線不受影響。
- 引擎無關化設計：工作流語意以 domain 的 `Pipeline` aggregate 為單一事實來源，Archon 僅為派發通道。

---

## 🛠️ 開發流程 (Development Workflow)

### 修改與提交

本專案以 `pyproject.toml` 為 **SSOT (唯一事實來源)**：ruff、mypy、pytest、coverage、SonarCloud、Sphinx 的配置集中於此。

1.  **修改 `pyproject.toml`**：在對應 `[tool.*]` 區段調整。
2.  **自動同步**：`git commit` 時 `pre-commit` 鉤子自動執行 `scripts/sync_sonar_props.py`，更新 `sonar-project.properties`。
3.  **治理記錄**：涉及架構決策時，建立新的 ADR 並更新 `docs/traceability-matrix.md`。

### 執行測試與驗證

```bash
# 全套測試（100% statement + branch 覆蓋率閘門、合約覆蓋率、模糊測試、形式化結構閘門）
pytest

# 靜態分析與格式化
ruff check src tests scripts
mypy src tests --ignore-missing-imports --explicit-package-bases

# Clean Architecture 邊界掃描（CI 外亦可手動執行）
python scripts/clean_architecture_scan.py
```

### 建置 API 文件 (Sphinx)

`docs/_autosummary/` 不納入版本控制（`.gitignore`），需在本機由 Sphinx 自動產生：

```bash
sphinx-build docs/ docs/_build/html
```

建置完成後，以瀏覽器開啟 `docs/_build/html/index.html` 即可檢視。CI 目前不建置文件，若需在 CI 發布，需在 workflow 補上此步驟。

---

## 📂 工具腳本 (Scripts)

| 腳本 | 用途 |
| :--- | :--- |
| `scripts/self_bootstrap.py` | 自舉組合根：真實 adapters 端對端執行 master graph |
| `scripts/clean_architecture_scan.py` | Clean Architecture 邊界違規掃描 (CLI) |
| `scripts/install_hooks.py` | 安裝 Git pre-commit 鉤子 |
| `scripts/sync_sonar_props.py` | 由 pyproject.toml 生成 sonar-project.properties |
| `scripts/fetch_sonar_metrics_detail.py` | 拉取 SonarCloud 全指標明細 (Markdown) |
| `scripts/fetch_sonar_issues.py` | 拉取 SonarCloud 既有 issues |

---

## 📖 核心文檔 (Documentation)

| 文檔 | 用途 |
| :--- | :--- |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | **架構深潛**：LangGraph 拓樸、狀態機設計與子圖邏輯。 |
| [Traceability Matrix](./docs/traceability-matrix.md) | **追溯矩陣**：所有需求 (FR) 與實作 (TC) 的對應關係。 |
| [ADR Index](./docs/adr/index.md) | **決策紀錄**：專案所有架構決定 (ADR) 的歷史存檔。 |
| [Workflow State](./docs/workflow-state.md) | **管線狀態**：當前 Pipeline Position 與 WBS。 |
| [docs/formal/](./docs/formal/) | **形式化規格**：TLA+ 狀態機與 Coq 定理（tests/formal/ 閘門驗證）。 |

> 統一工作流 12-Step 協議的正本由框架 repo（`$FRAMEWORK_ROOT`）維護；本 repo 為其可執行實作（ADR-STR-032）。

---

## 📡 監控與品質

- **SonarCloud**: [專案儀表板](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)

---

## ⚖️ 治理原則

1.  **OO Mandate (ALG-010)**：所有演算法必須以類別 (Class) 實作，禁止模組級函數。
2.  **Zero Warning (ADR-GOV-026)**：禁止提交帶有任何 Linter 警告或測試失敗的程式碼。
3.  **Traceability (ADR-GOV-008)**：每一行代碼都必須能回溯至對應的 FR/UC。
4.  **Boundary Hardening (ADR-STR-025/027)**：AST 掃描強制四層依賴方向；內三層禁 `# type:`/`# pragma:`。
5.  **Design by Contract (ADR-STR-028)**：domain 具體公開方法 100% 攜帶 deal 合約，模糊測試驅動驗證。
