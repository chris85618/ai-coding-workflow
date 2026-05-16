"""SonarCloud API Adapter.

Traceable to: FEA-015, FR-015
"""

from typing import Any

from sonarqube import SonarCloudClient

from agentic_workflow.frameworks.config import SonarCloudConfig

METRIC_KEYS = [
    "coverage",
    "duplicated_lines_density",
    "duplicated_blocks",
    "complexity",
    "cognitive_complexity",
    "vulnerabilities",
    "security_hotspots",
    "bugs",
    "code_smells",
    "sqale_debt_ratio",
    "reliability_rating",
    "ncloc",
    "alert_status",
]

KEY_MAP: dict[str, str] = {
    "complexity": "cyclomatic_complexity",
    "duplicated_lines_density": "duplication",
    "vulnerabilities": "security_vulnerabilities",
    "sqale_debt_ratio": "tech_debt_ratio",
    "bugs": "blocker_critical_smells",
    "code_smells": "major_smells",
}

CLOSED_STATUSES = {"CLOSED", "RESOLVED"}


def _coerce_value(raw: str | None) -> float | str | None:
    """Coerce a raw string value to float if numeric, else keep as str."""
    if raw is None:
        return None
    try:
        if raw.replace(".", "", 1).lstrip("-").isdigit():
            return float(raw)
    except (ValueError, AttributeError):
        pass
    return raw


class SonarCloudAdapter:
    """Adapter for interacting with SonarCloud Web API via python-sonarqube-api.

    Responsibilities:
    - Authenticate using SonarCloudClient (no raw requests).
    - Fetch project measures and transform keys to Domain vocabulary.
    - Fetch issues, filtering by open/closed status in Python.
    """

    def __init__(self, config: SonarCloudConfig) -> None:
        """Initialise the adapter with project configuration."""
        self.config = config
        self.client = SonarCloudClient(
            sonarqube_url="https://sonarcloud.io",
            token=config.token,
        )

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        """Fetch project measures and return them in Domain format.

        Returns:
            Dict mapping Domain metric names to scope-value dicts,
            e.g. ``{"coverage": {"global": 95.0}}``.

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        try:
            component = self.client.measures.get_component_with_specified_measures(
                component=self.config.project_key,
                fields="metrics,periods",
                metricKeys=",".join(METRIC_KEYS),
            )
        except Exception as exc:
            raise RuntimeError(f"SonarCloud API error: {exc}") from exc

        measures: list[dict[str, Any]] = component.get("component", {}).get(
            "measures", []
        )

        result: dict[str, dict[str, Any]] = {}
        for m in measures:
            api_key: str = m["metric"]
            domain_key = KEY_MAP.get(api_key, api_key)
            result[domain_key] = {"global": _coerce_value(m.get("value"))}

        return result

    def get_issues(self, include_closed: bool = False) -> list[dict[str, Any]]:
        """Fetch issues for the project.

        Args:
            include_closed: When True return all issues regardless of status.
                            Default False filters out CLOSED/RESOLVED issues.

        Returns:
            List of issue dicts as returned by the SonarCloud API.

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        try:
            response = self.client.issues.search_issues(
                componentKeys=self.config.project_key,
            )
        except Exception as exc:
            raise RuntimeError(f"SonarCloud API error: {exc}") from exc

        issues: list[dict[str, Any]] = (
            response.get("issues", []) if isinstance(response, dict) else list(response)
        )

        if include_closed:
            return issues
        return [i for i in issues if i.get("status") not in CLOSED_STATUSES]
