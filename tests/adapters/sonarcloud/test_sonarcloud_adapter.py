"""Unit tests for SonarCloudAdapter.

Traceable to: FEA-015, FR-015, TC-SONAR-ADAPTER
All SonarCloud API calls are mocked via unittest.mock — no network required.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_workflow.domain.value_objects import SonarCloudConfig
from agentic_workflow.frameworks.sonarcloud.sonar_adapter import (
    CLOSED_STATUSES,
    KEY_MAP,
    METRIC_KEYS,
    SonarCloudAdapter,
    _coerce_value,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_config(
    token: str = "test-token",
    project_key: str = "org_project",
    organization: str = "org",
) -> SonarCloudConfig:
    """Build a minimal SonarCloudConfig for tests."""
    return SonarCloudConfig(
        token=token,
        project_key=project_key,
        organization=organization,
    )


def _make_adapter(
    config: SonarCloudConfig | None = None,
) -> tuple[SonarCloudAdapter, MagicMock]:
    """Return adapter + mock client, skipping real HTTP initialisation."""
    cfg = config or _make_config()
    with patch("agentic_workflow.frameworks.sonarcloud.sonar_adapter.SonarCloudClient") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        adapter = SonarCloudAdapter(cfg)
    return adapter, mock_client


# ── _coerce_value ──────────────────────────────────────────────────────────────


class TestCoerceValue:
    """Unit tests for the _coerce_value helper."""

    def test_integer_string_becomes_float(self) -> None:
        """'100' → 100.0."""
        assert _coerce_value("100") == 100.0

    def test_decimal_string_becomes_float(self) -> None:
        """'3.14' → 3.14."""
        assert _coerce_value("3.14") == pytest.approx(3.14)

    def test_non_numeric_string_unchanged(self) -> None:
        """'OK' stays 'OK'."""
        assert _coerce_value("OK") == "OK"

    def test_none_returns_none(self) -> None:
        """None → None."""
        assert _coerce_value(None) is None

    def test_negative_string_becomes_float(self) -> None:
        """'-5' → -5.0."""
        assert _coerce_value("-5") == -5.0


# ── Module-level constants ─────────────────────────────────────────────────────


class TestModuleConstants:
    """Sanity checks on exported constants."""

    def test_metric_keys_non_empty(self) -> None:
        """METRIC_KEYS must have at least the core quality metrics."""
        assert "coverage" in METRIC_KEYS
        assert "complexity" in METRIC_KEYS
        assert "alert_status" in METRIC_KEYS

    def test_key_map_maps_complexity(self) -> None:
        """Complexity → cyclomatic_complexity."""
        assert KEY_MAP["complexity"] == "cyclomatic_complexity"

    def test_key_map_maps_duplication(self) -> None:
        """duplicated_lines_density → duplication."""
        assert KEY_MAP["duplicated_lines_density"] == "duplication"

    def test_closed_statuses_contains_closed(self) -> None:
        """CLOSED_STATUSES must include both closed states."""
        assert "CLOSED" in CLOSED_STATUSES
        assert "RESOLVED" in CLOSED_STATUSES


# ── SonarCloudAdapter.__init__ ─────────────────────────────────────────────────


class TestAdapterInit:
    """Tests for adapter initialisation."""

    def test_client_created_with_correct_url(self) -> None:
        """SonarCloudClient must be initialised with sonarcloud.io URL."""
        cfg = _make_config()
        with patch("agentic_workflow.frameworks.sonarcloud.sonar_adapter.SonarCloudClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            SonarCloudAdapter(cfg)
            mock_cls.assert_called_once_with(
                sonarqube_url="https://sonarcloud.io",
                token="test-token",
            )

    def test_config_stored(self) -> None:
        """Adapter must store the config reference."""
        cfg = _make_config()
        adapter, _ = _make_adapter(cfg)
        assert adapter.config is cfg


# ── get_metrics ────────────────────────────────────────────────────────────────


class TestGetMetrics:
    """Tests for SonarCloudAdapter.get_metrics."""

    def _stub_measures(self, mock_client: MagicMock, measures: list[dict[str, Any]]) -> None:
        """Wire mock client to return given measures list."""
        rv = {"component": {"measures": measures}}
        mock_client.measures.get_component_with_specified_measures.return_value = rv

    def test_returns_mapped_domain_keys(self) -> None:
        """API key 'complexity' must appear as 'cyclomatic_complexity'."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(mock_client, [{"metric": "complexity", "value": "42"}])
        result = adapter.get_metrics()
        assert "cyclomatic_complexity" in result
        assert result["cyclomatic_complexity"]["global"] == 42.0

    def test_unmapped_key_kept_as_is(self) -> None:
        """API key 'alert_status' has no mapping → kept verbatim."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(mock_client, [{"metric": "alert_status", "value": "OK"}])
        result = adapter.get_metrics()
        assert result["alert_status"]["global"] == "OK"

    def test_null_value_becomes_none(self) -> None:
        """Missing 'value' field → None stored in result."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(mock_client, [{"metric": "coverage"}])
        result = adapter.get_metrics()
        assert result["coverage"]["global"] is None

    def test_empty_measures_returns_empty_dict(self) -> None:
        """No measures → empty dict returned."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(mock_client, [])
        assert adapter.get_metrics() == {}

    def test_api_exception_raises_runtime_error(self) -> None:
        """Network/API failures must be wrapped in RuntimeError."""
        adapter, mock_client = _make_adapter()
        mock_client.measures.get_component_with_specified_measures.side_effect = Exception("connection refused")
        with pytest.raises(RuntimeError, match="SonarCloud API error"):
            adapter.get_metrics()

    def test_correct_metric_keys_sent(self) -> None:
        """All METRIC_KEYS must be sent in the API call."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(mock_client, [])
        adapter.get_metrics()
        stub = mock_client.measures.get_component_with_specified_measures
        sent_keys = stub.call_args[1]["metricKeys"].split(",")
        for key in METRIC_KEYS:
            assert key in sent_keys

    def test_correct_project_key_sent(self) -> None:
        """Configured project_key must be forwarded to the API."""
        adapter, mock_client = _make_adapter(_make_config(project_key="my_proj"))
        self._stub_measures(mock_client, [])
        adapter.get_metrics()
        stub = mock_client.measures.get_component_with_specified_measures
        assert stub.call_args[1]["component"] == "my_proj"

    def test_multiple_measures_all_present(self) -> None:
        """Multiple measures returned by API all appear in result."""
        adapter, mock_client = _make_adapter()
        self._stub_measures(
            mock_client,
            [
                {"metric": "coverage", "value": "95.0"},
                {"metric": "bugs", "value": "0"},
            ],
        )
        result = adapter.get_metrics()
        assert "coverage" in result
        assert "blocker_critical_smells" in result  # 'bugs' is mapped


# ── get_issues ─────────────────────────────────────────────────────────────────


class TestGetIssues:
    """Tests for SonarCloudAdapter.get_issues."""

    def _stub_issues(self, mock_client: MagicMock, issues: list[dict[str, Any]]) -> None:
        """Wire mock client to return given issues."""
        mock_client.issues.search_issues.return_value = {"issues": issues}

    def test_open_issues_returned_by_default(self) -> None:
        """OPEN issues must be included in default call."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(mock_client, [{"status": "OPEN", "message": "something"}])
        result = adapter.get_issues()
        assert len(result) == 1

    def test_closed_issues_excluded_by_default(self) -> None:
        """CLOSED issues must be filtered out in default call."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(mock_client, [{"status": "CLOSED", "message": "old"}])
        result = adapter.get_issues()
        assert result == []

    def test_resolved_issues_excluded_by_default(self) -> None:
        """RESOLVED issues must be filtered out in default call."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(mock_client, [{"status": "RESOLVED", "message": "fixed"}])
        result = adapter.get_issues()
        assert result == []

    def test_include_closed_returns_all(self) -> None:
        """include_closed=True returns CLOSED issues too."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(
            mock_client,
            [
                {"status": "OPEN", "message": "open"},
                {"status": "CLOSED", "message": "closed"},
            ],
        )
        result = adapter.get_issues(include_closed=True)
        assert len(result) == 2

    def test_empty_response_returns_empty_list(self) -> None:
        """API returning no issues → empty list."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(mock_client, [])
        assert adapter.get_issues() == []

    def test_api_exception_raises_runtime_error(self) -> None:
        """Network/API failures must be wrapped in RuntimeError."""
        adapter, mock_client = _make_adapter()
        mock_client.issues.search_issues.side_effect = Exception("timeout")
        with pytest.raises(RuntimeError, match="SonarCloud API error"):
            adapter.get_issues()

    def test_correct_project_key_sent(self) -> None:
        """Configured project_key must be forwarded to issues search."""
        adapter, mock_client = _make_adapter(_make_config(project_key="proj_x"))
        self._stub_issues(mock_client, [])
        adapter.get_issues()
        call_kwargs = mock_client.issues.search_issues.call_args[1]
        assert call_kwargs["componentKeys"] == "proj_x"

    def test_confirmed_issues_included_by_default(self) -> None:
        """CONFIRMED status is open — must be returned."""
        adapter, mock_client = _make_adapter()
        self._stub_issues(mock_client, [{"status": "CONFIRMED", "message": "confirmed"}])
        result = adapter.get_issues()
        assert len(result) == 1

    def test_generator_response_handled(self) -> None:
        """If API returns a generator instead of dict, it is consumed correctly."""
        adapter, mock_client = _make_adapter()
        mock_client.issues.search_issues.return_value = iter(
            [
                {"status": "OPEN", "message": "gen1"},
                {"status": "CLOSED", "message": "gen2"},
            ],
        )
        result = adapter.get_issues()
        assert len(result) == 1
        assert result[0]["message"] == "gen1"


# ── get_all_available_metrics ──────────────────────────────────────────────────


class TestGetAllAvailableMetrics:
    """Tests for SonarCloudAdapter.get_all_available_metrics."""

    def test_returns_metrics_list(self) -> None:
        """search_metrics return values must be converted to a list."""
        adapter, mock_client = _make_adapter()
        mock_client.metrics.search_metrics.return_value = [
            {"key": "coverage", "name": "Coverage"},
            {"key": "complexity", "name": "Complexity"},
        ]
        result = adapter.get_all_available_metrics()
        assert result == [
            {"key": "coverage", "name": "Coverage"},
            {"key": "complexity", "name": "Complexity"},
        ]

    def test_api_exception_raises_runtime_error(self) -> None:
        """Network/API failures must be wrapped in RuntimeError."""
        adapter, mock_client = _make_adapter()
        mock_client.metrics.search_metrics.side_effect = Exception("HTTP 500")
        with pytest.raises(RuntimeError, match="SonarCloud API error"):
            adapter.get_all_available_metrics()


# ── get_detailed_component_measures ───────────────────────────────────────────


class TestGetDetailedComponentMeasures:
    """Tests for SonarCloudAdapter.get_detailed_component_measures."""

    def test_empty_keys_returns_empty_list(self) -> None:
        """Passing an empty list of keys immediately returns empty list."""
        adapter, mock_client = _make_adapter()
        assert adapter.get_detailed_component_measures([]) == []
        mock_client.measures.get_component_with_specified_measures.assert_not_called()

    def test_missing_project_key_raises_runtime_error(self) -> None:
        """If project_key is missing in config, raise RuntimeError."""
        adapter, _ = _make_adapter(_make_config(project_key=""))
        with pytest.raises(RuntimeError, match="project_key configuration is missing"):
            adapter.get_detailed_component_measures(["coverage"])

    def test_fetches_measures_in_chunks(self) -> None:
        """Keys are chunked into groups of 50 to prevent URL length issues."""
        adapter, mock_client = _make_adapter()
        mock_client.measures.get_component_with_specified_measures.side_effect = [
            {"component": {"measures": [{"metric": f"m{k}", "value": "1.0"} for k in range(50)]}},
            {"component": {"measures": [{"metric": f"m{k}", "value": "1.0"} for k in range(50, 100)]}},
            {"component": {"measures": [{"metric": f"m{k}", "value": "1.0"} for k in range(100, 110)]}},
        ]

        keys = [f"m{k}" for k in range(110)]
        result = adapter.get_detailed_component_measures(keys)

        assert len(result) == 110
        assert mock_client.measures.get_component_with_specified_measures.call_count == 3

    def test_api_exception_raises_runtime_error(self) -> None:
        """Network/API failures inside a chunk must be wrapped in RuntimeError."""
        adapter, mock_client = _make_adapter()
        mock_client.measures.get_component_with_specified_measures.side_effect = Exception("Timeout")
        with pytest.raises(RuntimeError, match="SonarCloud API error"):
            adapter.get_detailed_component_measures(["coverage"])


# ── get_all_metrics_with_values ───────────────────────────────────────────────


class TestGetAllMetricsWithValues:
    """Tests for SonarCloudAdapter.get_all_metrics_with_values."""

    def test_merges_metrics_and_measures(self) -> None:
        """Definitions and measures are combined and coerced properly."""
        adapter, mock_client = _make_adapter()
        mock_client.metrics.search_metrics.return_value = [
            {"key": "coverage", "name": "Coverage", "type": "FLOAT"},
            {"key": "complexity", "name": "Complexity", "type": "INT"},
            {"key": "alert_status", "name": "Gate Status", "type": "DATA"},
        ]
        mock_client.measures.get_component_with_specified_measures.return_value = {
            "component": {
                "measures": [
                    {"metric": "coverage", "value": "92.5"},
                    {"metric": "complexity", "value": "10", "bestValue": True},
                    {"metric": "alert_status", "value": "OK"},
                ]
            }
        }

        result = adapter.get_all_metrics_with_values()
        assert len(result) == 3

        # Match keys
        cov = next(r for r in result if r["key"] == "coverage")
        comp = next(r for r in result if r["key"] == "complexity")
        stat = next(r for r in result if r["key"] == "alert_status")

        assert cov["value"] == 92.5
        assert comp["value"] == 10.0
        assert comp["bestValue"] is True
        assert stat["value"] == "OK"

    def test_handling_metric_without_key(self) -> None:
        """Metric dictionary lacking 'key' is ignored."""
        adapter, mock_client = _make_adapter()
        mock_client.metrics.search_metrics.return_value = [
            {"name": "No Key Metric"},
            {"key": "coverage", "name": "Coverage"},
        ]
        mock_client.measures.get_component_with_specified_measures.return_value = {
            "component": {"measures": [{"metric": "coverage", "value": "100"}]}
        }
        result = adapter.get_all_metrics_with_values()
        assert len(result) == 1
        assert result[0]["key"] == "coverage"

    def test_handling_no_measure_value(self) -> None:
        """Metric key has no matching measure value -> value is None."""
        adapter, mock_client = _make_adapter()
        mock_client.metrics.search_metrics.return_value = [
            {"key": "coverage", "name": "Coverage"},
        ]
        mock_client.measures.get_component_with_specified_measures.return_value = {"component": {"measures": []}}
        result = adapter.get_all_metrics_with_values()
        assert len(result) == 1
        assert result[0]["key"] == "coverage"
        assert result[0]["value"] is None
