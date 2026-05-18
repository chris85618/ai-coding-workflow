"""SonarCloud API Adapter.

Traceable to: FEA-015, FR-015
"""

from typing import Any

from agentic_workflow.application.ports.gateways import QualityGateway
from agentic_workflow.domain.value_objects import SonarCloudConfig
from sonarqube import SonarCloudClient

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


def _parse_float(raw: str) -> float | str:
    is_num = raw.replace(".", "", 1).lstrip("-").isdigit()
    return float(raw) if is_num else raw


def _coerce_value(raw: Any) -> float | str | None:
    """Coerce a raw string value to float if numeric, else keep as str."""
    is_str = isinstance(raw, str)
    return _parse_float(raw) if is_str else raw


def _fetch_issues(client: Any, project_key: str) -> Any:
    try:
        return client.issues.search_issues(componentKeys=project_key)
    except Exception as exc:
        raise RuntimeError(f"SonarCloud API error: {exc}") from exc


def _fetch_metrics(client: Any) -> Any:
    try:
        return client.metrics.search_metrics()
    except Exception as exc:
        raise RuntimeError(f"SonarCloud API error: {exc}") from exc


def _parse_metrics(res: Any) -> list[dict[str, Any]]:
    raw = res.get("metrics", []) if isinstance(res, dict) else res
    items = raw if isinstance(raw, list) else []
    return [dict(m) for m in items if isinstance(m, dict)]


def _validate_project_key(key: str | None) -> None:
    if not key:
        raise RuntimeError("SonarCloud API error: project_key configuration is missing")


def _fetch_chunk_measures(client: Any, project_key: str, chunk: list[str]) -> list[dict[str, Any]]:
    try:
        kw = {"component": project_key, "fields": "metrics,periods", "metricKeys": ",".join(chunk)}
        comp = client.measures.get_component_with_specified_measures(**kw)
        return list(comp.get("component", {}).get("measures", []))
    except Exception as exc:
        raise RuntimeError(f"SonarCloud API error: {exc}") from exc


def _fetch_all_measures(client: Any, project_key: str, keys: list[str]) -> list[dict[str, Any]]:
    measures: list[dict[str, Any]] = []
    for i in range(0, len(keys), 50):
        measures.extend(_fetch_chunk_measures(client, project_key, keys[i : i + 50]))
    return measures


def _map_metrics(measures: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {KEY_MAP.get(m["metric"], m["metric"]): {"global": _coerce_value(m.get("value"))} for m in measures}


def _has_best_value(measure: dict[str, Any] | None) -> bool:
    res = False
    if isinstance(measure, dict):
        res = "bestValue" in measure
    return res


def _add_best_value(detail: dict[str, Any], measure: dict[str, Any] | None) -> None:
    if _has_best_value(measure):
        detail["bestValue"] = measure["bestValue"]  # type: ignore


def _build_detail(m: dict[str, Any], mmap: dict[str, Any]) -> dict[str, Any]:
    key = m["key"]
    measure = mmap.get(key)
    detail = dict(m)
    detail["value"] = _coerce_value(measure.get("value")) if measure else None
    _add_best_value(detail, measure)
    return detail


def _select_key(k1: str | None, k2: str | None) -> str | None:
    res = k2
    if k1 is not None:
        res = k1
    return res


def _get_str(val: str | None) -> str:
    res = ""
    if val is not None:
        res = val
    return res


def _has_key(m: dict[str, Any]) -> bool:
    return "key" in m


def _get_key(m: dict[str, Any]) -> str:
    return str(m["key"])


def _build_measures_map(measures: list[dict[str, Any]]) -> dict[str, Any]:
    valid = filter(lambda m: "metric" in m, measures)
    return {m["metric"]: m for m in valid}


class SonarCloudAdapter(QualityGateway):
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

    def get_metrics(self, project_key: str | None = None) -> dict[str, dict[str, Any]]:
        """Fetch project measures and return them in Domain format.

        Returns:
            Dict mapping Domain metric names to scope-value dicts,
            e.g. ``{"coverage": {"global": 95.0}}``.

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        key = _select_key(project_key, self.config.project_key)
        _validate_project_key(key)
        measures = _fetch_chunk_measures(self.client, _get_str(key), METRIC_KEYS)
        return _map_metrics(measures)

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
        _validate_project_key(self.config.project_key)
        res = _fetch_issues(self.client, _get_str(self.config.project_key))
        issues = res.get("issues", []) if isinstance(res, dict) else list(res)
        filtered = list(filter(lambda i: i.get("status") not in CLOSED_STATUSES, issues))
        return issues if include_closed else filtered

    def get_all_available_metrics(self) -> list[dict[str, Any]]:
        """Fetch all available metric definitions from SonarCloud.

        Returns:
            List of metric dictionaries containing keys like 'key', 'name', 'type', etc.

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        return _parse_metrics(_fetch_metrics(self.client))

    def get_detailed_component_measures(self, metric_keys: list[str]) -> list[dict[str, Any]]:
        """Fetch detailed component measures for the given metric keys.

        Args:
            metric_keys: A list of metric keys to query.

        Returns:
            A list of measure dictionaries (each containing 'metric', 'value', etc.).

        Raises:
            RuntimeError: If the SonarCloud API call fails.
        """
        _validate_project_key(self.config.project_key)
        key = _get_str(self.config.project_key)
        return _fetch_all_measures(self.client, key, metric_keys) if metric_keys else []

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
        keys = list(map(_get_key, filter(_has_key, metrics)))
        measures = self.get_detailed_component_measures(keys)
        mmap = _build_measures_map(measures)
        return list(map(lambda m: _build_detail(m, mmap), filter(_has_key, metrics)))

    def get_quality_metrics(self, project_key: str) -> dict[str, Any]:
        """Fetch quality metrics for a project."""
        metrics = self.get_metrics(project_key)
        return {k: v.get("global") for k, v in metrics.items()}

    def passes_gate(self, project_key: str) -> bool:
        """Check if the project passes the quality gate."""
        metrics = self.get_quality_metrics(project_key)
        return metrics.get("alert_status") == "OK"
