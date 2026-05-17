#!/usr/bin/env python3
"""Script to fetch all SonarCloud/SonarQube metrics with detailed values for the project.

Fetches metric definitions and fuses them with their current project measures,
formatting them into a clear Markdown table.
"""

import sys
from pathlib import Path
from typing import Any

# Insert src directory to path to resolve local imports cleanly
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_workflow.domain.value_objects.sonarcloud_config import (
    SonarCloudConfig as DomainSonarCloudConfig,
)
from agentic_workflow.frameworks.config.workflow_config import WorkflowConfigLoader
from agentic_workflow.frameworks.sonarcloud.sonar_adapter import SonarCloudAdapter


def main() -> None:
    """Load config, retrieve metrics and values, and display them in Markdown."""
    print("=== SonarQube/SonarCloud Detailed Metrics Puller ===")

    # 1. Load configuration
    config_path = "config.yaml"
    if not Path(config_path).exists():
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)

    try:
        config = WorkflowConfigLoader.load(config_path)
    except Exception as exc:
        print(f"Error loading configuration: {exc}")
        sys.exit(1)

    sonar_config = config.sonarcloud

    # 2. Validate configuration
    if not sonar_config.is_valid:
        print("\n[!] SonarCloud configuration is incomplete.")
        print(f"Missing variables: {', '.join(sonar_config.missing_vars)}")
        print("Please check your .env file or configuration parameters.")
        sys.exit(1)

    print(f"Configured Project: {sonar_config.project_key}")
    print(f"Organization: {sonar_config.organization}")
    print("Connecting to SonarCloud and retrieving metrics detail...")

    # Convert frameworks config to domain config for compatibility
    domain_sonar_config = DomainSonarCloudConfig(
        token=sonar_config.token,
        project_key=sonar_config.project_key,
        organization=sonar_config.organization,
        auto_convert_to_debt=sonar_config.feedback.auto_convert_to_debt,
        default_debt_priority=sonar_config.feedback.default_debt_priority,
        on_missing_config=sonar_config.on_missing_config,
    )

    # 3. Initialize Adapter & Retrieve Metrics
    adapter = SonarCloudAdapter(domain_sonar_config)

    try:
        metrics = adapter.get_all_metrics_with_values()
    except Exception as exc:
        print(f"\nError pulling metrics from SonarCloud API: {exc}")
        print("Please verify your API token and network connection.")
        sys.exit(1)

    if not metrics:
        print("\nNo metrics were returned. Please check if the project key is correct and contains data.")
        sys.exit(0)

    # 4. Print Summary table
    print(f"\nRetrieved {len(metrics)} available metrics. Formatting details...\n")

    # Group metrics by Domain for readability
    by_domain: dict[str, list[dict[str, Any]]] = {}
    for m in metrics:
        domain = m.get("domain", "Other")
        by_domain.setdefault(domain, []).append(m)

    for domain in sorted(by_domain.keys()):
        print(f"### Domain: {domain}")
        print("| Metric Key | Name | Type | Current Value | Description |")
        print("|---|---|---|---|---|")
        for m in sorted(by_domain[domain], key=lambda x: str(x.get("key", ""))):
            key = m.get("key", "N/A")
            name = m.get("name", "N/A")
            m_type = m.get("type", "N/A")
            val = m.get("value")
            val_str = str(val) if val is not None else "*No Value*"
            desc = str(m.get("description", "")).replace("\n", " ")
            print(f"| `{key}` | {name} | {m_type} | **{val_str}** | {desc} |")
        print()


if __name__ == "__main__":
    main()
