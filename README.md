# AI Coding Workflow — Agentic Pipeline

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=chris85618_ai-coding-workflow)](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)

一套基於 **LangGraph** 與 **Clean Architecture** 的自動化代理編程工作流系統。本專案將複雜的開發協議具象化為可執行的導向無環圖 (DAG)，實現 100% 追溯與治理。

---

## 🚀 快速上手 (Quick Start)

### 1. 複製專案 (Clone)

本專案包含關鍵的子模組與治理協議，請務必使用遞迴複製：

```bash
git clone --recursive https://github.com/chris85618/ai-coding-workflow.git
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

建立 `.env` 檔案並填入您的 Key：

```dotenv
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
SONAR_TOKEN=your_sonar_token
```

---

## 🛠️ 開發流程 (Development Workflow)

### 第一次開發：修改與提交

本專案實施 **SSOT (唯一事實來源)** 治理。若需修改 SonarCloud 或 MkDocs 配置，請遵循以下流程：

1.  **修改 `pyproject.toml`**：在 `[tool.sonar]` 或 `[tool.mkdocs]` 區段進行調整。
2.  **自動同步**：當您執行 `git commit` 時，`pre-commit` 鉤子會自動執行 `scripts/sync_sonar_props.py`，更新 `sonar-project.properties`。
3.  **治理記錄**：若涉及架構決策，請建立新的 ADR 並更新 `docs/traceability-matrix.md`。

### 執行測試與驗證

```bash
# 執行全套測試 (100% 覆蓋率要求)
pytest

# 靜態分析與格式化
ruff check .
mypy src
```

---

## 📖 核心文檔 (Documentation)

| 文檔 | 用途 |
| :--- | :--- |
| [AGENTS.md](./AGENTS.md) | **執行憲法**：AI 代理必須嚴格遵守的 Step 0-12 執行協議。 |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | **架構深潛**：LangGraph 拓樸、狀態機設計與子圖邏輯。 |
| [Traceability Matrix](./docs/traceability-matrix.md) | **追溯矩陣**：所有需求 (FR) 與實作 (TC) 的對應關係。 |
| [ADR Index](./docs/adr/index.md) | **決策紀錄**：專案所有架構決定 (ADR) 的歷史存檔。 |

---

## 📡 監控與品質

- **SonarCloud**: [專案儀表板](https://sonarcloud.io/summary/new_code?id=chris85618_ai-coding-workflow)
- **MkDocs**: 執行 `mkdocs serve` 即可在本地預覽完整治理文件。

---

## ⚖️ 治理原則

1.  **OO Mandate (ALG-010)**：所有演算法必須以類別 (Class) 實作，禁止模組級函數。
2.  **Zero Warning (ADR-GOV-026)**：禁止提交帶有任何 Linter 警告或測試失敗的程式碼。
3.  **Traceability (ADR-GOV-008)**：每一行代碼都必須能回溯至對應的 FR/UC。
