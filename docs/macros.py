import os
import tomllib

# 安全黑名單：禁止透過巨集暴露的環境變數關鍵字
SECRET_KEYWORDS = ["KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH"]


def define_env(env):
    """Define variables, macros and filters for mkdocs-macros-plugin."""
    # Load pyproject.toml as the single source of truth
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            project_meta = pyproject.get("project", {})
            tool_mkdocs = pyproject.get("tool", {}).get("mkdocs", {})

            env.variables["project"] = project_meta
            env.variables["version"] = project_meta.get("version", "0.0.0")
            env.variables["project_name"] = project_meta.get("name", "unknown")
            env.variables["mkdocs_config"] = tool_mkdocs

    except Exception as e:
        env.variables["project_error"] = str(e)

    @env.macro
    def get_safe_env(var_name, default=""):
        """安全獲取環境變數，禁止讀取敏感資訊"""
        if any(keyword in var_name.upper() for keyword in SECRET_KEYWORDS):
            return "[REDACTED]"
        return os.environ.get(var_name, default)

    @env.macro
    def include_file(filename, start_line=1, end_line=None):
        """Include a file content in markdown."""
        try:
            with open(filename, encoding="utf-8") as f:
                lines = f.readlines()
                if end_line is None:
                    end_line = len(lines)
                return "".join(lines[start_line - 1 : end_line])
        except Exception as e:
            return f"Error including file: {e}"


def on_config(config):
    """Hook to modify mkdocs configuration dynamically from pyproject.toml [tool.mkdocs]."""
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            tool_mkdocs = pyproject.get("tool", {}).get("mkdocs", {})

            # Sync core fields
            if tool_mkdocs.get("site_name"):
                config["site_name"] = tool_mkdocs["site_name"]

            if tool_mkdocs.get("site_description"):
                config["site_description"] = tool_mkdocs["site_description"]

            # Sync navigation if present in pyproject.toml
            if tool_mkdocs.get("nav"):
                config["nav"] = tool_mkdocs["nav"]

    except Exception:
        pass
    return config
