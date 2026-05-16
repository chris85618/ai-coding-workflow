# ADR-STR-015: 導入 pyproject-mkdocs-plugin 實施單一事實來源

## 狀態
Accepted

## 背景
目前專案的元資料（名稱、版本、描述）分別存在於  `pyproject.toml` 與 `mkdocs.yml`。這導致版本更新或描述修改時需要維護兩個地方，增加了不一致的風險。

## 決策
導入 `pyproject-mkdocs-plugin` 套件，並在 `mkdocs.yml` 中啟用該插件。

## 後果
- **優點**: 
    - `site_name` 與 `site_description` 自動從 `pyproject.toml` 讀取。
    - 降低版本漂移風險。
- **缺點**: 
    - 增加一個開發依賴項。

## 追溯
- **FR**: FR-043
- **FEA**: FEA-016
