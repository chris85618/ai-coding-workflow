"""SonarCloud API Adapter.

Traceable to: FEA-015, FR-015
"""

from typing import Any

from sonarqube import SonarCloudClient

from agentic_workflow.domain.value_objects import SonarCloudConfig

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

        measures: list[dict[str, Any]] = component.get("component", {}).get("measures", [])

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

        issues: list[dict[str, Any]] = response.get("issues", []) if isinstance(response, dict) else list(response)

        if include_closed:
            return issues
        return [i for i in issues if i.get("status") not in CLOSED_STATUSES]

    def get_all_available_metrics(self) -> list[dict[str, Any]]:
        """Fetch all available metric definitions from SonarCloud.

        Returns:
            List of metric dictionaries containing keys like 'key', 'name', 'type', etc.

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        try:
            res = self.client.metrics.search_metrics()
            if isinstance(res, dict):
                metrics_list = res.get("metrics", [])
                if isinstance(metrics_list, list):
                    return [dict(m) for m in metrics_list if isinstance(m, dict)]
            elif isinstance(res, list):
                return [dict(m) for m in res if isinstance(m, dict)]
            return []
        except Exception as exc:
            raise RuntimeError(f"SonarCloud API error: {exc}") from exc

    def get_detailed_component_measures(self, metric_keys: list[str]) -> list[dict[str, Any]]:
        """Fetch detailed component measures for the given metric keys.

        Args:
            metric_keys: A list of metric keys to query.

        Returns:
            A list of measure dictionaries (each containing 'metric', 'value', etc.).

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        if not metric_keys:
            return []

        if not self.config.project_key:
            raise RuntimeError("SonarCloud API error: project_key configuration is missing")

        chunk_size = 50
        all_measures: list[dict[str, Any]] = []

        for i in range(0, len(metric_keys), chunk_size):
            chunk = metric_keys[i : i + chunk_size]
            try:
                component = self.client.measures.get_component_with_specified_measures(
                    component=self.config.project_key,
                    fields="metrics,periods",
                    metricKeys=",".join(chunk),
                )
            except Exception as exc:
                raise RuntimeError(f"SonarCloud API error: {exc}") from exc

            measures = component.get("component", {}).get("measures", [])
            all_measures.extend(measures)

        return all_measures

    def get_all_metrics_with_values(self) -> list[dict[str, Any]]:
        """Fetch all available metric definitions and their values for this project.

        Returns:
            List of dictionaries, each containing:
            - Metric metadata (key, name, description, domain, type, etc.)
            - Value details (global, periods, etc. under 'value')

        Raises:
            RuntimeError: If any SonarCloud API call fails.
        """
        metrics = self.get_all_available_metrics()
        metric_keys = [m["key"] for m in metrics if "key" in m]

        measures = self.get_detailed_component_measures(metric_keys)
        measures_map = {m["metric"]: m for m in measures if "metric" in m}

        result: list[dict[str, Any]] = []
        for m in metrics:
            key = m.get("key")
            if not key:
                continue

            detail = dict(m)
            measure = measures_map.get(key)
            if measure:
                detail["value"] = _coerce_value(measure.get("value"))
                if "bestValue" in measure:
                    detail["bestValue"] = measure["bestValue"]
            else:
                detail["value"] = None

            result.append(detail)

        return result
