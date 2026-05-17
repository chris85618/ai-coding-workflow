#!/usr/bin/env python3
"""Script to fetch and display open issues from SonarCloud/SonarQube.

Fetches open issues and formats them in a clear Markdown table.
"""

import sys
from pathlib import Path

# Insert src directory to path to resolve local imports cleanly
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_workflow.domain.value_objects.sonarcloud_config import (
    SonarCloudConfig as DomainSonarCloudConfig,
)
from agentic_workflow.frameworks.config.workflow_config import WorkflowConfigLoader
from agentic_workflow.frameworks.sonarcloud.sonar_adapter import SonarCloudAdapter


def main() -> None:
    """Load config, retrieve issues, and display them in Markdown."""
    print("=== SonarQube/SonarCloud Open Issues Puller ===")

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
    print("Connecting to SonarCloud and retrieving open issues...")

    # Convert frameworks config to domain config for compatibility
    domain_sonar_config = DomainSonarCloudConfig(
        token=sonar_config.token,
        project_key=sonar_config.project_key,
        organization=sonar_config.organization,
        auto_convert_to_debt=sonar_config.feedback.auto_convert_to_debt,
        default_debt_priority=sonar_config.feedback.default_debt_priority,
        on_missing_config=sonar_config.on_missing_config,
    )

    # 3. Initialize Adapter & Retrieve Issues
    adapter = SonarCloudAdapter(domain_sonar_config)

    try:
        issues = adapter.get_issues(include_closed=False)
    except Exception as exc:
        print(f"\nError pulling issues from SonarCloud API: {exc}")
        print("Please verify your API token and network connection.")
        sys.exit(1)

    # 4. Display Results
    print(f"\nFound {len(issues)} open issues.\n")

    if not issues:
        print("🎉 No open issues found!")
        sys.exit(0)

    print("| # | Severity | Type | Key | Component | Message | Status |")
    print("|---|---|---|---|---|---|---|")
    for idx, issue in enumerate(issues, 1):
        severity = issue.get("severity", "N/A")
        issue_type = issue.get("type", "N/A")
        key = issue.get("key", "N/A")
        component = issue.get("component", "N/A").split(":")[-1]
        message = issue.get("message", "N/A").replace("\n", " ")
        status = issue.get("status", "N/A")
        print(f"| {idx} | **{severity}** | {issue_type} | `{key}` | `{component}` | {message} | {status} |")


if __name__ == "__main__":
    main()
